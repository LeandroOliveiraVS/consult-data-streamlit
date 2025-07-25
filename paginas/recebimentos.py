import streamlit as st
import pandas as pd
import sqlalchemy as sa
import datetime

from core.connection import conectar_banco

def recebimentos_page():
    # -- Configuração da Página --
    st.set_page_config(
        page_title="consulta de recebimentos",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # -- Conexão e Carregamento dos dados --
    engine = conectar_banco()

    # O cache de dados continua aqui, pois a consulta pode mudar.
    @st.cache_data(ttl=600)
    def carregar_dados(_engine):
        """Executa uma consulta no banco de dados e reotrna um DataFrame. """
        query = "SELECT * FROM recebimentos"

        try:
            st.spinner("🔄 Carregando dados do banco...")
            with _engine.connect() as connection:
                df = pd.read_sql(sa.text(query), connection)
                # ===================================================================
                coluna_data = 'registro'
                if coluna_data in df.columns:
                    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
                else:
                    st.warning(f"Atenção: A coluna de data '{coluna_data}' não foi encontrada na tabela.")
                # ============================== CONVERSÕES =====================================
                coluna_hora = 'Hora_recebimento'
                if coluna_hora in df.columns:
                    
                    def converter_para_hora(valor):
                        """Converte um valor (string ou timedelta) para um objeto time."""
                        if pd.isnull(valor):
                            return None
                        try:
                            # Converte para string e pega a última parte (ex: "14:30:00")
                            # Funciona tanto para "14:30:00" como para "0 days 14:30:00"
                            hora_str = str(valor).split()[-1]
                            # Converte a string da hora para um objeto time
                            return datetime.datetime.strptime(hora_str, '%H:%M:%S').time()
                        except (ValueError, TypeError):
                            # Retorna None se a conversão falhar
                            return None
                        
                    # Aplica a função de conversão segura à coluna
                    df[coluna_hora] = df[coluna_hora].apply(converter_para_hora)
                    
                    df.dropna(subset=[coluna_data], inplace=True)
                else:
                    st.warning(f"Atenção: A coluna de hora '{coluna_hora}' não foi encontrada na tabela.")
                # ===============================================================================
            return df
        except Exception as e:
            st.error(f"Erro ao carregar dados da tabela: {e}")
            st.info(f"Verifique se o nome da tabela ('recebimentos') está correto no script.")
            st.stop()

    df = carregar_dados(engine)

    # --- INTERFACE DO WEB APP ---
    st.header("📊 Dashboard de Recebimentos")
    st.markdown("Use os filtros na barra lateral para explorar os dados de recebimentos.")

    # --- BARRA LATERAL (SIDEBAR) PARA FILTROS ---
    st.sidebar.header("Filtros")

    # Adicionando um placeholder para o DataFrame filtrado
    df_filtrado = df.copy()

    # --- INÍCIO DA DEPURAÇÃO ---
    st.sidebar.write(f"Total de linhas carregadas do banco: **{len(df)}**")
    # ---------------------------

    df_filtrado = df.copy()

    coluna_data = 'registro'
    if not df.empty and coluna_data in df.columns and not df[coluna_data].isnull().all():
        data_min = df[coluna_data].min().date()
        data_max = df[coluna_data].max().date()

        data_inicio = st.sidebar.date_input(
            "Data Inicial",
            value=data_min,
            min_value=data_min,
            max_value=data_max
        )

        data_fim = st.sidebar.date_input(
            "Data Final",
            value=data_max,
            min_value=data_min,
            max_value=data_max
        )
        
        df_filtrado = df_filtrado[df_filtrado[coluna_data].dt.date.between(data_inicio, data_fim)]
        
    else:
        st.sidebar.warning(f"Não foi possível criar o filtro de data. Verifique a coluna '{coluna_data}'.")

    # --- FILTRO POR FORNECEDOR (COM OPÇÃO "TODOS") ---
    coluna_fornecedor = 'Nome_fornecedor'
    if coluna_fornecedor in df.columns:
        # Pega a lista de fornecedores únicos e ordena
        lista_fornecedores = sorted(df[coluna_fornecedor].dropna().unique())
        
        # Adiciona a opção "Todos" no início da lista
        opcoes_filtro = ["Todos os Fornecedores"] + lista_fornecedores
        
        fornecedor_selecionado = st.sidebar.selectbox(
            "Selecione um Fornecedor",
            options=opcoes_filtro
        )
        
        # Aplica o filtro apenas se um fornecedor específico for selecionado
        if fornecedor_selecionado != "Todos os Fornecedores":
            df_filtrado = df_filtrado[df_filtrado[coluna_fornecedor] == fornecedor_selecionado]
    # ---------------------------------------------------------

    # --- CONTAGEM DE LINHAS FILTRADAS ---
    num_linhas = st.sidebar.write(f"Linhas filtradas: **{len(df_filtrado)}**")

    # --- PAINEL PRINCIPAL ---
    st.markdown("---")
    st.subheader("Dados Detalhados do Período Selecionado")
    st.write(f"Exibindo **{len(df_filtrado)}** de **{len(df)}** registros totais.")

    # Exibe a tabela com os dados que foram filtrados
    st.dataframe(df_filtrado, use_container_width=True)
    # ------------------------------------

    with st.expander("Ver código-fonte do App"):
        st.code(open(__file__, 'r', encoding='utf-8').read())
