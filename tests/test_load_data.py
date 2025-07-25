import pandas as pd
import sqlalchemy as sa
import pytest
from unittest.mock import MagicMock

from core.load_data import carregar_tabela


def test_carregar_tabela_sucesso(mocker):
    # 1. Prepara os dados de teste
    name_table_test = "users"
    dados_esperados = pd.DataFrame({"id": [1], "username": ["testuser"]})

    # 2. Simular o engine e a sua conexão
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    # 3. Simula o pd.read_sql para retornar os nossos dados de teste
    mock_read_sql = mocker.patch("pandas.read_sql", return_value=dados_esperados)

    # 4. Simula os componentes do Streamlit
    mocker.patch("streamlit.spinner")

    # 5. Executa a função
    df_resultado = carregar_tabela(mock_engine, name_table_test)

    # 6. Verificar os resultados

    # Verifica se a consulta SQL foi construída corretamente
    query_esperada = f"SELECT * FROM {name_table_test};"

    # pd.read_sql recebe um objeto SQLAlchemy TextClause, então verificamos o seu conteúdo
    chamada_real = mock_read_sql.call_args[0][0]
    assert str(chamada_real) == query_esperada

    # Verifica se o DataFrame retornado é o que esperávamos
    pd.testing.assert_frame_equal(df_resultado, dados_esperados)

    # Limpa o cache para o próximo teste
    carregar_tabela.clear()


def test_carregar_tabela_falha_na_conexao(mocker):
    """
    Testa o caminho de falha: ocorre um erro ao tentar ler do banco de dados.
    """
    # 1. Prepara os dados de teste
    nome_tabela_teste = "tabela_inexistente"

    # 2. Simula o 'engine' para que a conexão levante um erro
    mock_engine = MagicMock()
    erro_db = sa.exc.ProgrammingError("Tabela não encontrada", "orig", "params")
    mock_engine.connect.side_effect = erro_db

    # 3. Simula os componentes de erro do Streamlit
    mock_error = mocker.patch("streamlit.error")
    mock_info = mocker.patch("streamlit.info")

    # 4. Executa a função e verifica se ela chama st.stop()
    with pytest.raises(SystemExit):
        carregar_tabela(mock_engine, nome_tabela_teste)

    # 5. Verifica se as mensagens de erro corretas foram exibidas
    assert mock_error.called
    assert mock_info.called

    # Limpa o cache para o próximo teste
    carregar_tabela.clear()
