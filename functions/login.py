import streamlit as st
import mysql.connector
import bcrypt
import os
from dictionary.vars import to_remove_list, absolute_app_path
from dictionary.db_config import db_config
from dictionary.sql import doc_name_query, name_query, sex_query
from functions.query_executor import QueryExecutor
from time import sleep


class Login:
    """
    Classe que representa o login, com métodos de validação e obtenção dos dados de login.
    """

    def validate_login(self, login: str, password: str):
        """
        Realiza a validação do login do usuário.

        Parameters
        ----------
        login: str
        """

        check_if_user_exists = QueryExecutor().simple_consult_query(
            "SELECT COUNT(id_usuario) FROM usuarios WHERE login = %s AND senha = %s", params=(login, password))
        check_if_user_exists = QueryExecutor().treat_simple_result(
            check_if_user_exists, to_remove_list)
        check_if_user_exists = int(check_if_user_exists)

        if check_if_user_exists == 1:
            return True
        else:
            return False

    def get_user_doc_name(self):
        """
        Realiza a consulta do nome e documento do usuário.

        Returns
        -------
        owner_name: str = O nome do usuário.
        owner_document: int = O documento do usuário.
        """

        user_doc_name = QueryExecutor().complex_consult_query(
            doc_name_query)
        treated_user_doc_name = QueryExecutor().treat_complex_result(
            user_doc_name, to_remove_list)

        owner_name = treated_user_doc_name[0]
        owner_document = treated_user_doc_name[1]

        return owner_name, owner_document

    def check_login(self, user, password):
        """
        Valida o login do usuário.

        Parameters
        ----------
        user: Nome do usuário que está realizando o login.
        password: Senha do usuário que está realizando o login.

        Returns
        -------
        bool: A validade do login.
        hashed_password (str): A senha do usuário encriptada.
        """
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "SELECT senha FROM usuarios WHERE login = %s"
        cursor.execute(query, (user,))
        result = cursor.fetchone()

        if result:
            hashed_password = result[0]
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password), hashed_password
        return False, '0'

    def check_user(self):
        """
        Realiza a consulta do nome e sexo do usuário.

        Returns
        -------
        name: str = O nome do usuário.
        sex: str = O sexo do usuário.
        """
        name = QueryExecutor().simple_consult_query(name_query)
        name = QueryExecutor().treat_simple_result(name, to_remove_list)

        sex = QueryExecutor().simple_consult_query(sex_query)
        sex = QueryExecutor().treat_simple_result(sex, to_remove_list)

        return name, sex

    def show_user(self, name: str, sex: str):
        """
        Exibe o nome e sexo do usuário.

        Parameters
        ----------
        name: str = O nome do usuário.
        sex: str = O sexo do usuário.
        """

        if sex == "M":
            st.image(
                image="{}/library/images/man.png".format(absolute_app_path))
        elif sex == "F":
            st.image(
                image="{}/library/images/woman.png".format(absolute_app_path))
        st.text(body="{}".format(name))
        st.divider()

    def get_login(self):
        """
        Realiza a coleta dos dados de login do usuário.
        """
        query_executor = QueryExecutor()

        col1, col2, col3 = st.columns(3)

        with col2:

            st.header(body=":heavy_dollar_sign: ExpenseLit")

            with st.container():
                with st.expander(label=":computer: Login", expanded=True):

                    user = st.text_input(":closed_lock_with_key: Usuário")
                    password = st.text_input(":key: Senha", type="password")
                    login_button = st.button(label=":unlock: Entrar")

                    if login_button:
                        is_login_valid, hashed_password = self.check_login(
                            user, password)

                        st.info(is_login_valid)
                        st.info(hashed_password)

                        if is_login_valid:
                            with st.spinner("Aguarde..."):
                                sleep(1)
                                st.toast("Login bem-sucedido!")

                                log_query = '''INSERT INTO logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES (%s, %s, %s)'''
                                log_values = (user, 'Acesso',
                                              'O usuário acessou o sistema.')
                                query_executor.insert_query(
                                    log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                                with open("data/cache/session_state.py", "w") as archive:
                                    archive.write(
                                        "logged_user = '{}'\n".format(user))
                                    archive.write(
                                        "logged_user_password = {}\n".format(hashed_password))
                                    sleep(1)
                                    os.chmod(
                                        "data/cache/session_state.py", 0o600)
                                sleep(1)

                            st.session_state.is_logged_in = True
                            st.rerun()

                        else:
                            st.error(
                                "Login falhou. Verifique suas credenciais.")
