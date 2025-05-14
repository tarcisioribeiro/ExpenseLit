from dictionary.sql.account_queries import (
    unique_account_id_query,
    user_fund_accounts_query
)
from dictionary.sql.revenues_queries import (
    insert_revenue_query,
    last_revenue_id_query
)
from dictionary.vars import TO_REMOVE_LIST
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep
import streamlit as st


user_id, user_document = Login().get_user_data()


class NewFundRevenue:
    """
    Classe que representa o cadastro de uma nova receita de fundo de garantia.
    """

    def get_user_fund_accounts(self):
        """
        Consulta as contas de fundo de garantia do usuário.

        Returns
        -------
        user_fund_accounts : list
            A lista com as contas de fundo de garantia do usuário.
        """

        user_fund_accounts = QueryExecutor().complex_consult_query(
            query=user_fund_accounts_query,
            params=(user_id, user_document)
        )
        user_fund_accounts = QueryExecutor().treat_simple_results(
            user_fund_accounts,
            TO_REMOVE_LIST
        )
        return user_fund_accounts

    def main_menu(self):
        """
        Coleta os dados da nova receita de fundo de garantia.
        """

        user_fund_accounts = self.get_user_fund_accounts()

        col4, col5, col6 = st.columns(3)

        if len(user_fund_accounts) == 0:
            with col5:
                st.info(body="Você não possui fundos de garantia cadastrados.")

        elif len(user_fund_accounts) >= 1:

            with col4:

                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados", expanded=True):
                    id = QueryExecutor().simple_consult_query(
                        last_revenue_id_query,
                        ()
                    )
                    id = QueryExecutor().treat_simple_result(
                        id,
                        TO_REMOVE_LIST
                    )
                    id = int(id) + 1

                    options = {
                        "Sim": "S",
                        "Não": "N"
                    }

                    description = st.text_input(
                        label=":lower_left_ballpoint_pen: Descrição",
                        placeholder="Informe uma descrição",
                        key="new_fund_description",
                        help="Descrição breve da receita.",
                        max_chars=25
                    )
                    value = st.number_input(
                        label=":dollar: Valor",
                        min_value=0.01
                    )
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(
                        label=":card_index_dividers: Categoria",
                        options=["Depósito", "Rendimentos"]
                    )
                    account = st.selectbox(
                        label=":bank: Conta",
                        options=user_fund_accounts
                    )
                    received = st.selectbox(
                        label=":inbox_tray: Recebido",
                        options=options.keys()
                    )

                    confirm_values_check_box = st.checkbox(
                        label="Confirmar Dados"
                    )

            send_revenue_button = st.button(
                label=":pencil: Gerar Comprovante",
                key="send_revenue_button"
            )

            with col6:
                if send_revenue_button and confirm_values_check_box:

                    received = options[received]

                    with col5:

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        st.subheader(body="Validação de Dados")

                        data_validation_expander = st.expander(
                            label="Informações",
                            expanded=True
                        )

                    if (
                        description != ""
                        and value >= 0.01
                        and date != ""
                    ):

                        with data_validation_expander:
                            st.success(body="Dados válidos.")

                        account_id = QueryExecutor().simple_consult_query(
                            unique_account_id_query,
                            (account, user_id, user_document)
                        )
                        account_id = QueryExecutor().treat_simple_result(
                            account_id,
                            TO_REMOVE_LIST
                        )
                        account_id = int(account_id)

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
                            received,
                        )
                        QueryExecutor().insert_query(
                            insert_revenue_query,
                            values,
                            "Receita registrada com sucesso!",
                            "Erro ao registrar receita:"
                        )

                        str_value = Variable().treat_complex_string(value)

                        log_values = (
                            user_id,
                            "Registro",
                            """Registrou uma receita no valor de R$ {}
                            associada a conta {}.""".format(
                                str_value,
                                account
                            )
                        )
                        QueryExecutor().register_log_query(
                            log_values,
                        )

                        st.subheader(body=":pencil: Comprovante de Receita")

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        Receipts().generate_receipt(
                            'receitas',
                            id,
                            description,
                            value,
                            str(date),
                            category,
                            account
                        )

                    else:
                        with data_validation_expander:
                            if description == '':
                                st.error(body="A descrição está vazia.")
