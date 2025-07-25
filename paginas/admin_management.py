import streamlit as st
import bcrypt
import sqlalchemy as sa
import pandas as pd

from core.connection import conectar_banco
from core.load_data import carregar_tabela


def admin_management_page():
    """
    Renderiza a página para administradores criarem novos usuários.
    """
    st.title("🔑 Gestão de Usuários")
    st.subheader("Crie um novo usuário para o sistema.")

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
                    hashed_password = bcrypt.hashpw(
                        new_password.encode("utf-8"), bcrypt.gensalt()
                    )
                    admin_flag = "V" if is_admin else "X"

                    # Passo 1: Obter a conexão
                    connection = engine.connect()
                    # Passo 2: Iniciar a transação
                    transaction = connection.begin()

                    query = sa.text(
                        "INSERT INTO users (username, hashed_password, admin) VALUES (:username, :password, :admin)"
                    )
                    connection.execute(
                        query,
                        {
                            "username": new_username,
                            "password": hashed_password,
                            "admin": admin_flag,
                        },
                    )
                    # Passo 3: Commitar as modificações
                    transaction.commit()

                    st.toast(f"Usuário '{new_username}' criado com sucesso!")
                    st.cache_data.clear()
                    st.rerun()

                except sa.exc.IntegrityError:
                    st.error(f"Erro: O usuário '{new_username}' já existe.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao criar o usuário: {e}")
                finally:
                    if connection:
                        connection.close()
    st.markdown("---")

    # =========================================================================================
    engine = conectar_banco()
    st.subheader("Excluir usuário")
    try:
        # Carregar a tabela de Usuários
        table = "users"
        df = carregar_tabela(engine, table)

        # Não permite que o admin logado se delete
        admin_logado = st.session_state.get("username", "")
        lista_usuarios_para_deletar = df[df["username"] != admin_logado][
            "username"
        ].tolist()

        # Caso não haja usuários para deletar
        if not lista_usuarios_para_deletar:
            st.info("Não há outros usuários para excluir.")

        else:
            with st.form("delete_user", clear_on_submit=True):
                usuario_selecionado = st.selectbox(
                    "Selecione um Usuário", options=sorted(lista_usuarios_para_deletar)
                )
                submitted_delete = st.form_submit_button("Deletar Usuário")

                if submitted_delete:
                    # Pega o status de admin do usuário selecionado a partir do DataFrame
                    user_info = df[df["username"] == usuario_selecionado]

                    if not user_info.empty and user_info.iloc[0]["admin"] == "V":
                        st.error(
                            f"Não é possível excluir o usuário '{usuario_selecionado}' porque ele é um administrador."
                        )

                    else:
                        # Lógica para deletar o usuário
                        connection = None
                        try:
                            connection = engine.connect()
                            transaction = connection.begin()
                            query = sa.text(
                                "DELETE FROM users WHERE username = :username"
                            )
                            connection.execute(query, {"username": usuario_selecionado})
                            transaction.commit()

                            st.toast(
                                f"Usuário '{usuario_selecionado}' excluído com sucesso!"
                            )
                            st.cache_data.clear()
                            st.rerun()  # Recarrega a página para atualizar a lista
                        except Exception as e:
                            st.error(f"Ocorreu um erro ao excluir o usuário: {e}")
                            if "transaction" in locals() and transaction.is_active:
                                transaction.rollback()
                        finally:
                            if connection:
                                connection.close()

    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar a lista de usuários: {e}")
