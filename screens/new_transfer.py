import streamlit as st
from dictionary.sql.account_queries import (
    user_fund_accounts_query,
    unique_account_id_query,
    user_current_accounts_query
)
from dictionary.sql.expenses_queries import (
    insert_expense_query,
    total_account_expense_query
)
from dictionary.sql.revenues_queries import (
    insert_revenue_query,
    total_account_revenue_query
)
from dictionary.sql.transfer_queries import (
    last_transfer_id_query,
    insert_transfer_query,
)
from dictionary.vars import TRANSFER_CATEGORIES, TO_REMOVE_LIST
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep


user_id, user_document = Login().get_user_data()


class NewTransfer:
    """
    Classe responsável pela realização de transferências entre contas.
    """

    def new_fund_account_transfer(self):
        """
        Realiza a coleta dos dados da transferência do fundo de garantia.
        """

        col4, col5, col6 = st.columns(3)

        user_fund_accounts = QueryExecutor().complex_consult_query(
            query=user_fund_accounts_query,
            params=(user_id, user_document)
        )
        user_fund_accounts = QueryExecutor().treat_simple_results(
            user_fund_accounts,
            TO_REMOVE_LIST
        )
        user_current_accounts = QueryExecutor().complex_consult_query(
            query=user_current_accounts_query,
            params=(user_id, user_document)
        )
        user_current_accounts = QueryExecutor().treat_simple_results(
            user_current_accounts,
            TO_REMOVE_LIST
        )
        if len(user_fund_accounts) == 0 and len(user_current_accounts) == 0:
            with col5:
                st.info(
                    body="""
                    Você ainda não possui contas correntes e
                    contas de fundo de garantia.
                    """
                )
        elif len(user_current_accounts) == 0:
            with col5:
                st.info(
                    body="Você ainda não possui contas correntes.")
        elif len(user_fund_accounts) == 0:
            with col5:
                st.info(
                    body="Você ainda não possui contas de fundo de garantia."
                )
        elif len(user_fund_accounts) >= 1 and len(user_current_accounts) >= 1:

            with col4:
                st.subheader(body=":computer: Entrada de Dados")

                to_treat_id = QueryExecutor().simple_consult_query(
                    last_transfer_id_query,
                    ()
                )
                id = (
                        int(
                            QueryExecutor().treat_simple_result(
                                to_treat_id,
                                TO_REMOVE_LIST
                            )
                        ) + 1
                )

                options = {
                    "Sim": "S",
                    "Não": "N"
                }

                with st.expander(label="Dados", expanded=True):
                    description = st.text_input(
                        label=":lower_left_ballpoint_pen: Descrição",
                        placeholder="Informe uma descrição",
                        help="Descrição breve da transferência.",
                        max_chars=50
                    )
                    value = st.number_input(
                        label=":dollar: Valor",
                        step=0.01,
                        min_value=0.01
                    )
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(
                        label=":card_index_dividers: Categoria",
                        options=TRANSFER_CATEGORIES
                    )
                    origin_account = st.selectbox(
                        label=":bank: Conta de Origem",
                        options=user_fund_accounts
                    )
                    destiny_account = st.selectbox(
                        label=":bank: Conta de Destino",
                        options=user_current_accounts
                    )
                    transfered = st.selectbox(
                        label=":inbox_tray: Transferido",
                        options=options.keys()
                    )

                    confirm_values_check_box = st.checkbox(
                        label="Confirmar dados"
                    )

                generate_receipt_button = st.button(
                    label=":pencil: Gerar Comprovante",
                    key="generate_receipt_button"
                )

            with col6:
                if confirm_values_check_box and generate_receipt_button:
                    transfered = options[transfered]
                    with col5:
                        with st.spinner("Aguarde..."):
                            sleep(2.5)
                        st.subheader(
                            body=":white_check_mark: Validação de dados"
                        )
                        data_validation_expander = st.expander(
                            label="Informações",
                            expanded=True
                        )

                        with data_validation_expander:
                            origin_account_id = (
                                QueryExecutor().simple_consult_query(
                                    query=unique_account_id_query,
                                    params=(
                                        origin_account,
                                        user_id,
                                        user_document
                                    )
                                )
                            )
                            origin_account_id = (
                                QueryExecutor().treat_simple_result(
                                    origin_account_id,
                                    TO_REMOVE_LIST
                                )
                            )
                            destiny_account_id = (
                                QueryExecutor().simple_consult_query(
                                    query=unique_account_id_query,
                                    params=(
                                        destiny_account,
                                        user_id,
                                        user_document
                                    )
                                )
                            )
                            destiny_account_id = (
                                QueryExecutor().treat_simple_result(
                                    destiny_account_id,
                                    TO_REMOVE_LIST
                                )
                            )
                            str_selected_account_revenues = (
                                QueryExecutor().simple_consult_query(
                                    query=total_account_revenue_query,
                                    params=(
                                        origin_account_id,
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
                                    query=total_account_expense_query,
                                    params=(
                                        origin_account_id,
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
                            str_account_available_value = (
                                Variable().treat_complex_string(
                                    account_available_value
                                )
                            )

                    with data_validation_expander:
                        st.info(
                            body="""
                            Saldo disponível da conta de origem: R$ {}
                            """.format(str_account_available_value)
                        )

                    if (
                        description != ""
                        ) and (
                            value <= account_available_value
                        ) and (
                            category != "Selecione uma opção"
                        ) and (
                            destiny_account != origin_account
                    ):
                        with data_validation_expander:
                            st.success(body="Dados Válidos.")

                        actual_horary = GetActualTime().get_actual_time()
                        revenue_owner_name, revenue_owner_document = (
                            Login().get_user_data()
                        )

                        transfer_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            origin_account_id,
                            destiny_account_id,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered
                        )
                        expense_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            origin_account_id,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered
                        )
                        revenue_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            destiny_account_id,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered
                        )
                        QueryExecutor().insert_query(
                            insert_transfer_query,
                            transfer_values,
                            "Transferência registrada com sucesso!",
                            "Erro ao registrar transferência:",
                        )
                        QueryExecutor().insert_query(
                            insert_expense_query,
                            expense_values,
                            "Despesa registrada com sucesso!",
                            "Erro ao registrar despesa:"
                        )
                        QueryExecutor().insert_query(
                            insert_revenue_query,
                            revenue_values,
                            "Receita registrada com sucesso!",
                            "Erro ao registrar receita:"
                        )

                        str_value = Variable().treat_complex_string(value)

                        log_values = (
                            user_id,
                            "Registro",
                            """Registrou uma transferência no valor de R$ {}
                            da conta {} para a conta {}.
                            """.format(
                                str_value,
                                origin_account,
                                destiny_account
                            )
                        )
                        QueryExecutor().register_log_query(
                            log_values,
                        )

                        st.subheader(
                            body=":pencil: Comprovante de Transferência"
                        )

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        Receipts().generate_transfer_receipt(
                            id,
                            description,
                            value,
                            date,
                            category,
                            origin_account,
                            destiny_account
                        )

                    elif (
                        description == ""
                        ) or (
                            value > account_available_value
                        ) or (
                            category == "Selecione uma opção"
                        ) or (
                            destiny_account == origin_account
                    ):
                        with data_validation_expander:
                            if description == "":
                                st.error(body="A descrição está vazia.")
                            if value > account_available_value:
                                st.error(
                                    body="""
                                    O valor da transferência não pode exceder
                                    o valor disponível da conta de origem.
                                    """
                                )
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
                            if origin_account == destiny_account:
                                st.error(
                                    body="""
                                    A conta de origem e a conta de destino
                                    não podem ser a mesma.
                                    """
                                )

                elif (
                    confirm_values_check_box is False
                    ) and (
                        generate_receipt_button
                ):
                    with col5:
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        st.subheader(
                            body=":white_check_mark: Validação de Dados"
                        )
                        with st.expander(label="Aviso", expanded=True):
                            st.warning(
                                body="Confirme os dados antes de prosseguir."
                            )

    def new_current_account_transfer(self):
        """
        Coleta os dados da nova transferência e a insere no banco de dados.
        """

        col4, col5, col6 = st.columns(3)

        user_current_accounts = QueryExecutor().complex_consult_query(
            query=user_current_accounts_query,
            params=(user_id, user_document)
        )
        user_current_accounts = QueryExecutor().treat_simple_results(
            user_current_accounts,
            TO_REMOVE_LIST
        )

        if len(user_current_accounts) == 0:
            with col5:
                st.info(body="Você ainda não possui contas cadastradas.")
        elif len(user_current_accounts) == 1:
            with col5:
                st.info(
                    body="Você ainda não possui outra conta cadastrada."
                )
        elif len(user_current_accounts) >= 2:

            with col4:
                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados", expanded=True):
                    to_treat_id = QueryExecutor().simple_consult_query(
                        last_transfer_id_query,
                        ()
                    )
                    id = (
                            int(
                                QueryExecutor().treat_simple_result(
                                    to_treat_id,
                                    TO_REMOVE_LIST
                                )
                            ) + 1
                    )

                    options = {
                        "Sim": "S",
                        "Não": "N"
                    }

                    description = st.text_input(
                        label=":lower_left_ballpoint_pen: Descrição",
                        placeholder="Informe uma descrição",
                        help="Descrição breve da transferência.",
                        max_chars=50
                    )
                    value = st.number_input(
                        label=":dollar: Valor",
                        step=0.01,
                        min_value=0.01
                    )
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(
                        label=":card_index_dividers: Categoria",
                        options=TRANSFER_CATEGORIES
                    )
                    origin_account = st.selectbox(
                        label=":bank: Conta de Origem",
                        options=user_current_accounts
                    )
                    destiny_account = st.selectbox(
                        label=":bank: Conta de Destino",
                        options=user_current_accounts
                    )
                    transfered = st.selectbox(
                        label=":inbox_tray: Transferido",
                        options=options
                    )

                    confirm_values_check_box = st.checkbox(
                        label="Confirmar Dados"
                    )

                generate_receipt_button = st.button(
                    label=":pencil: Gerar Comprovante",
                    key="generate_receipt_button"
                )

            with col6:
                if confirm_values_check_box and generate_receipt_button:
                    transfered = options[transfered]
                    with col5:
                        with st.spinner("Aguarde..."):
                            sleep(2.5)
                        st.subheader(
                            body=":white_check_mark: Validação de dados"
                        )
                        data_validation_expander = st.expander(
                            label="Informações",
                            expanded=True
                        )

                        origin_account_id = (
                            QueryExecutor().simple_consult_query(
                                query=unique_account_id_query,
                                params=(
                                    origin_account,
                                    user_id,
                                    user_document
                                )
                            )
                        )
                        origin_account_id = (
                            QueryExecutor().treat_simple_result(
                                origin_account_id,
                                TO_REMOVE_LIST
                            )
                        )

                        destiny_account_id = (
                            QueryExecutor().simple_consult_query(
                                query=unique_account_id_query,
                                params=(
                                    destiny_account,
                                    user_id,
                                    user_document
                                )
                            )
                        )
                        destiny_account_id = (
                            QueryExecutor().treat_simple_result(
                                destiny_account_id,
                                TO_REMOVE_LIST
                            )
                        )

                        with data_validation_expander:
                            str_selected_account_revenues = (
                                QueryExecutor().simple_consult_query(
                                    query=total_account_revenue_query,
                                    params=(
                                        origin_account_id,
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
                                    query=total_account_expense_query,
                                    params=(
                                        origin_account,
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
                            str_account_available_value = (
                                Variable().treat_complex_string(
                                    account_available_value
                                )
                            )

                    with data_validation_expander:
                        st.info(
                            body="""
                            Saldo disponível da conta de origem: R$ {}
                            """.format(str_account_available_value))

                    if (
                        description != ""
                        ) and (
                            value <= account_available_value
                        ) and (
                            category != "Selecione uma opção"
                        ) and (
                            destiny_account != origin_account
                    ):
                        with data_validation_expander:
                            st.success(body="Dados Válidos.")

                        actual_horary = GetActualTime().get_actual_time()
                        revenue_owner_name, revenue_owner_document = (
                            Login().get_user_data()
                        )

                        transfer_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            origin_account_id,
                            destiny_account_id,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered
                        )
                        expense_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            origin_account_id,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered
                        )
                        revenue_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            destiny_account_id,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered
                        )
                        QueryExecutor().insert_query(
                            insert_transfer_query,
                            transfer_values,
                            "Transferência registrada com sucesso!",
                            "Erro ao registrar transferência:",
                        )
                        QueryExecutor().insert_query(
                            insert_expense_query,
                            expense_values,
                            "Despesa registrada com sucesso!",
                            "Erro ao registrar despesa:"
                        )
                        QueryExecutor().insert_query(
                            insert_revenue_query,
                            revenue_values,
                            "Receita registrada com sucesso!",
                            "Erro ao registrar receita:"
                        )

                        str_value = Variable().treat_complex_string(value)

                        log_values = (
                            user_id,
                            "Registro",
                            """
                            Registrou uma transferência no valor de R$ {}
                            da conta {} para a conta {}.
                            """.format(
                                str_value,
                                origin_account,
                                destiny_account
                            )
                        )
                        QueryExecutor().register_log_query(
                            log_values,
                        )

                        st.subheader(
                            body=":pencil: Comprovante de Transferência"
                        )

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        Receipts().generate_transfer_receipt(
                            id,
                            description,
                            value,
                            date,
                            category,
                            origin_account,
                            destiny_account
                        )

                    elif (
                        description == ""
                        ) or (
                            value > account_available_value
                        ) or (
                            category == "Selecione uma opção"
                        ) or (
                            destiny_account == origin_account
                    ):
                        with data_validation_expander:
                            if description == "":
                                st.error(body="A descrição está vazia.")
                            if value > account_available_value:
                                st.error(
                                    body="""
                                    O valor da transferência não pode exceder
                                    o valor disponível da conta de origem."""
                                    )
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
                            if origin_account == destiny_account:
                                st.error(
                                    body="""A conta de origem
                                    e a conta de destino não podem ser a mesma.
                                    """
                                )

                elif (
                    confirm_values_check_box is False
                    ) and (
                        generate_receipt_button
                ):
                    with col5:
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        st.subheader(
                            body=":white_check_mark: Validação de Dados"
                        )
                        with st.expander(label="Aviso", expanded=True):
                            st.warning(
                                body="Confirme os dados antes de prosseguir."
                            )

    def main_menu(self):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.header(body=":currency_exchange: Nova Transferência")

        menu_options = {
            "Transferência entre Contas Correntes": (
                self.new_current_account_transfer
            ),
            "Transferência de Fundo de Garantia": (
                self.new_fund_account_transfer
            )
        }

        with col2:
            selected_option = st.selectbox(
                label="Menu",
                options=menu_options.keys()
            )

        st.divider()

        if selected_option:
            selected_option = menu_options[selected_option]
            selected_option()
