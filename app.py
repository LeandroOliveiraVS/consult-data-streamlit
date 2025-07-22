import streamlit as st

# Configuração da página principal
st.set_page_config(
    page_title="Pagina Principal",
    page_icon="🏠",
    layout="wide"
)

# Conteúdo da página principal
st.title("🏠 Bem-vindo ao Dashboard Principal!")

st.sidebar.success("Selecione um dashboard acima.")

st.markdown(
    """
    Este é um dashboard interativo para visualização de dados
    conectado a um banco de dados MySQL.

    **👈 Selecione um dos dashboards na barra lateral** para começar a explorar os dados.

    ### Dashboards Disponíveis:
    - **Recebimentos:** Análise detalhada da tabela de recebimentos com filtros interativos.
    - **Outra Tabela:** Um espaço reservado para futuras análises de outras tabelas.

    ---

    *Este app foi construído com Streamlit e se conecta a um banco de dados MySQL em tempo real.*
    """
)