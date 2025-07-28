import pandas as pd
import streamlit as st

from core.connection import conectar_banco
from core.load_data import carregar_tabela


@st.cache_data(ttl=600)
def reembolsos_page():

    engine = conectar_banco()
    table = "reembolso_pedido"

    try:
        result = carregar_tabela(engine, table)
        df = pd.DataFrame(result)

    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela: {e}")
        st.info(
            f"Verifique se o nome da tabela ('recebimentos') está correto no script."
        )
        st.stop()

    st.header("Pedidos de reembolsos")
    st.markdown("---")
    # Exibe a tabela com os dados que foram filtrados
    st.dataframe(df, use_container_width=True)
