from screens.loans.new_loan import NewLoan
import streamlit as st


class Loan:

    def main_menu(self):

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(":bank: Novo Empréstimo")

        with col2:
            loan_menu_choice = st.selectbox(
                label="Opções",
                options=[
                    "Tomar empréstimo",
                    "Realizar empréstimo",
                ],
            )

        st.divider()

        if loan_menu_choice == "Tomar empréstimo":
            call_loan = NewLoan()
            call_loan.take_loan()

        elif loan_menu_choice == "Realizar empréstimo":
            call_loan = NewLoan()
            call_loan.make_loan()
