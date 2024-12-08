import streamlit as st
from screens.reports.receipts import Receipts
from screens.reports.account_statement import AccountStatement


class Reports:
    def __init__(self):

        superior_menu_options = {
            "Consultar Comprovante": Receipts(),
            "Extrato Bancário": AccountStatement(),
        }

        def reports_interface():

            col1, col2, col3 = st.columns(3)

            with col1:
                st.header(body=":ledger: Relatórios")

            with col3:

                cm_cl1, cm_cl2 = st.columns(2)

                with cm_cl2:
                    menu_selected_option = st.selectbox(label="Menu", options=superior_menu_options.keys())

            st.divider()

            if menu_selected_option:
                call_interface = superior_menu_options[menu_selected_option]
                call_interface.main_menu()

        self.main_menu = reports_interface
