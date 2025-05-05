import streamlit as st
from screens.revenues.confirm_revenue import ConfirmRevenue
from screens.revenues.new_fund_revenue import NewFundRevenue
from screens.revenues.new_revenue import NewCurrentRevenue
from screens.loans.receive_loan import ReceiveLoan


class NewRevenue:
    """
    Classe que representa as novas receitas.
    """

    def main_menu(self):
        """
        Menu principal.
        """

        menu_options = {
            "Receita em Contas Correntes": NewCurrentRevenue(),
            "Receita de Fundo de Garantia": NewFundRevenue(),
            "Receber Valores em Aberto": ReceiveLoan(),
            "Confirmar Receita": ConfirmRevenue(),
        }

        col1, col2, col3 = st.columns(3)

        st.divider()

        with col1:
            st.header(body=":moneybag: Nova Receita")

        with col2:

            revenue_type = st.selectbox(
                label="Tipo de Receita",
                options=menu_options.keys()
            )
            call_interface = menu_options[revenue_type]
        call_interface.main_menu()
