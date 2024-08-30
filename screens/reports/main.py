import streamlit as st
from screens.reports.receipts import Receipts
from screens.reports.account_statement import AccountStatement

class Reports:
    def __init__(self):

        call_receipts = Receipts()
        call_statement = AccountStatement()

        superior_menu_options = ["Consultar Comprovante", "Extrato Bancário"]

        def reports_interface():

            col1, col2, col3 = st.columns(3)

            with col1:
                st.header(body=":ledger: Relatórios")

            with col3:

                cm_cl1, cm_cl2 = st.columns(2)

                with cm_cl2:
                    menu_selected_option = st.selectbox(label="Menu", options=superior_menu_options)

            if menu_selected_option == superior_menu_options[0]:
                st.divider()
                call_receipts.get_receipt_data()

            elif menu_selected_option == superior_menu_options[1]:
                st.divider()
                call_statement.main_menu()

        self.interface = reports_interface
