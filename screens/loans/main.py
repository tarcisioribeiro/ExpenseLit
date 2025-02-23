from screens.loans.new_loan import TakeNewLoan, MakeNewLoan
import streamlit as st


class Loan:
    """
    Classe que representa os empréstimos.
    """

    def main_menu(self):
        """
        Menu principal.
        """

        col1, col2, col3 = st.columns(3)

        with col1:
            st.header(":bank: Novo Empréstimo")

        menu_options = {
            "Tomar empréstimo": TakeNewLoan,
            "Realizar empréstimo": MakeNewLoan
        }

        with col2:
            loan_menu_options = st.selectbox(label="Menu", options=menu_options.keys())
            selected_class = menu_options[loan_menu_options]
        
        st.divider()
        selected_class().main_menu()
