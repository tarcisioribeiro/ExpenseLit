import streamlit as st
import mysql.connector
import bcrypt
import os
import uuid
from dictionary.vars import to_remove_list, absolute_app_path
from dictionary.db_config import db_config
from functions.query_executor import QueryExecutor
from time import sleep


class Login:
    """
    Classe que representa o login, com métodos de validação e obtenção dos dados de login.
    """
    def get_user_data(self, return_option: str):
        """
        Faz a consulta dos dados do usuário, de acordo com a opção de dados retornados selecionada.

        Parameters
        ----------
        return_option : str
            Define os dados que serão retornados pela função.

        Returns
        -------
        user_name : str
            Nome completo do usuário logado.
        user_document : str
            Documento do usuário logado.
        """
        user_login_query = ""
        user_data_query = ""

        if return_option == "user_doc_name":
            user_data_query = """
            SELECT usuarios.nome, usuarios.documento
            FROM usuarios
            INNER JOIN usuarios_logados ON usuarios.id_usuario = usuarios_logados.usuario_id
            WHERE usuarios_logados.sessao_id = %s;
            """

            user_data = QueryExecutor().complex_compund_query(query=user_data_query, list_quantity=2, params=(st.session_state.sessao_id,))
            user_data = QueryExecutor().treat_complex_result(values_to_treat=user_data, values_to_remove=to_remove_list)

            user_name = user_data[0]
            user_document = user_data[1]

            return user_name, user_document

        elif return_option == "user_login_password":

            user_login_query = """
            SELECT usuarios.login, usuarios.senha
            FROM usuarios
            INNER JOIN usuarios_logados ON usuarios.id_usuario = usuarios_logados.usuario_id
            WHERE usuarios_logados.sessao_id = %s
            """

            user_login_data = QueryExecutor().complex_compund_query(query=user_login_query, list_quantity=2, params=(st.session_state.sessao_id,))
            user_login_data = QueryExecutor().treat_complex_result(values_to_treat=user_login_data, values_to_remove=to_remove_list)

            user_login = user_login_data[0]
            user_password = str(user_login_data[1])
            
            if user_password.startswith('b'):
                user_password = user_password[1:]

            return user_login, user_password

        else:
            st.error(body="Parâmetro não reconhecido.")

    def validate_login(self, login: str, password: str):
        """
        Realiza a validação do login do usuário.

        Parameters
        ----------
        login : str
            O nome de usuário.
        password: str
            A senha do usuário.
        """

        check_if_user_exists = QueryExecutor().simple_consult_query(query="SELECT COUNT(id_usuario) FROM usuarios WHERE login = %s AND senha = %s", params=(login, password))
        check_if_user_exists = QueryExecutor().treat_simple_result(check_if_user_exists, to_remove_list)
        check_if_user_exists = int(check_if_user_exists)

        if check_if_user_exists == 1:
            return True
        else:
            return False


    def check_login(self, user, password):
        """
        Valida o login do usuário.

        Parameters
        ----------
        user : str
            Nome do usuário que está realizando o login.
        password : str
            Senha do usuário que está realizando o login.

        Returns
        -------
        bool
            A validade do login.
        hashed_password : str
            A senha do usuário encriptada.
        """
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "SELECT senha FROM usuarios WHERE login = %s"
        cursor.execute(query, (user,))
        result = cursor.fetchone()

        if result:
            hashed_password = result[0].encode('utf-8') if isinstance(result[0], str) else result[0]
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password), hashed_password

        return False, '0'
    
    def register_login(self, logged_user_id: int, logged_user_name: str, logged_user_document: str):
        """
        Registra a sessão do usuário no banco de dados.

        Paramaters
        ----------
        logged_user_id : int
            ID do usuário que está presente na tabela 'usuarios'.
        logged_user_name : str
            Nome completo do usuário, presente na tabela 'usuarios'.
        logged_user_document : str
            Documento do usuário, presente na tabela 'usuarios'.
        """
        session_id = str(uuid.uuid4())

        register_session_query = """INSERT INTO usuarios_logados (usuario_id, nome_completo, documento, sessao_id) VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE data_login = CURRENT_TIMESTAMP, sessao_id = VALUES(sessao_id);"""
        session_values = (logged_user_id, logged_user_name, logged_user_document, session_id)

        QueryExecutor.insert_query(self, query=register_session_query, values=session_values, success_message="Sessão registrada.", error_message="Erro ao registrar sessão:")

        sleep(1.25)

        st.session_state.usuario_id = logged_user_id
        st.session_state.sessao_id = session_id

    def check_user(self):
        """
        Realiza a consulta do nome e sexo do usuário.

        Returns
        -------
        name : str
            O nome do usuário.
        sex : str
            O sexo do usuário.
        """
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        name_query: str = "SELECT nome FROM usuarios WHERE login = %s AND senha = %s"
        sex_query: str = "SELECT sexo FROM usuarios WHERE login = %s AND senha = %s"

        name = QueryExecutor().simple_consult_query(query=name_query, params=(logged_user, logged_user_password))
        name = QueryExecutor().treat_simple_result(name, to_remove_list)

        sex = QueryExecutor().simple_consult_query(query=sex_query, params=(logged_user, logged_user_password))
        sex = QueryExecutor().treat_simple_result(sex, to_remove_list)

        return name, sex

    def show_user(self, name: str, sex: str):
        """
        Exibe o nome e sexo do usuário.

        Parameters
        ----------
        name : str
            O nome do usuário.
        sex : str
            O sexo do usuário.
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

            st.header(body=":moneybag: ExpenseLit")

            with st.container():
                with st.expander(label=":computer: Login", expanded=True):

                    user = st.text_input(":closed_lock_with_key: Usuário")
                    password = st.text_input(":key: Senha", type="password")
                    login_button = st.button(label=":unlock: Entrar")

                    is_login_valid, hashed_password = self.check_login(user, password)

                    if login_button:
                        if is_login_valid:
                            with st.spinner("Aguarde..."):
                                sleep(1)
                                st.toast("Login bem-sucedido!")

                                log_query = '''INSERT INTO logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES (%s, %s, %s)'''
                                log_values = (user, 'Acesso','O usuário acessou o sistema.')
                                query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                                name_doc_query = """SELECT id_usuario, nome, documento FROM usuarios WHERE login = %s AND senha = %s;"""

                                user_name_doc = QueryExecutor().complex_compund_query(query=name_doc_query, list_quantity=3, params=(user, hashed_password))
                                user_name_doc = QueryExecutor().treat_numerous_simple_result(user_name_doc, to_remove_list)

                                user_id = int(user_name_doc[0])
                                user_name = str(user_name_doc[1])
                                user_document = str(user_name_doc[2])

                                self.register_login(logged_user_id=user_id, logged_user_name=user_name, logged_user_document=user_document)

                            st.session_state.is_logged_in = True
                            st.rerun()

                        else:
                            st.error("Login falhou. Verifique suas credenciais.")
