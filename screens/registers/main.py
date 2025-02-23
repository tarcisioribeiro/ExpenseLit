from functions.login import CreateUser
from screens.registers.update_account import UpdateAccounts
from screens.registers.update_credit_card import UpdateCreditCards
from screens.registers.update_creditors import Creditors
from screens.registers.update_benefited import Benefited
import streamlit as st


class Registers:
    """
    Classe que representa os cadastros realizados na aplicação.
    """

    def main_menu(self):
        """
        Menu principal.
        """

        col1, col2, col3 = st.columns(3)

        with col3:
            cl1, cl2 = st.columns(2)

        registers_menu_options = {
            "Contas": UpdateAccounts(),
            "Cartões de Crédito": UpdateCreditCards(),
            "Credores": Creditors(),
            "Beneficiados": Benefited()
            }

        with col1:
            st.header(body=":memo: Cadastros")

        with col2:

            selected_menu_option = st.selectbox(label="Menu", options=registers_menu_options.keys())
            selected_class = registers_menu_options[selected_menu_option]

        selected_class.main_menu(cl2)