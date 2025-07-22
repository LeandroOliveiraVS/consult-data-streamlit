import streamlit as st
import bcrypt
import sqlalchemy as sa

from core.connection import conectar_banco

def admin_management_page():
    """
    Renderiza a página para administradores criarem novos usuários.
    """
    st.title("🔑 Gestão de Usuários")
    st.write("Crie novos usuários para o sistema.")

    with st.form("create_user_form", clear_on_submit=True):
        st.subheader("Criar Novo Usuário")

        new_username = st.text_input("Nome do Novo Usuário").lower()
        new_password = st.text_input("Senha para o Novo Usuário", type="password")
        is_admin = st.checkbox("Este usuário será um administrador?")

        submitted = st.form_submit_button("Criar Usuário")

        if submitted:
            if not new_username or not new_password:
                st.warning("Por favor, preencha todos os campos.")
            else:
                engine = conectar_banco()
                connection = None
                try:
                    # Gera a hash segura da senha
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    admin_flag = 'V' if is_admin else 'X'

                    # Passo 1: Obter a conexão
                    connection = engine.connect()
                    # Passo 2: Iniciar a transação
                    transaction = connection.begin()

                    query = sa.text(
                        "INSERT INTO users (username, hashed_password, admin) VALUES (:username, :password, :admin)"
                    )
                    connection.execute(query, {"username":new_username, "password": hashed_password, "admin":admin_flag})
                    # Passo 3: Commitar as modificações
                    transaction.commit()

                    st.success(f"Usuário '{new_username}' criado com sucesso!")

                except sa.exc.IntegrityError:
                    st.error(f"Erro: O usuário '{new_username}' já existe.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao criar o usuário: {e}")