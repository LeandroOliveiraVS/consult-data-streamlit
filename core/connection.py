import sqlalchemy as sa
import streamlit as st


@st.cache_resource
def conectar_banco():

    st.spinner("🔌 Conectando ao banco de dados MySQL...")

    try:

        db_user = st.secrets["mysql"]["user"]
        db_password = st.secrets["mysql"]["password"]
        db_host = st.secrets["mysql"]["host"]
        db_port = st.secrets["mysql"]["port"]
        db_name = st.secrets["mysql"]["db_name"]

        connection_string = (
            f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        engine = sa.create_engine(connection_string)

        # Testa a conexão para garantir que tudo está funcionando
        with engine.connect() as connection:
            pass  # A conexão bem-sucedida não faz nada, falha gera exceção

        # st.sidebar.success("Conexão com o MySQL estabelecida com sucesso!")
        return engine

    except Exception as e:

        st.error(f"Erro ao conectar ao MySQL: {e}")
        st.info(
            "Verifique se o arquivo .streamlit/secrets.toml está configurado corretamente."
        )
        st.stop()
