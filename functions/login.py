import streamlit as st
from dictionary.vars import to_remove_list, absolute_app_path
from dictionary.sql import doc_name_query, name_query, sex_query
from functions.query_executor import QueryExecutor
from time import sleep


class User:
    """
    Classe responsável pela validação do login do usuário no sistema.

    Attributes
    ----------
    validate_login(login, password)
        Realiza a validação da existência do login do usuário.
    get_user_doc_name()
        Realiza a busca do nome e documento do usuário.
    check_user()
        Realiza a consulta do nome e sexo do usuário.
    show_user(name, sex)
        Exibe o nome e avatar do usuário.
    get_login()
        Exibe a tela de login e realiza a chamada da função de validação do login.
    """

    def validate_login(self, login: str, password: str):
        """
        Realiza a validação da existência do login do usuário.

        Parameters
        ----------
        login: str
            O login do usuário.
        password: str
            A senha do usuário.

        Returns
        -------
        True or False
            Valor booleano que corresponde a existência do usuário no banco de dados.
        """

        query_executor = QueryExecutor()

        check_if_user_exists = query_executor.simple_consult_query(
            "SELECT COUNT(id_usuario) FROM usuarios WHERE login = '{}' AND senha = '{}'".format(
                login, password
            )
        )
        check_if_user_exists = query_executor.treat_simple_result(
            check_if_user_exists, to_remove_list
        )
        check_if_user_exists = int(check_if_user_exists)

        if check_if_user_exists == 1:
            return True
        else:
            return False

    def get_doc_name(self):
        """
        Realiza a busca do nome e documento do usuário.

        Returns
        -------
        owner_name: Any
            Nome do usuário.
        owner_document: Any
            Documento do usuário.
        """

        query_executor = QueryExecutor()

        user_doc_name = query_executor.complex_consult_query(doc_name_query)
        treated_user_doc_name = query_executor.treat_complex_result(
            user_doc_name, to_remove_list
        )

        owner_name = treated_user_doc_name[0]
        owner_document = treated_user_doc_name[1]

        return owner_name, owner_document

    def check_user(self):
        """
        Realiza a consulta do nome e sexo do usuário.

        Returns
        -------
        name: str
            O nome do usuário.
        sex: str
            O sexo do usuário.
        """

        query_executor = QueryExecutor()

        name = query_executor.simple_consult_query(name_query)
        name = query_executor.treat_simple_result(name, to_remove_list)

        sex = query_executor.simple_consult_query(sex_query)
        sex = query_executor.treat_simple_result(sex, to_remove_list)

        return name, sex

    def show_user(self, name: str, sex: str):
        """
        Exibe o nome e avatar do usuário.

        Parameters
        ----------
        name: str
            O nome do usuário.
        sex: str
            O sexo do usuário.
        """

        if sex == "M":
            st.image(image="{}/library/images/man.png".format(absolute_app_path))
        elif sex == "F":
            st.image(image="{}/library/images/woman.png".format(absolute_app_path))
        st.text(body="{}".format(name))
        st.divider()

    def get_login(self):
        """
        Exibe a tela de login e realiza a chamada da função de validação do login.
        """

        query_executor = QueryExecutor()

        col1, col2, col3 = st.columns(3)

        with col2:
            st.header(body=":dollar: Controle Financeiro")

            with st.container():
                with st.expander(label=":computer: Login", expanded=True):
                    user = st.text_input(":closed_lock_with_key: Usuário")
                    password = st.text_input(":key: Senha", type="password")
                    login_button = st.button(label=":unlock: Entrar")

                    if login_button:
                        if self.validate_login(user, password):
                            with st.spinner("Aguarde..."):
                                sleep(1)
                                st.toast("Login bem-sucedido!")
                                sleep(1)
                                with open(
                                    "data/cache/session_state.py", "w"
                                ) as session:
                                    session.write("logged_user = '{}'".format(user))
                                    session.write(
                                        "\nlogged_user_password = '{}'".format(password)
                                    )
                                    log_query = """INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);"""
                                    log_values = (
                                        user,
                                        "Acesso",
                                        "O usuário acessou o sistema.",
                                    )
                                    query_executor.insert_query(
                                        log_query,
                                        log_values,
                                        "Log gravado.",
                                        "Erro ao gravar log:",
                                    )

                                st.session_state.is_logged_in = True
                                st.rerun()

                        else:
                            st.error("Login falhou. Verifique suas credenciais.")
