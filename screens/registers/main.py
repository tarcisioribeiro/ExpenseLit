from functions.create_user import CreateUser
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

        registers_menu_options = [
            "Contas", "Cartões", "Usuários", "Credores", "Beneficiados"]

        with col1:
            st.header(body=":memo: Cadastros")

        with col2:

            selected_menu_option = st.selectbox(
                label="Menu", options=registers_menu_options)

        st.divider()

        if selected_menu_option == registers_menu_options[0]:
            UpdateAccounts().main_menu()

        elif selected_menu_option == registers_menu_options[1]:
            UpdateCreditCards().main_menu()

        elif selected_menu_option == registers_menu_options[2]:
            CreateUser().main_menu()

        elif selected_menu_option == registers_menu_options[3]:
            Creditors().main_menu()

        elif selected_menu_option == registers_menu_options[4]:
            Benefited().main_menu()
