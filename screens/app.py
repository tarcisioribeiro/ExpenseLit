import streamlit as st
from data.cache.session_state import logged_user
from dictionary.vars import menu_options
from functions.query_executor import QueryExecutor
from functions.login import User
from screens.expenses.main import NewExpense
from screens.homepage import Home
from screens.loans.main import Loan
from screens.registers.main import Registers
from screens.reports.main import Reports
from screens.revenues.main import NewRevenue
from screens.new_transfer import NewTransfer
from time import sleep


class App:
    """
    Classe que representa a página inicial do aplicativo.

    Attributes
    ----------
    logout()
        Realiza a saída do usuário do aplicativo.
    HomePage()
        Exibe a página inicial do aplicativo.
    """

    def logout(self):
        """
        Realiza a saída do usuário do aplicativo.
        """

        st.session_state.is_logged_in = False
        st.rerun()


    def HomePage(self):
        """
        Exibe a página inicial do aplicativo.
        """

        sidebar = st.sidebar

        with sidebar:
            call_user = User()
            name, sex = call_user.check_user()
            call_user.show_user(name, sex)

        sidebar_choice = sidebar.selectbox(label="Menu", options=list(menu_options))

        sidebar.divider()

        sidebar_home_button = sidebar.button(label=":house: Início")
        sidebar_reload_button = sidebar.button(label=":cd: Recarregar")
        sidebar_logoff_button = sidebar.button(label=":lock: Sair")

        if sidebar_reload_button:
            with sidebar:
                with st.spinner(text="Recarregando..."):
                    sleep(2.5)
                    st.rerun()

        if sidebar_logoff_button:
            with sidebar:
                with st.spinner("Aguarde um momento..."):

                    query_executor = QueryExecutor()
                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                    log_values = (logged_user, "Logoff", "O usuário realizou logoff.")
                    query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")
                    sleep(1)
                    st.toast("Saindo do sistema...")
                    sleep(1)
                    self.logout()


        if sidebar_choice == "Selecione uma opção" or sidebar_home_button:
            call_home = Home()
            call_home.show_balance()

        elif sidebar_choice == "Registrar despesa":
            call_expenses = NewExpense()
            call_expenses.main_menu()

        elif sidebar_choice == "Empréstimos":
            call_loan = Loan()
            call_loan.main_menu()
            
        elif sidebar_choice == "Registrar receita":
            call_revenue = NewRevenue()
            call_revenue.main_menu()

        elif sidebar_choice == "Registrar transferência":
            call_transfer = NewTransfer()
            call_transfer.get_transfer()

        elif sidebar_choice == "Relatórios":
            call_report = Reports()
            call_report.interface()

        elif sidebar_choice == "Cadastros":
            call_registers = Registers()
            call_registers.main_menu()