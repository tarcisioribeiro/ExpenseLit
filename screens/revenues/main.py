import streamlit as st
from screens.revenues.confirm_revenue import ConfirmRevenue
from screens.revenues.new_fund_revenue import NewFundRevenue
from screens.revenues.new_revenue import NewCurrentRevenue


class NewRevenue:

    def __init__(self):

        menu_options = {
            "Receita em Contas Correntes": NewCurrentRevenue(),
            "Receita de Fundo de Garantia": NewFundRevenue(),
            "Confirmar recebimento": ConfirmRevenue(),
        }

        def revenue_main_menu():

            col1, col2, col3 = st.columns(3)

            st.divider()

            with col1:
                st.header(body=":moneybag: Nova Receita")

            with col2:

                revenue_type = st.selectbox(label="Tipo de Receita", options=menu_options.keys())

            if revenue_type:
                call_interface = menu_options[revenue_type]
                call_interface.main_menu()

        self.main_menu = revenue_main_menu
