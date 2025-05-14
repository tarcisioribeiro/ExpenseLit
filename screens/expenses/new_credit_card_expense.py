import streamlit as st
from datetime import timedelta
from dictionary.vars import EXPENSE_CATEGORIES, TO_REMOVE_LIST
from dictionary.sql.credit_card_expenses_queries import (
    last_credit_card_expense_id_query,
    invoices_quantity_query,
    card_associated_account_id_query,
    credit_card_expense_query
)
from dictionary.sql.credit_card_queries import (
    owner_cards_query
)
from functions.credit_card import Credit_Card
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep


user_id, user_document = Login().get_user_data()


class NewCreditCardExpense:
    """
    Classe que representa uma nova despesa de cartão de crédito.
    """

    def get_last_credit_card_expense_id(self):
        """
        Obtém o último ID de despesas de cartão.
        """

        last_id = QueryExecutor().simple_consult_query(
            last_credit_card_expense_id_query,
            ()
        )
        last_id = QueryExecutor().treat_simple_result(
            last_id,
            TO_REMOVE_LIST
        )

        return last_id

    def insert_new_credit_card_expense(self, query: str, values: tuple):
        """
        Insere no banco de dados uma nova despesa de cartão.

        Parameters
        ----------
        query : str
            A consulta de inserção.
        values : tuple
            A tupla com os valores da nova despesa.
        """

        QueryExecutor().insert_query(
            query,
            values,
            "Despesa de cartão registrada.",
            "Erro ao registrar despesa de cartão:"
        )

    def main_menu(self):
        """
        Obtém os dados da nova despesa de cartão.
        """

        user_cards = QueryExecutor().complex_consult_query(
            query=owner_cards_query,
            params=(user_id, user_document)
        )
        user_cards = QueryExecutor().treat_simple_results(
            user_cards,
            TO_REMOVE_LIST
        )

        col1, col2, col3 = st.columns(3)

        if len(user_cards) == 0:

            with col2:
                st.info("Você ainda não possui cartões cadastrados.")

        elif len(user_cards) >= 1:
            with col1:
                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados da despesa", expanded=True):

                    input_id = int(self.get_last_credit_card_expense_id()) + 1
                    description = st.text_input(
                        label=":lower_left_ballpoint_pen: Descrição",
                        placeholder="Informe uma descrição",
                        max_chars=25,
                        help="Descrição simples para a despesa."
                    )
                    value = st.number_input(
                        label=":dollar: Valor",
                        step=0.01,
                        min_value=0.01
                    )
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(
                        label=":card_index_dividers: Categoria",
                        options=EXPENSE_CATEGORIES
                    )
                    card = st.selectbox(
                        label=":credit_card: Cartão",
                        options=user_cards
                    )
                    remaining_limit = Credit_Card().card_remaining_limit(
                        selected_card=card
                    )
                    remaining_limit = round(remaining_limit, 2)

                    str_remaining_limit = Variable().treat_complex_string(
                        remaining_limit
                    )

                    parcel = st.number_input(
                        label=":pencil: Parcelas", min_value=1, step=1)
                    inputed_credit_card_code = st.text_input(
                        label=":credit_card: Informe o código do cartão",
                        max_chars=3,
                        type="password",
                        help="Código CVV do cartão."
                    )

                    (
                        card_id,
                        credit_card_number,
                        credit_card_owner,
                        credit_card_owner_document,
                        credit_card_code
                    ) = Credit_Card().get_credit_card_key(card=card)

                    confirm_values_checkbox = st.checkbox(
                        label="Confirmar Dados"
                    )

                generate_receipt_button = st.button(
                    label=":pencil: Gerar Comprovante",
                    key="generate_receipt_button"
                )

            with col3:
                if confirm_values_checkbox and generate_receipt_button:

                    invoices_quantity = QueryExecutor().simple_consult_query(
                        invoices_quantity_query,
                        (
                            card_id,
                            card,
                            user_id,
                            user_document
                        )
                    )
                    invoices_quantity = QueryExecutor().treat_simple_result(
                        invoices_quantity,
                        TO_REMOVE_LIST
                    )

                    invoices_quantity = int(invoices_quantity)

                    if invoices_quantity > 0:

                        card_associated_account_id = (
                            QueryExecutor().simple_consult_query(
                                query=card_associated_account_id_query,
                                params=(user_id, user_document, card)
                            )
                        )

                        card_associated_account_id = (
                            QueryExecutor().treat_simple_result(
                                card_associated_account_id,
                                TO_REMOVE_LIST
                            )
                        )

                        with col2:

                            with st.spinner("Aguarde..."):
                                sleep(2.5)

                            st.subheader(
                                body=":white_check_mark: Validação de Dados"
                                )

                            data_expander = st.expander(
                                label="Avisos", expanded=True
                            )

                            with data_expander:
                                st.info(
                                    body="""
                                        Limite restante do cartão: R$ {}
                                        """.format(
                                            str_remaining_limit
                                        )
                                )

                        if (
                            description != ""
                            and value >= 0.01 and value <= remaining_limit
                            and date
                            and category != "Selecione uma opção"
                            and card != "Selecione uma opção"
                            and inputed_credit_card_code == credit_card_code
                        ):
                            with data_expander:
                                st.success(body="Dados válidos.")

                            st.subheader(
                                body=":pencil: Comprovante de Despesa")
                            with st.spinner("Aguarde..."):
                                sleep(2.5)

                            for i in range(0, parcel):
                                if i >= 1:
                                    date += timedelta(days=30)

                                actual_horary = (
                                    GetActualTime().get_actual_time()
                                )

                                values = (
                                    description,
                                    (value / parcel),
                                    date,
                                    actual_horary,
                                    category,
                                    card_id,
                                    credit_card_number,
                                    credit_card_owner,
                                    credit_card_owner_document,
                                    i + 1,
                                    "N",
                                )
                                self.insert_new_credit_card_expense(
                                    credit_card_expense_query, values
                                )

                            str_value = Variable().treat_complex_string(value)

                            log_values = (
                                user_id,
                                "Registro",
                                """Registrou uma despesa de cartã
                                no valor de R$ {} associada a conta {}.
                                """.format(
                                    str_value,
                                    card
                                )
                            )
                            QueryExecutor().register_log_query(
                                log_values,
                            )

                            Receipts().generate_receipt(
                                'despesas_cartao_credito',
                                input_id,
                                description,
                                value,
                                str(date),
                                category,
                                card_id
                            )

                        else:
                            with data_expander:
                                if value > remaining_limit:
                                    st.error(
                                        body="""
                                        O valor é maior que o limite restante.
                                        """
                                        )
                                if description == "":
                                    st.error(body="A descrição está vazia.")
                                if category == "Selecione uma opção":
                                    st.error(body="Selecione uma categoria.")
                                if (
                                    inputed_credit_card_code
                                ) != credit_card_code:
                                    st.error(body="Código do cartão inválido.")

                    elif invoices_quantity == 0:
                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)
                            st.subheader(
                                body=":white_check_mark: Validação de Dados"
                                )
                            with st.expander(
                                label="Validação de Dados",
                                expanded=True
                            ):
                                st.warning(
                                    body="""
                                        Você ainda não cadastrou
                                        fechamentos de fatura para o cartão {}.
                                        """.format(card)
                                )
