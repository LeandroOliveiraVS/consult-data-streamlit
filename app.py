import streamlit as st
import sqlalchemy as sa
import bcrypt

from core.connection import conectar_banco
from paginas.recebimentos import recebimentos_page

# Configuração da página principal
st.set_page_config(
    page_title="Dashboard Corporativo",
    page_icon="🔐",
    layout="wide"
)

# --- LÓGICA DE LOGIN ---

def check_login(username, password):
    """
    Verifica as credenciais do usuário consultando o banco de dados.
    Retorna True se o login for bem-sucedido, False caso contrário.
    """
    engine = conectar_banco()
    try:
        with engine.connect() as connection:
            # Prepara a consulta para buscar o hash da senha do usuário
            query = sa.text("SELECT hashed_password FROM users WHERE username = :username")
            result = connection.execute(query, {"username":username}).fetchone()

            # Se o usuario for encontrado
            if result:
                # Pega o hash do banco de dados
                hashed_password = result[0].encode('utf-8')

                 # Compara o hash do banco com a senha fornecida
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True # Senha correta
    except Exception as e:
        st.error(f"Erro ao verificar o login: {e}")
    
    return False # Usuario não encontrado ou senha incorreta

def login_form():
    # Renderiza o formulário de login
    st.title("Bem-vindo  ao Dashboard!")
    st.write("Por favor, faça o login para continuar.")

    with st.form("login_form"):
        username = st.text_input("Usuário").lower()
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if check_login(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# --- CONTROLE PRINCIPAL DO APP ---

# Inicializa o estado de login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Se não estiver logado, mostra o formulário
if not st.session_state["logged_in"]:
    login_form()

else:
    # Se estiver logado, mostra o app principal
    st.sidebar.title(f"Bem-vindo, {st.session_state['username']}!")

    # Dicionario de paginas
    paginas = {
        "Recebimentos": recebimentos_page
    }

    pagina_selecionada = st.sidebar.radio("Navegar", paginas.keys())

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state.pop("username", None)
        st.rerun()

    # Executa a função da página selecionada
    paginas[pagina_selecionada]()