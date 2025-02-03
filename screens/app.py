import streamlit as st
from functions.query_executor import QueryExecutor
from functions.login import Login
from screens.expenses.main import NewExpense
from screens.homepage import Home
from screens.loans.main import Loan
from screens.registers.main import Registers
from screens.reports.main import Reports
from screens.revenues.main import NewRevenue
from screens.new_transfer import NewTransfer
from screens.configuration.main import Configuration
from time import sleep


class App:
    """
    Classe que representa o layout principal da aplicação.
    """

    def logout(self):
        """
        Realiza o logout da aplicação, deletando os registros de sessão do usuário.
        """
        logged_user_name, logged_user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        delete_session_query = """DELETE usuarios_logados FROM usuarios_logados WHERE nome_completo = %s AND documento = %s;"""
        delete_session = QueryExecutor().insert_query(query=delete_session_query, values=(logged_user_name, logged_user_document), success_message="Logout efetuado.", error_message="Erro ao efetuar logout:")

        log_query = '''INSERT INTO seguranca.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
        log_values = (logged_user, "Logoff", "O usuário realizou logoff.")
        QueryExecutor().insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

        with st.spinner("Aguarde um momento..."):
            sleep(1.25)
            st.toast("Saindo do sistema...")
            sleep(1.25)

        st.session_state.is_logged_in = False
        st.rerun()

    def main_menu(self):
        """
        Exibe a página inicial do projeto.
        """
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        sidebar = st.sidebar

        with sidebar:
            call_user = Login()
            name, sex = call_user.check_user()
            call_user.show_user(name, sex)

        sidebar_menu_dictionary = {
            "Início": Home(),
            "Registrar Despesa": NewExpense(),
            "Registrar Receita": NewRevenue(),
            "Registrar Transferência": NewTransfer(),
            "Registrar Empréstimo": Loan(),
            "Relatórios": Reports(),
            "Cadastros": Registers(),
            "Configurações": Configuration()
        }

        sidebar_choice = sidebar.selectbox(
            label="Menu", options=list(sidebar_menu_dictionary.keys()))

        sidebar.divider()

        sidebar_reload_button = sidebar.button(label=":cd: Recarregar")
        sidebar_logoff_button = sidebar.button(label=":lock: Sair")

        if sidebar_reload_button:
            with sidebar:
                with st.spinner(text="Recarregando..."):
                    sleep(2.5)
                    st.rerun()

        if sidebar_logoff_button:
            with sidebar:
                query_executor = QueryExecutor()
                log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                log_values = (logged_user, "Logoff", "O usuário realizou logoff.")
                query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")
                self.logout()

        if sidebar_choice:
            call_interface = sidebar_menu_dictionary[sidebar_choice]
            call_interface.main_menu()
