import streamlit as st
import sqlalchemy as sa
from streamlit_oauth import OAuth2Component
import os
import requests

from core.connection import conectar_banco
from paginas.recebimentos import recebimentos_page
from paginas.admin_management import admin_management_page

# Configuração da página principal
st.set_page_config(
    page_title="Dashboard Corporativo",
    page_icon="🔐",
    layout="wide"
)

# --- CONFIGURAÇÃO DO GOOGLE OAUTH ---
# Carrega as credenciais do arquivo secrets.toml
try:
    CLIENT_ID = st.secrets["google_oauth"]["client_id"]
    CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
    REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
except KeyError:
    st.error("As credenciais do Google OAuth não foram encontradas em secrets.toml. Por favor, siga o guia de configuração.")
    st.stop()

# Define os endpoints do Google
AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
REVOKE_URL = 'https://oauth2.googleapis.com/revoke'

# Cria o componente de autenticação
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint=AUTHORIZE_URL,
    token_endpoint=TOKEN_URL,
    refresh_token_endpoint=None,
    revoke_token_endpoint=REVOKE_URL,
)

# --- CONTROLE PRINCIPAL DO APP ---

# Verifica se o usuário já está logado
if 'user_info' not in st.session_state:
    # Se não, verifica se acabámos de receber um token do Google
    if 'token' not in st.session_state:
        # Se não houver token, mostra a página de boas-vindas e o botão de login
        st.title("Bem-vindo ao Dashboard Corporativo")
        st.write("Por favor, faça o login com a sua conta Google para continuar.")

        result = oauth2.authorize_button(
            name="Entrar com o Google",
            icon="https://www.google.com.tw/favicon.ico",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
        )
        # Se o login for bem-sucedido, o 'result' conterá o token
        if result and "token" in result:
            st.session_state.token = result.get('token')
            st.rerun()

    else: 
        # Se temos o token, mas não as informações, vamos busca-las.
        token = st.session_state['token']
        access_token = token.get('access_token')
            
        # Faz a chamada à API do Google para obter as informações do perfil
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)

        if response.status_code == 200:
            # Se a chamada for bem-sucedida, guarda as informações na sessão
            st.session_state.user_info = response.json()
            st.rerun()
        else:
            st.error("Não foi possível obter as informações do usuário do Google.")
            st.write(response.text) # Mostra o erro da API para depuração
            del st.session_state['token'] # Limpa o token inválido

else:
     # Se já temos as informações do usuário, o login está completo
    user_info = st.session_state.user_info

    # Extrai o nome e o email do dicionário 'user_info' que vem do Google
    user_name = user_info.get('name', 'Usuário')
    user_email = user_info.get('email', '')

    st.sidebar.title(f"Bem-vindo, {user_name}!")
    st.sidebar.write(user_email)

    # Dicionario de paginas
    paginas = {
        "Recebimentos": recebimentos_page
    }

    pagina_selecionada = st.sidebar.radio("Navegar", paginas.keys())

    if st.sidebar.button("Logout"):
        # Limpa o token da session_state para fazer logout
        del st.session_state['token']
        st.rerun()

    # Executa a função da página selecionada
    paginas[pagina_selecionada]()
