import streamlit as st
import sqlalchemy as sa
import pytest
from unittest.mock import MagicMock

from core.connection import conectar_banco


def test_conectar_banco(mocker):
    # 1. Simula o st.secrets
    mock_secrets = {
        "mysql": {
            "user": "test_user",
            "password": "test_password",
            "host": "localhost",
            "port": "3306",
            "db_name": "test_db",
        }
    }
    mocker.patch.object(st, "secrets", new=mock_secrets)

    # 2. Simula a função sa.create_engine
    mock_create_engine = mocker.patch("sqlalchemy.create_engine")

    # 3. Simula o comportamento de sucesso da conexão
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = (
        MagicMock()
    )  # Simula o 'with'
    mock_create_engine.return_value = mock_engine

    # 4. Simula a função st.sidebar.success para que não tente desenhar na tela
    mocker.patch("streamlit.sidebar.success")

    # 5. Executa a função que queremos testar
    engine_retornado = conectar_banco()

    # 6. Verifica os resultados (Asserts)

    # Verifica se a função create_engine foi chamada com a string de conexão correta
    expected_connection_string = (
        "mysql+pymysql://test_user:test_password@localhost:3306/test_db"
    )
    mock_create_engine.assert_called_once_with(expected_connection_string)

    # Verifica se a função retornou o "engine" que criámos
    assert engine_retornado is not None

    # Limpa o cache para o próximo teste
    conectar_banco.clear()


def test_conectar_banco_falha_nos_segredos(mocker):
    # Testar o caminho de falha: o arquivo de segredos está incompleto.

    # 1. Simula um st.secrets incompleto (falta a senha)
    mock_secrets = {
        "mysql": {
            "user": "test_user",
            "host": "localhost",
            "port": "3306",
            "db_name": "test_db",
        }
    }
    mocker.patch.object(st, "secrets", new=mock_secrets)

    # 2. Simula as funções de erro do Streamlit
    mock_error = mocker.patch("streamlit.error")
    mock_info = mocker.patch("streamlit.info")

    # 3. Executa a função e verifica se ela chama st.stop()
    # st.stop() levanta uma exceção SystemExit, então usamos pytest.raises para capturá-la.
    with pytest.raises(SystemExit):
        conectar_banco()

    # 4. Verifica se as mensagens de erro corretas foram exibidas
    assert mock_error.called
    assert mock_info.called
    # Limpa o cache para o próximo teste
    conectar_banco.clear()
