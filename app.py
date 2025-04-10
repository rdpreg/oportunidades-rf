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
        bancarios = pd.read_excel(uploaded_file, sheet_name="Crédito bancario")
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
            info = f"🏦*{produto} {nome}*\n⏰ Vencimento: {venc}\n📈 Taxa: {taxa}\n💰mínimo: {minimo}\n"
            return info
