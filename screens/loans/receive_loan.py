import streamlit as st
import pandas as pd
from dictionary.sql.account_queries import (
    unique_account_id_query,
    user_current_accounts_query
)
from dictionary.sql.loan_queries import (
    update_loan_query,
    total_loan_actual_value_query,
    received_actual_value_query,
    receiving_max_value_query,
    not_received_loans_query
)
from dictionary.sql.revenues_queries import (
    insert_revenue_query,
    last_revenue_id_query
)
from dictionary.vars import TO_REMOVE_LIST, today
from functions.query_executor import QueryExecutor
from functions.login import Login
from functions.get_actual_time import GetActualTime
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep


user_id, user_document = Login().get_user_data()


class ReceiveLoan:
    """
    Classe que representa o recebimento de valores dos empréstimos concedidos.
    """
    def mount_not_received_loan_df(self, values: list):
        """
        Elabora e retorna o dataframe dos empréstimos não recebidos,

        Parameters
        ----------
        values : list
            A lista com os valores do dataframe.

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
                "Valor Recebido": values[3],
                "Valor a Receber": values[4],
                "Data": values[5],
                "Categoria": values[6],
                "Conta": values[7],
                "Devedor": values[8]
            }
        )
        loan_data_df["Valor Total"] = loan_data_df[
            "Valor Total"].apply(
            lambda x: f"R$ {x:.2f}".replace(".", ",")
        )
        loan_data_df["Valor Recebido"] = loan_data_df[
            "Valor Recebido"].apply(
            lambda x: f"R$ {x:.2f}".replace(".", ",")
        )
        loan_data_df["Valor a Receber"] = loan_data_df[
            "Valor a Receber"].apply(
            lambda x: f"R$ {x:.2f}".replace(".", ",")
        )
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
        Exibe os empréstimos concedidos que ainda não foram recebidos.
        """
        not_received_loans = QueryExecutor().complex_compund_query(
            query=not_received_loans_query,
            list_quantity=9,
            params=(user_id, user_document)
        )
        if len(not_received_loans[0]) >= 1:

            col4, col5, col6 = st.columns(3)

            with col4:
                loan_data_df = self.mount_not_received_loan_df(
                    not_received_loans
                )
                st.subheader(body=":computer: Entrada de Dados")
                with st.expander(label="Valores", expanded=True):
                    st.dataframe(
                        loan_data_df,
                        hide_index=True,
                        use_container_width=True
                    )
                    total_loan_value = 0
                    for i in range(0, len(not_received_loans[4])):
                        total_loan_value += not_received_loans[4][i]
                    total_loan_value = str(total_loan_value)
                    total_loan_value = total_loan_value.replace(".", ",")
                    st.info(
                        body="Valor total: :heavy_dollar_sign: {}".format(
                            total_loan_value
                        )
                    )
                    usr_accnts = QueryExecutor().complex_consult_query(
                        user_current_accounts_query,
                        params=(user_id, user_document)
                    )
                    usr_accnts = QueryExecutor().treat_simple_results(
                        usr_accnts,
                        TO_REMOVE_LIST
                    )

                    debt = st.selectbox(
                        label="Selecione a dívida",
                        options=not_received_loans[1]
                    )

                    choosed_id = self.search_loan_id(
                        not_received_loans[0],
                        not_received_loans[1],
                        debt
                    )

                    receiving_max_value = (
                        QueryExecutor().simple_consult_query(
                            receiving_max_value_query,
                            (choosed_id,)
                        )
                    )
                    receiving_max_value = (
                        QueryExecutor().treat_simple_result(
                            receiving_max_value,
                            TO_REMOVE_LIST
                        )
                    )
                    receiving_max_value = float(receiving_max_value)

                    received_actual_value = (
                        QueryExecutor().simple_consult_query(
                            received_actual_value_query,
                            (choosed_id,)
                        )
                    )
                    received_actual_value = (
                        QueryExecutor().treat_simple_result(
                            received_actual_value,
                            TO_REMOVE_LIST
                        )
                    )
                    received_actual_value = float(received_actual_value)
                    total_actual_value = (
                        QueryExecutor().simple_consult_query(
                            total_loan_actual_value_query,
                            (choosed_id, user_id, user_document)
                        )
                    )
                    total_actual_value = (
                        QueryExecutor().treat_simple_result(
                            total_actual_value,
                            TO_REMOVE_LIST
                        )
                    )
                    total_actual_value = float(total_actual_value)
                    receiving_value = st.number_input(
                        label="Valor",
                        min_value=0.00,
                        max_value=receiving_max_value,
                        step=0.01
                    )
                    selected_account = st.selectbox(
                        label="Conta",
                        options=usr_accnts
                    )
                    confirm_values = st.checkbox(label="Confirmar valores")
                receive_button = st.button(
                    label=":floppy_disk: Receber valor de empréstimo"
                )
            with col5:
                if confirm_values:
                    with st.spinner(text="Aguarde..."):
                        sleep(1.25)
                    st.subheader(
                        body=":white_check_mark: Validação de Dados"
                    )
                    if receiving_value > 0:
                        with col5:
                            with st.expander(label="Dados", expanded=True):
                                to_receive_value = (
                                    receiving_value + received_actual_value
                                )
                                str_receiving_value = (
                                        Variable().treat_complex_string(
                                            to_receive_value
                                        )
                                    )
                                st.info(
                                    body="""
                                    Valor sendo recebido:
                                    :heavy_dollar_sign: {}
                                    """.format(
                                        str_receiving_value
                                    )
                                )
                                str_to_receive_value = (
                                    Variable().treat_complex_string(
                                        to_receive_value
                                    )
                                )
                                st.info(
                                    body="""
                                    Valor recebido atualizado:
                                    :heavy_dollar_sign: {}
                                    """.format(
                                        str_to_receive_value
                                    )
                                )

                                remaining_to_receive_value = (
                                    (total_actual_value)
                                    - (receiving_value + received_actual_value)
                                )
                                str_remaining_to_receive_value = (
                                    Variable().treat_complex_string(
                                        remaining_to_receive_value
                                    )
                                )
                                st.info(
                                    body="""
                                    Valor restante a receber:
                                    :heavy_dollar_sign: {}
                                    """.format(
                                        str_remaining_to_receive_value
                                    )
                                )
                        loan_payed = 'N'
                        if remaining_to_receive_value == 0:
                            loan_payed = 'S'
                    elif receiving_value == 0:
                        with st.spinner(text="Aguarde..."):
                            sleep(1.25)
                        with col5:
                            with st.expander(label="Aviso", expanded=True):
                                st.warning(
                                    body="""
                                    O valor recebido deve ser maior do que 0.
                                    """
                                )
                if confirm_values and receive_button:
                    actual_horary = GetActualTime().get_actual_time()
                    if receiving_value > 0:
                        account_id = QueryExecutor().simple_consult_query(
                            unique_account_id_query,
                            (selected_account, user_id, user_document)
                        )
                        account_id = QueryExecutor().treat_simple_result(
                            account_id,
                            TO_REMOVE_LIST
                        )
                        account_id = int(account_id)

                        values = (
                            debt,
                            receiving_value,
                            today,
                            actual_horary,
                            'Devolução de empréstimo',
                            account_id,
                            user_id,
                            user_document,
                            'S'
                        )
                        QueryExecutor().insert_query(
                            insert_revenue_query,
                            values,
                            "Valor de empréstimo recebido com sucesso!",
                            "Erro ao receber valor do empréstimo:"
                        )

                        QueryExecutor().update_unique_register(
                            update_loan_query,
                            (
                                to_receive_value,
                                loan_payed,
                                debt,
                                'N',
                                user_id,
                                user_document
                            ),
                            "Empréstimo recebido.",
                            "Erro ao receber empréstimo:"
                        )
                        last_revenue_id = (
                            QueryExecutor().simple_consult_query(
                                last_revenue_id_query,
                                ()
                            )
                        )
                        last_revenue_id = (
                            QueryExecutor().treat_simple_result(
                                last_revenue_id,
                                TO_REMOVE_LIST
                            )
                        )
                        last_revenue_id = int(last_revenue_id)
                        with col6:
                            with st.spinner(text="Aguarde..."):
                                sleep(1.25)
                            st.subheader(
                                body="""
                                :pencil: Comprovante de Recebimento
                                """
                            )
                            str_receiving_value = (
                                Variable().treat_complex_string(
                                    not_received_loans[3]
                                )
                            )
                            Receipts().generate_receipt(
                                table="receitas",
                                id=last_revenue_id,
                                description=debt,
                                value=receiving_value,
                                date=today,
                                category='Pagamento de Empréstimo',
                                account=selected_account
                            )

                            log_values = (
                                user_id,
                                "Registro",
                                """
                                Recebeu R$ {} de um empréstimo
                                realizado na conta {}.
                                """.format(
                                    str_receiving_value,
                                    selected_account
                                )
                            )
                            QueryExecutor().register_log_query(
                                log_values,
                            )
        elif len(not_received_loans[0]) == 0:
            col4, col5, col6 = st.columns(3)
            with col5:
                st.info(body="Você não tem valores a receber.")
