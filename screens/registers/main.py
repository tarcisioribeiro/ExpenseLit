from functions.create_user import CreateUser
from screens.registers.update_account import UpdateAccounts
from screens.registers.update_credit_card import UpdateCreditCards
import streamlit as st


class Registers:

    def __init__(self):

        def registers_main_menu():

            col1, col2, col3 = st.columns(3)

            registers_menu_options = ["Contas", "Cartões", "Usuários"]

            with col1:
                st.header(body=":memo: Cadastros")

            with col2:

                selected_menu_option = st.selectbox(label="Menu", options=registers_menu_options)

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

        self.main_menu = registers_main_menu