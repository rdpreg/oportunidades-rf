import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Mensagem de Destaques", layout="centered")

st.title("📈 Gerador de Destaques - Crédito Bancário")
st.write("Faça o upload da planilha diária e copie a mensagem formatada para WhatsApp.")

uploaded_file = st.file_uploader("📎 Envie o arquivo .xlsm", type=["xlsm"])

if uploaded_file:
    try:
        # Carregar planilha
        bancarios = pd.read_excel(uploaded_file, sheet_name="Crédito bancário")
        bancarios.columns = bancarios.columns.str.strip()  # remove espaços nos nomes das colunas

        # Funções auxiliares
        def isento(produto):
            return any(x in produto.upper() for x in ['LCA', 'LCI', 'LCD'])

        def nao_isento(produto):
            return 'CDB' in produto.upper()

        def separar_top_3_por_indexador(df, tipo):
            filtrado = df[df['Indexador'].str.upper().str.contains(tipo, na=False)].copy()

            # Converter taxa para número, mesmo que venha como string tipo "95,5% do CDI"
            def extrair_numero(t):
                if isinstance(t, str):
                    t = t.replace('%', '').replace(',', '.')
                    num = ''.join(c for c in t if (c.isdigit() or c == '.'))
                    try:
                        return float(num)
                    except:
                        return None
                elif isinstance(t, (int, float)):
                    return t
                return None

            filtrado['taxa_num'] = filtrado['Tx. Portal'].apply(extrair_numero)
            return filtrado.sort_values(by='taxa_num', ascending=False).head(3)



        def formatar_ativo(row):
            produto = row['Produto']
            nome = row['Emissor']
            venc = row['Vencimento'].strftime('%d/%m/%Y') if not pd.isnull(row['Vencimento']) else '---'

            # Tratar taxa
            taxa = row['Tx. Portal']
            if isinstance(taxa, (int, float)) and taxa < 1:
                taxa_formatada = f"{taxa * 100:.0f}%"
            elif isinstance(taxa, (int, float)):
                taxa_formatada = f"{taxa:.2f}%"
            else:
                taxa_formatada = str(taxa)

            # Adicionar o tipo de taxa com base no indexador
            indexador = row['Indexador'].upper() if isinstance(row['Indexador'], str) else ""

            if "CDI" in indexador:
                taxa_formatada += " do CDI"
            elif "IPCA" in indexador:
                taxa_formatada = f"IPCA + {taxa_formatada}"

            # Formatar valor mínimo
            minimo = f"R$ {float(row['Aplicação mínima']):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

            # Montar mensagem final
            info = f"🏦*{produto} {nome}*\n⏰ Vencimento: {venc}\n📈 Taxa: {taxa_formatada}\n💰mínimo: {minimo}\n"
            return info


        # Separar em isentos e não isentos
        bancarios_isentos = bancarios[bancarios['Produto'].apply(isento)]
        bancarios_nao_isentos = bancarios[bancarios['Produto'].apply(nao_isento)]

        # Traduzir o dia da semana para português
        dias_semana = {
            "Monday": "Segunda-feira",
            "Tuesday": "Terça-feira",
            "Wednesday": "Quarta-feira",
            "Thursday": "Quinta-feira",
            "Friday": "Sexta-feira",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
            }

        agora = datetime.today()
        dia_semana = dias_semana[agora.strftime('%A')]
        hoje = f"{dia_semana} {agora.strftime('%d/%m')}"

        # Montar mensagem
        #hoje = datetime.today().strftime('%A %d/%m').capitalize()
        mensagem = f"🚨*TAXAS DE HOJE ({hoje})*\n\n‼️ *DESTAQUE CRÉDITO BANCÁRIO - ISENTOS* ‼️\n\n📍*PÓS-FIXADOS*\n\n"

        for _, row in separar_top_3_por_indexador(bancarios_isentos, 'CDI').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n📍*PRÉ-FIXADOS*\n"
        for _, row in separar_top_3_por_indexador(bancarios_isentos, 'PRÉ').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n📍*IPCA+*\n"
        for _, row in separar_top_3_por_indexador(bancarios_isentos, 'IPCA').iterrows():
            mensagem += formatar_ativo(row) + '\n'


        for _, row in separar_top_3_por_indexador(bancarios_isentos, 'CDI').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n📍*PRÉ-FIXADOS*\n"
        for _, row in separar_top_3_por_indexador(bancarios_isentos, 'PRÉ').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n📍*IPCA+*\n"
        for _, row in separar_top_3_por_indexador(bancarios_isentos, 'IPCA').iterrows():
            mensagem += formatar_ativo(row) + '\n'


        # Exibir resultado
        st.subheader("📋 Mensagem Gerada")
        st.text_area("Copie e cole a mensagem abaixo no WhatsApp:", value=mensagem, height=600)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
