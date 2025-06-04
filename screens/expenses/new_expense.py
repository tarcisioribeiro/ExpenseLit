import streamlit as st
from dictionary.sql.account_queries import (
    user_current_accounts_query,
    unique_account_id_query
)
from dictionary.sql.expenses_queries import (
    last_expense_id_query,
    total_account_expense_query,
    insert_expense_query
)
from dictionary.sql.revenues_queries import (
    total_account_revenue_query
)
from dictionary.vars import EXPENSE_CATEGORIES, TO_REMOVE_LIST
from functions.login import Login
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep


user_id, user_document = Login().get_user_data()


class NewCurrentExpense:
    """
    Classe que representa uma nova despesa em contas correntes.
    """

    def main_menu(self):
        """
        Obtém os dados de uma nova despesa em conta corrente.
        """

        user_current_accounts = QueryExecutor().complex_consult_query(
            query=user_current_accounts_query,
            params=(user_id, user_document)
        )
        user_current_accounts = QueryExecutor().treat_simple_results(
            user_current_accounts,
            TO_REMOVE_LIST
        )

        col1, col2, col3 = st.columns(3)

        if len(user_current_accounts) == 0:

            with col2:
                st.info(body="Você ainda não possui contas cadastradas.")

        elif (
            len(user_current_accounts) >= 1
            ) and (
                user_current_accounts[0] != "Selecione uma opção"
        ):
            with col1:
                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados", expanded=True):

                    id = QueryExecutor().simple_consult_query(
                        last_expense_id_query,
                        ()
                    )
                    id = QueryExecutor().treat_simple_result(
                        id,
                        TO_REMOVE_LIST
                    )

                    options = {
                        "Sim": "S",
                        "Não": "N"
                    }

                    id = int(id) + 1
                    description = st.text_input(
                        label=":lower_left_ballpoint_pen: Descrição",
                        placeholder="Informe uma descrição",
                        max_chars=25,
                        help="Descrição simples para a despesa."
                    )
                    value = st.number_input(
                        label=":dollar: Valor", step=0.01, min_value=0.01)
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(
                        label=":card_index_dividers: Categoria",
                        options=EXPENSE_CATEGORIES
                    )
                    account = st.selectbox(
                        label=":bank: Conta", options=user_current_accounts
                    )
                    payed = st.selectbox(
                        label=":outbox_tray: Pago", options=options.keys()
                    )
                    confirm_values_check_box = st.checkbox(
                        label="Confirmar dados"
                    )

                generate_receipt_button = st.button(
                    label=":pencil: Gerar Comprovante",
                    key="generate_receipt_button"
                )

            with col3:

                if confirm_values_check_box and generate_receipt_button:

                    payed = options[payed]

                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(1.25)

                        st.subheader(
                            body=":white_check_mark: Validação de Dados")

                        data_validation_expander = st.expander(
                            label="Informações", expanded=True
                        )

                        with data_validation_expander:

                            account_id = QueryExecutor().simple_consult_query(
                                unique_account_id_query,
                                (
                                    account,
                                    user_id,
                                    user_document
                                )
                            )

                            account_id = QueryExecutor().treat_simple_result(
                                account_id,
                                TO_REMOVE_LIST
                            )

                            str_selected_account_revenues = (
                                QueryExecutor().simple_consult_query(
                                    query=total_account_revenue_query,
                                    params=(
                                        account_id,
                                        user_id,
                                        user_document
                                    )
                                )
                            )
                            str_selected_account_revenues = (
                                QueryExecutor().treat_simple_result(
                                    str_selected_account_revenues,
                                    TO_REMOVE_LIST
                                )
                            )
                            selected_account_revenues = float(
                                str_selected_account_revenues
                            )

                            str_selected_account_expenses = (
                                QueryExecutor().simple_consult_query(
                                    total_account_expense_query,
                                    params=(
                                        account_id,
                                        user_id,
                                        user_document
                                    )
                                )
                            )
                            str_selected_account_expenses = (
                                QueryExecutor().treat_simple_result(
                                    str_selected_account_expenses,
                                    TO_REMOVE_LIST
                                )
                            )
                            selected_account_expenses = float(
                                str_selected_account_expenses
                            )

                            account_available_value = round(
                                (
                                    selected_account_revenues
                                ) - selected_account_expenses, 2
                            )
                            available_value = Variable().treat_complex_string(
                                account_available_value
                            )

                    with data_validation_expander:
                        st.info(
                            body="""
                            Valor disponível da conta {}: R$ {}
                            """.format(account, available_value)
                        )

                    if (
                        description != ""
                        ) and (
                            value <= account_available_value
                        ) and (
                            category != "Selecione uma opção"
                    ):
                        with data_validation_expander:
                            st.success(body="Dados Válidos.")

                        actual_horary = GetActualTime().get_actual_time()

                        values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            account_id,
                            user_id,
                            user_document,
                            payed
                        )
                        QueryExecutor().insert_query(
                            insert_expense_query,
                            values,
                            "Despesa registrada com sucesso!",
                            "Erro ao registrar despesa:"
                        )

                        str_value = Variable().treat_complex_string(value)

                        log_values = (
                            user_id,
                            "Registro",
                            """Registrou uma despesa no valor de R$ {}
                            associada a conta {}.
                        """.format(str_value, account))
                        QueryExecutor().register_log_query(
                            log_values,
                        )

                        with st.spinner("Aguarde..."):
                            sleep(1.25)

                        if payed == "S":
                            st.subheader(
                                body=":pencil: Comprovante de Despesa"
                            )
                            Receipts().generate_receipt(
                                'despesas',
                                id,
                                description,
                                value,
                                str(date),
                                category,
                                account
                            )

                    else:
                        with data_validation_expander:
                            if description == "":
                                st.error(body="A descrição está vazia.")
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
                            if value > account_available_value:
                                st.error(
                                    body="""
                                    O valor da despesa não pode ser maior que
                                    o valor disponível em conta.
                                    """
                                )
