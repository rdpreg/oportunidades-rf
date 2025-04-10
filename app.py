import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Mensagem de Destaques", layout="centered")

st.title("📈 Gerador de Destaques - Crédito Bancário")
st.write("Faça o upload da planilha diária e copie a mensagem formatada para WhatsApp.")

uploaded_file = st.file_uploader("📎 Envie o arquivo .xlsm", type=["xlsm"])

if uploaded_file:
    try:
        bancarios = pd.read_excel(uploaded_file, sheet_name="Crédito bancario")
        bancarios.columns = bancarios.columns.str.strip()  # Remove espaços em branco dos nomes das colunas

        def formatar_ativo(row):
            nome = row['Emissor']
            venc = row['Vencimento'].strftime('%d/%m/%Y') if not pd.isnull(row['Vencimento']) else '---'
            taxa = row['Tx. Portal']
            minimo = f"R$ {float(row['Aplicação mínima']):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            info = f"🏦*{nome}*\nVencimento: {venc}\nTaxa: {taxa}\nR$  mínimo: {minimo}\n"
            return info

        def separar_por_indexador(df, tipo):
            return df[df['Indexador'].str.upper().str.contains(tipo, na=False)]

        hoje = datetime.today().strftime('%A %d/%m').capitalize()
        mensagem = f"‼️ *DESTAQUE CRÉDITO BANCÁRIO - ISENTOS* ‼️\n\n🚨*TAXAS DE HOJE ({hoje})*\n\n📍*PÓS-FIXADOS*\n"

        for _, row in separar_por_indexador(bancarios, 'CDI').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        mensagem += "\n📍*PRÉ-FIXADOS*\n"
        for _, row in separar_por_indexador(bancarios, 'PRÉ').iterrows():
            mensagem += formatar_ativo(row) + '\n'

        st.subheader("📋 Mensagem Gerada")
        st.text_area("Copie e cole a mensagem abaixo no WhatsApp:", value=mensagem, height=600)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
