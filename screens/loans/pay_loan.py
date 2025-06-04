import streamlit as st
import pandas as pd
from dictionary.sql.account_queries import (
    unique_account_id_query,
    user_current_accounts_query
)
from dictionary.sql.expenses_queries import (
    insert_expense_query,
    last_expense_id_query
)
from dictionary.sql.loan_queries import update_debt_query
from dictionary.sql.loan_queries import (
    not_payed_loans_query,
    payed_actual_value_query,
    paying_max_value_query,
    total_actual_value_query
)
from dictionary.vars import TO_REMOVE_LIST, today
from functions.query_executor import QueryExecutor
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep


user_id, user_document = Login().get_user_data()


class PayLoan:
    """
    Classe que representa o pagamento dos empréstimos tomados pelo usuário.
    """
    def mount_loan_df(self, values: list):
        """
        Elabora o dataframe dos empréstimos não pagos.

        Parameters
        ----------
        values : list
            A lista com os valores a serem exibidos.
        Returns
        -------
        loan_data_df : DataFrame
            O dataframe elaborado.
        """

        loan_data_df = pd.DataFrame(
            {
                "ID": values[0],
                "Descrição": values[1],
                "Valor Total": values[2],
                "Valor Pago": values[3],
                "Valor a Pagar": values[4],
                "Data": values[5],
                "Categoria": values[6],
                "Conta": values[7],
                "Credor": values[8]
            }
        )

        loan_data_df["Valor Total"] = loan_data_df[
            "Valor Total"
        ].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
        loan_data_df["Valor Pago"] = loan_data_df[
            "Valor Pago"
        ].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
        loan_data_df["Valor a Pagar"] = loan_data_df[
            "Valor a Pagar"
        ].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
        loan_data_df["Data"] = pd.to_datetime(
            loan_data_df["Data"]
        ).dt.strftime("%d/%m/%Y")

        return loan_data_df

    def search_loan_id(
        self,
        id_list: list,
        description_list: list,
        option: str
    ):
        """
        Procura o ID da opção escolhida, retornando o número do ID.

        Parameters
        ----------
        id_list : list
            A lista dos id's.
        description_list : list
            A lista com as descrições.

        Returns
        -------
        choosed_id : int
            O id correspondente a opção.
        """
        aux_id = None

        for i in range(0, len(description_list)):
            if description_list[i] == option:
                aux_id = int(id_list[i])
            else:
                pass

        return aux_id

    def main_menu(self):
        """
        Exibe os empréstimos tomados pelo usuário.
        """

        not_payed_loans = QueryExecutor().complex_compund_query(
            query=not_payed_loans_query,
            list_quantity=9,
            params=(user_id, user_document)
        )

        if len(not_payed_loans[0]) >= 1:

            col4, col5, col6 = st.columns(3)

            with col4:

                loan_data_df = self.mount_loan_df(not_payed_loans)

                st.subheader(body=":computer: Entrada de Dados")
                with st.expander(label="Valores", expanded=True):
                    st.dataframe(
                        loan_data_df,
                        hide_index=True,
                        use_container_width=True
                    )
                    total_loan_value = 0
                    for i in range(0, len(not_payed_loans[4])):
                        total_loan_value += not_payed_loans[4][i]
                    total_loan_value = str(total_loan_value)
                    total_loan_value = total_loan_value.replace(".", ",")
                    st.info(body="Valor total: :heavy_dollar_sign: {}".format(
                        total_loan_value
                        )
                    )
                    user_accounts = QueryExecutor().complex_consult_query(
                        user_current_accounts_query,
                        params=(user_id, user_document)
                    )
                    user_accounts = (
                        QueryExecutor().treat_simple_results(
                            user_accounts,
                            TO_REMOVE_LIST
                        )
                    )
                    debt = st.selectbox(
                        label="Selecionar dívida", options=not_payed_loans[1]
                    )

                    choosed_id = self.search_loan_id(
                        not_payed_loans[0],
                        not_payed_loans[1],
                        debt
                    )

                    paying_max_value = (
                        QueryExecutor().simple_consult_query(
                            paying_max_value_query,
                            (choosed_id,)
                        )
                    )
                    paying_max_value = (
                        QueryExecutor().treat_simple_result(
                            paying_max_value, TO_REMOVE_LIST
                        )
                    )
                    paying_max_value = float(paying_max_value)

                    payed_actual_value = (
                        QueryExecutor().simple_consult_query(
                            payed_actual_value_query,
                            (choosed_id,)
                        )
                    )
                    payed_actual_value = (
                        QueryExecutor().treat_simple_result(
                            payed_actual_value, TO_REMOVE_LIST
                        )
                    )
                    payed_actual_value = float(payed_actual_value)
                    total_actual_value = (
                        QueryExecutor().simple_consult_query(
                            total_actual_value_query,
                            (choosed_id,)
                        )
                    )
                    total_actual_value = (
                        QueryExecutor().treat_simple_result(
                            total_actual_value, TO_REMOVE_LIST
                        )
                    )
                    total_actual_value = float(total_actual_value)

                    paying_value = st.number_input(
                        label="Valor",
                        min_value=0.00,
                        max_value=paying_max_value,
                        step=0.01
                    )
                    selected_account = st.selectbox(
                        label="Conta",
                        options=user_accounts
                    )
                    confirm_values = st.checkbox(label="Confirmar valores")

                pay_button = st.button(
                    label=":floppy_disk: Pagar valor de empréstimo"
                )
            with col5:
                if confirm_values:
                    with st.spinner(text="Aguarde..."):
                        sleep(1.25)
                    st.subheader(body=":white_check_mark: Validação de Dados")
                    if paying_value > 0:
                        with col5:
                            with st.expander(label="Dados", expanded=True):
                                to_pay_value = (
                                    paying_value + payed_actual_value
                                )
                                str_paying_value = (
                                    Variable().treat_complex_string(
                                        paying_value
                                    )
                                )
                                st.info(
                                    body="""
                                    Valor sendo pago: :heavy_dollar_sign: {}
                                    """.format(str_paying_value))
                                str_to_pay_value = (
                                    Variable().treat_complex_string(
                                        to_pay_value
                                    )
                                )
                                st.info(
                                    body="""
                                    Valor pago atualizado:
                                     :heavy_dollar_sign: {}
                                    """.format(str_to_pay_value)
                                )

                                remaining_to_pay_value = total_actual_value - \
                                    (paying_value + payed_actual_value)

                                str_remaining_to_pay_value = (
                                    Variable().treat_complex_string(
                                        remaining_to_pay_value
                                    )
                                )

                                st.info(
                                    body="""
                                        Valor restante a pagar:
                                         :heavy_dollar_sign: {}
                                        """.format(str_remaining_to_pay_value)
                                )
                        loan_payed = 'N'
                        if remaining_to_pay_value == 0:
                            loan_payed = 'S'
                    elif paying_value == 0:
                        with st.spinner(text="Aguarde..."):
                            sleep(1.25)
                        with col5:
                            with st.expander(label="Aviso", expanded=True):
                                st.warning(
                                    body="""
                                        O valor pago precisa ser
                                        maior do que 0.
                                        """
                                    )
                if confirm_values and pay_button:
                    selected_account_id = QueryExecutor().simple_consult_query(
                        unique_account_id_query,
                        (selected_account, user_id, user_document)
                    )
                    selected_account_id = QueryExecutor().treat_simple_result(
                        selected_account_id,
                        TO_REMOVE_LIST
                    )

                    actual_horary = GetActualTime().get_actual_time()
                    if paying_value > 0:

                        values = (
                            debt,
                            paying_value,
                            today,
                            actual_horary,
                            'Taxas',
                            selected_account_id,
                            user_id,
                            user_document,
                            'S'
                        )

                        QueryExecutor().insert_query(
                            insert_expense_query,
                            values,
                            "Valor de empréstimo pago com sucesso!",
                            "Erro ao pagar valor do empréstimo:"
                        )
                        update_loan_values = (
                            to_pay_value,
                            loan_payed,
                            debt,
                            'N',
                            user_id,
                            user_document
                        )
                        QueryExecutor().update_unique_register(
                            update_debt_query,
                            update_loan_values,
                            "Empréstimo pago.",
                            "Erro ao pagar empréstimo:"
                        )
                        last_expense_id = (
                            QueryExecutor().simple_consult_query(
                                last_expense_id_query,
                                ()
                            )
                        )
                        last_expense_id = (
                            QueryExecutor().treat_simple_result(
                                last_expense_id,
                                TO_REMOVE_LIST
                            )
                        )
                        last_expense_id = int(last_expense_id)
                        with col6:
                            with st.spinner(text="Aguarde..."):
                                sleep(1.25)
                            st.subheader(
                                body="""
                                    :pencil: Comprovante de
                                    Pagamento de Empréstimo
                                """
                            )
                            Receipts().generate_receipt(
                                table="despesas",
                                id=last_expense_id,
                                description=debt,
                                value=paying_value,
                                date=today,
                                category='Pagamento de Empréstimo',
                                account=selected_account
                            )

                            log_values = (
                                user_id,
                                "Registro",
                                """Pagou R$ {} de um empréstimo
                                tomado na conta {}.
                                """.format(str_paying_value, selected_account))
                            QueryExecutor().register_log_query(
                                log_values,
                            )
        elif len(not_payed_loans[0]) == 0:
            col4, col5, col6 = st.columns(3)
            with col5:
                st.info(body="Você não tem valores a pagar.")
