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
            call_account_update = UpdateAccounts()
            call_account_update.show_interface()

        elif selected_menu_option == registers_menu_options[1]:
            call_credit_card_update = UpdateCreditCards()
            call_credit_card_update.credit_cards_interface()

        elif selected_menu_option == registers_menu_options[2]:
            call_create_user = CreateUser()
            call_create_user.main_menu()

        elif selected_menu_option == registers_menu_options[3]:
            call_creditor_app = Creditors()
            call_creditor_app.main_menu()

        elif selected_menu_option == registers_menu_options[4]:
            call_benefited_app = Benefited()
            call_benefited_app.main_menu()
