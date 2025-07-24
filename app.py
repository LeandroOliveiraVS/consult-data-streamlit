import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
from streamlit_cookies_manager import EncryptedCookieManager
import json

from paginas.recebimentos import recebimentos_page

caminho_arquivo = './assets/css/style.css'

# --- FUNÇÃO PARA CARREGAR O CSS ---
def carregar_css_local(caminho_arquivo):
    with open(caminho_arquivo) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Configuração da página principal ---
st.set_page_config(
    page_title="Dashboard Corporativo",
    page_icon="🔐",
    layout="wide"
)

# --- INJEÇÃO DE CSS A PARTIR DO ARQUIVO ---
carregar_css_local('./assets/css/style.css')

# --- CONFIGURAÇÃO DO GOOGLE OAUTH ---
# Carrega as credenciais do arquivo secrets.toml
try:
    CLIENT_ID = st.secrets["google_oauth"]["client_id"]
    CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
    REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
except KeyError:
    st.error("As credenciais do Google OAuth não foram encontradas em secrets.toml. Por favor, siga o guia de configuração.")
    st.stop()

# --- GESTOR DE COOKIES ---
cookie_password = st.secrets.get("cookie_password", "default_cookie_password_123")
cookies = EncryptedCookieManager(password=cookie_password)

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

# 1. Tenta obter as informações do usuário a partir do cookie na inicialização
if 'user_info' not in st.session_state:
    user_info_json = cookies.get('user_info')
    if user_info_json:
        # Converte o texto JSON de volta para um dicionário
        st.session_state.user_info = json.loads(user_info_json)

#  2. Se ainda não estiver logado (nem por cookie, nem por sessão), mostra o login
if 'user_info' not in st.session_state:
    # Coloca o conteúdo da tela de login dentro de um container para estilização
    with st.container():
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            with st.container():
                st.title("Bem-vindo!")
                st.write("Faça o login com a sua conta Google para aceder ao dashboard.")
                st.markdown("<br>", unsafe_allow_html=True)
                result = oauth2.authorize_button(
                    name="Entrar com o Google",
                    icon="https://www.google.com.tw/favicon.ico",
                    redirect_uri=REDIRECT_URI,
                    scope="openid email profile",
                    key="google",
                    extras_params={"prompt": "consent", "access_type": "offline"},
                    use_container_width=True,
                )
                # -------------------------------------------------------------------------

    # Se o login for bem-sucedido, o 'result' conterá o token
    if result and "token" in result:
        token = result.get('token')
        access_token = token.get('access_token')
            
        # Faz a chamada à API do Google para obter as informações do perfil
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)

        if response.status_code == 200:
            user_info = response.json()
            # Guarda as informações na sessão e no cookie
            st.session_state.user_info = user_info
            cookies['user_info'] = json.dumps(user_info)
            st.rerun()
        else:
            st.error("Não foi possível obter as informações do usuário do Google.")
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
        # 5. Apaga o cookie e a sessão ao fazer logout
        if 'user_info' in cookies:
            del cookies['user_info']
        if 'token' in st.session_state: del st.session_state['token']
        if 'user_info' in st.session_state: del st.session_state['user_info']
        st.rerun()

    # Executa a função da página selecionada
    paginas[pagina_selecionada]()
