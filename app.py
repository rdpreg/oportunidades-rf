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

        def separar_por_indexador(df, tipo):
            return df[df['Indexador'].str.upper().str.contains(tipo, na=False)]

        def formatar_ativo(row):
            produto = row['Produto']
            nome = row['Emissor']
            venc = row['Vencimento'].strftime('%d/%m/%Y') if not pd.isnull(row['Vencimento']) else '---'
            taxa = row['Tx. Portal']
            minimo = f"R$ {float(row['Aplicação mínima']):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            info = f"🏦**{produto} {nome}**\n⏰ Vencimento: {venc}\n📈 Taxa: {taxa}\n💰mínimo: {minimo}\n"
            return info

        # Separar em isentos e não isentos
        bancarios_isentos = bancarios[bancarios['Produto'].apply(isento)]
        bancarios_nao_isentos = bancarios[bancarios['Produto'].apply(nao_isento)]

        # Montar mensagem
        hoje = datetime.today().strftime('%A %d/%m').capitalize()
        mensagem = f"‼️ *DESTAQUE CRÉDITO BANCÁRIO - ISENTOS* ‼️\n\n🚨*TAXAS DE HOJE ({hoje})*\n\n📍*PÓS-FIXADOS*\n"

        for _, row in separar_por_indexador(bancarios_isentos, 'CDI').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n📍*PRÉ-FIXADOS*\n"
        for _, row in separar_por_indexador(bancarios_isentos, 'PRÉ').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n‼️ *DESTAQUE CRÉDITO BANCÁRIO - NÃO ISENTOS* ‼️\n\n📍*PÓS-FIXADOS*\n"
        for _, row in separar_por_indexador(bancarios_nao_isentos, 'CDI').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n📍*PRÉ-FIXADOS*\n"
        for _, row in separar_por_indexador(bancarios_nao_isentos, 'PRÉ').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        # Exibir resultado
        st.subheader("📋 Mensagem Gerada")
        st.text_area("Copie e cole a mensagem abaixo no WhatsApp:", value=mensagem, height=600)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
