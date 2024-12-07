import streamlit as st
from screens.revenues.confirm_revenue import ConfirmRevenue
from screens.revenues.new_fund_revenue import NewFundRevenue
from screens.revenues.new_revenue import NewCurrentRevenue


class NewRevenue:

    def __init__(self):

        new_fund_revenue = NewFundRevenue()
        confirm_revenue = ConfirmRevenue()
        new_current_revenue = NewCurrentRevenue()

        def revenue_main_menu():

            col1, col2, col3 = st.columns(3)

            menu_options = ["Receita em Contas Correntes", "Receita de Fundo de Garantia", "Confirmar recebimento"]

            st.divider()

            with col1:
                st.subheader(body=":moneybag: Nova Receita")

            with col2:

                revenue_type = st.selectbox(label="Tipo de Receita", options=menu_options)

            if revenue_type == menu_options[0]:

                new_current_revenue.get_revenue()

            elif revenue_type == menu_options[1]:

                new_fund_revenue.new_fund_revenue()

            elif revenue_type == menu_options[2]:

                confirm_revenue.confirm_revenue()

        self.main_menu = revenue_main_menu