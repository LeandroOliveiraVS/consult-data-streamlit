import streamlit as st
from streamlit_oauth import OAuth2Component
from streamlit_cookies_manager import EncryptedCookieManager
import streamlit.components.v1 as components
import requests
import json

# Importando as funções que representam cada página
from paginas.recebimentos import recebimentos_page
from paginas.reembolsos import reembolsos_page


# --- FUNÇÃO PARA CARREGAR O CSS ---
def carregar_css_local(caminho_arquivo):
    try:
        with open(caminho_arquivo, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS não encontrado em: {caminho_arquivo}")


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Corporativo", page_icon="🔐", layout="wide")

# --- INJEÇÃO DE CSS A PARTIR DO ARQUIVO EXTERNO ---
carregar_css_local("./assets/css/style.css")

# --- CONFIGURAÇÃO DO GOOGLE OAUTH E COOKIES ---
try:
    CLIENT_ID = st.secrets["google_oauth"]["client_id"]
    CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
    REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
    cookie_password = st.secrets.get("cookie_password", "default_cookie_password_123")
except KeyError:
    st.error(
        "As credenciais do Google OAuth ou a senha do cookie não foram encontradas em secrets.toml."
    )
    st.stop()

cookies = EncryptedCookieManager(password=cookie_password)
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    refresh_token_endpoint=None,
    revoke_token_endpoint="https://oauth2.googleapis.com/revoke",
)


# --- FUNÇÃO PARA VERIFICAR O ESTADO DE LOGIN ---
def check_login():
    # 1. Verifica se já estamos logados na sessão atual
    if "user_info" in st.session_state:
        return True

    # 2. Se não, verifica se temos um cookie válido
    if not cookies.ready():
        return None  # Indica que os cookies ainda não estão prontos

    user_info_json = cookies.get("user_info")
    if user_info_json:
        st.session_state.user_info = json.loads(user_info_json)
        return True

    return False


# --- CONTROLO PRINCIPAL DO APP ---

is_logged_in = check_login()

if is_logged_in is None:
    st.spinner("Inicializando sessão...")
elif is_logged_in:
    # --- MOSTRA A APLICAÇÃO PRINCIPAL ---
    user_info = st.session_state.user_info
    user_name = user_info.get("name", "Usuário")
    user_email = user_info.get("email", "")

    st.sidebar.title(f"Bem-vindo, {user_name}!")
    st.sidebar.write(user_email)

    paginas = {
        "Recebimentos": recebimentos_page,
        "Reembolsos": reembolsos_page,
    }

    pagina_selecionada = st.sidebar.radio("Navegar", paginas.keys())

    if st.sidebar.button("Logout"):
        if "user_info" in cookies:
            del cookies["user_info"]

        if "user_info" in cookies:
            del cookies["user_info"]
        if "user_info" in st.session_state:
            del st.session_state["user_info"]

        # Força uma recarga completa do navegador para garantir um estado limpo
        components.html("<script>window.location.reload();</script>", height=0)
        st.rerun()

    paginas[pagina_selecionada]()
else:
    # --- MOSTRA A TELA DE LOGIN ---
    with st.container():
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            with st.container():
                st.title("Bem-vindo!")
                st.write(
                    "Faça o login com a sua conta Google para aceder ao dashboard."
                )
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

    if result and "token" in result:
        token = result.get("token")
        access_token = token.get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo", headers=headers
        )

        if response.status_code == 200:
            user_info = response.json()
            # Guarda as informações na sessão e no cookie
            st.session_state.user_info = user_info
            cookies["user_info"] = json.dumps(user_info)
            st.rerun()
        else:
            st.error("Não foi possível obter as informações do usuário do Google.")
