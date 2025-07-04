import streamlit as st
from screens.reports.account_statement import AccountStatement
from screens.reports.receipts import Receipts
from screens.reports.ask import SQLChatBot


class Reports:
    """
    Classe que representa os relatórios disponíveis na aplicação.
    """

    def main_menu(self):
        """
        Menu principal.
        """

        superior_menu_options = {
            "Consultar Comprovante": Receipts(),
            "Extrato Bancário": AccountStatement(),
            "Assistente Financeiro": SQLChatBot()
        }

        col1, col2, col3 = st.columns(3)

        with col1:
            st.header(body=":ledger: Relatórios")

        with col2:
            menu_selected_option = st.selectbox(
                label="Menu",
                options=superior_menu_options.keys()
            )
            selected_class = superior_menu_options[menu_selected_option]

        st.divider()

        selected_class.main_menu()
