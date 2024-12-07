from screens.expenses.new_expense import NewCurrentExpense
from screens.expenses.new_credit_card_expense import NewCreditCardExpense
from screens.expenses.pay_credit_card_invoice import CreditCardInvoice
from screens.loans.pay_loan import PayLoan
import streamlit as st


class NewExpense:

    def __init__(self):

        def expenses_main_menu():

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("	:money_with_wings: Nova Despesa")

            with col2:
                menu_choice = st.selectbox(
                    label="Tipo de despesa",
                    options=[
                        "Despesa em conta corrente",
                        "Despesa de cartão",
                        "Pagar fatura de cartão",
                        "Pagar valores em aberto"
                    ],
                )

            st.divider()

            if menu_choice == "Despesa em conta corrente":
                call_expense = NewCurrentExpense()
                call_expense.get_expense()

            elif menu_choice == "Despesa de cartão":
                call_credit_card_expense = NewCreditCardExpense()
                call_credit_card_expense.get_credit_card_expense()

            elif menu_choice == "Pagar fatura de cartão":
                call_update_credit_card_invoices = CreditCardInvoice()
                call_update_credit_card_invoices.show_update_credit_card_invoices()

            elif menu_choice == "Pagar valores em aberto":
                call_pay_loan = PayLoan()
                call_pay_loan.show_loans()

        self.main_menu = expenses_main_menu