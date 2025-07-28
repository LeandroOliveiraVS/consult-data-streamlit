import pandas as pd
import sqlalchemy as sa
import streamlit as st


@st.cache_data(ttl=600)
def carregar_tabela(_engine, table):

    queryUsers = f"SELECT * FROM {table};"

    try:
        with st.spinner("🔄 Carregando dados do banco..."):
            with _engine.connect() as connection:
                df = pd.read_sql(sa.text(queryUsers), connection)

        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela: {e}")
        st.info("Verifique se o nome da tabela ('users') está correto no script.")
        st.stop()

