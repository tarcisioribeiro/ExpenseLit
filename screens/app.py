import streamlit as st
from dictionary.sql.others_queries import delete_session_query
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
from screens.configuration.help import Help
from time import sleep


class App:
    """
    Classe que representa o layout principal da aplicação.
    """

    def logout(self):
        """
        Realiza o logout da aplicação,
        deletando os registros de sessão do usuário.
        """
        user_id, user_document = Login().get_user_data()

        QueryExecutor().insert_query(
            query=delete_session_query,
            values=(user_id, user_document),
            success_message="Logout efetuado.",
            error_message="Erro ao efetuar logout:"
        )

        log_values = (user_id, "Logoff", "O usuário realizou logoff.")
        QueryExecutor().register_log_query(
            log_values,
        )
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
        user_id, user_document = Login().get_user_data()

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

        sidebar_help_button = sidebar.button(label=":question: Ajuda")
        sidebar_reload_button = sidebar.button(label=":cd: Recarregar")
        sidebar_logoff_button = sidebar.button(label=":lock: Sair")

        if sidebar_help_button:
            Help().main_menu()

        if sidebar_reload_button:
            with sidebar:
                with st.spinner(text="Recarregando..."):
                    sleep(2.5)
                    st.rerun()

        if sidebar_logoff_button:
            with sidebar:
                log_values = (
                    user_id,
                    "Logoff",
                    "O usuário realizou logoff."
                )
                QueryExecutor().register_log_query(
                    log_values,
                )
                self.logout()

        if sidebar_choice:
            call_interface = sidebar_menu_dictionary[sidebar_choice]
            call_interface.main_menu()
