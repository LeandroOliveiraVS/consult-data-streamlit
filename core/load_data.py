import sqlalchemy as sa
import pandas as pd
import streamlit as st

from core.connection import conectar_banco

engine = conectar_banco()

@st.cache_data(ttl=600)
def carregar_tabela(_engine, table):
        
    queryUsers = f"SELECT * FROM {table};"
   
    try:
        st.spinner("🔄 Carregando dados do banco...")
        with _engine.connect() as connection:
            df = pd.read_sql(sa.text(queryUsers), connection)

    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela: {e}")
        st.info(f"Verifique se o nome da tabela ('users') está correto no script.")
        st.stop()

    return df