import streamlit as st
from dictionary.vars import EXPENSE_CATEGORIES, TO_REMOVE_LIST
from dictionary.sql.account_queries import (
    user_current_accounts_query,
    unique_account_id_query
)
from dictionary.sql.benefited_queries import (
    beneficiaries_query,
    benefited_doc_name_query,
    benefited_quantity_query,
    choosed_benefited_id_query
)
from dictionary.sql.creditor_queries import (
    creditors_complete_data_query,
    creditor_doc_name_query,
    creditors_names_query,
    creditors_quantity_query
)
from dictionary.sql.expenses_queries import (
    insert_expense_query,
    total_account_expense_query
)
from dictionary.sql.loan_queries import (
    insert_loan_query,
    last_loan_id_query
)
from dictionary.sql.revenues_queries import (
    insert_revenue_query,
    total_account_revenue_query
)
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from functions.login import Login
from screens.reports.receipts import Receipts
from time import sleep


user_id, user_document = Login().get_user_data()


class TakeNewLoan:
    def get_user_current_accounts(self):
        """
        Consulta as contas correntes do usuário.

        Returns
        -------
        user_current_accounts: list = A lista com as contas correntes.
        """

        user_current_accounts = QueryExecutor().complex_consult_query(
            query=user_current_accounts_query,
            params=(user_id, user_document)
        )
        user_current_accounts = QueryExecutor().treat_simple_results(
            user_current_accounts,
            TO_REMOVE_LIST
        )

        return user_current_accounts

    def main_menu(self):
        """
        Coleta os dados do novo empréstimo tomado pelo cliente.
        """

        col1, col2, col3 = st.columns(3)

        user_current_accounts = self.get_user_current_accounts()

        if len(user_current_accounts) == 0:
            with col2:
                st.info(body="Você ainda não possui contas ou cartões.")

        elif len(user_current_accounts) >= 1 and (
            user_current_accounts[0] != "Selecione uma opção"
        ):

            creditors_quantity = QueryExecutor().simple_consult_query(
                query=creditors_quantity_query,
                params=(user_id, user_document)
            )

            creditors_quantity = int(QueryExecutor().treat_simple_result(
                creditors_quantity,
                TO_REMOVE_LIST
                )
            )

            if creditors_quantity == 0:
                with col2:
                    st.warning(
                        body="Você ainda não cadastrou credores.")

            elif creditors_quantity >= 1:

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):
                        id = QueryExecutor().simple_consult_query(
                            last_loan_id_query,
                            ()
                        )
                        id = QueryExecutor().treat_simple_result(
                            id,
                            TO_REMOVE_LIST
                        )
                        id = int(id) + 1

                        description = st.text_input(
                            label=":lower_left_ballpoint_pen: Descrição",
                            placeholder="Informe uma descrição",
                            help="Descrição do empréstimo tomado.",
                            max_chars=25
                        )
                        value = st.number_input(
                            label=":dollar: Valor",
                            step=0.01,
                            min_value=0.01
                        )
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(
                            label=":card_index_dividers: Categoria",
                            options=EXPENSE_CATEGORIES,
                        )
                        account = st.selectbox(
                            label=":bank: Conta",
                            options=user_current_accounts
                        )

                        creditors = QueryExecutor().complex_consult_query(
                            creditors_names_query,
                            params=(user_id, user_document)
                        )
                        creditors = (
                            QueryExecutor().treat_simple_results(
                                creditors,
                                TO_REMOVE_LIST
                            )
                        )
                        creditor = st.selectbox(
                            label="Credor",
                            options=creditors
                        )

                        creditor_name_document = (
                            QueryExecutor().complex_consult_query(
                                creditors_complete_data_query,
                                params=(user_id, user_document, creditor)
                            )
                        )
                        creditor_name_document = (
                            QueryExecutor().treat_complex_result(
                                creditor_name_document,
                                TO_REMOVE_LIST
                            )
                        )
                        creditor_name = creditor_name_document[0]
                        creditor_document = creditor_name_document[1]
                        benefited_name, benefited_document = (
                            Login().get_user_data()
                        )
                        confirm_values_check_box = st.checkbox(
                            label="Confirmar Dados"
                        )

                    generate_receipt_button = st.button(
                        label=":pencil: Gerar Comprovante",
                        key="generate_receipt_button",
                    )

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

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

                        with col2:
                            with st.spinner("Aguarde..."):
                                sleep(2.5)
                            st.subheader(
                                body=":white_check_mark: Validação de dados"
                            )

                            with st.expander(
                                label="Informações",
                                expanded=True
                            ):
                                str_selected_account_revenues = (
                                    QueryExecutor().simple_consult_query(
                                        query=total_account_revenue_query,
                                        params=(
                                            account,
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
                                            account,
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
                                    ) - (
                                        selected_account_expenses
                                    ), 2
                                )

                        if (
                            description != ""
                            ) and (
                                value >= 0.01
                            ) and (
                                date
                            ) and (
                                category != "Selecione uma opção"
                        ) and account != "Selecione uma opção":
                            with col2:
                                description = "Empréstimo - " + description
                                with st.expander(
                                    label="Informações",
                                    expanded=True
                                ):
                                    st.success(body="Dados válidos.")

                            expense_values = (
                                description,
                                value,
                                date,
                                actual_horary,
                                category,
                                account_id,
                                creditor_name,
                                creditor_document,
                                "S"
                            )
                            QueryExecutor().insert_query(
                                insert_expense_query,
                                expense_values,
                                "Despesa registrada com sucesso!",
                                "Erro ao registrar despesa:"
                            )

                            revenue_values = (
                                description,
                                value,
                                date,
                                actual_horary,
                                category,
                                account_id,
                                user_id,
                                user_document,
                                "S"
                            )
                            QueryExecutor().insert_query(
                                insert_revenue_query,
                                revenue_values,
                                "Receita registrada com sucesso!",
                                "Erro ao registrar receita:"
                            )

                            loan_values = (
                                description,
                                value,
                                0,
                                date,
                                actual_horary,
                                category,
                                account_id,
                                benefited_name,
                                benefited_document,
                                creditor_name,
                                creditor_document,
                                "N"
                            )
                            QueryExecutor().insert_query(
                                insert_loan_query,
                                loan_values,
                                "Empréstimo registrado com sucesso!",
                                "Erro ao registrar empréstimo:"
                            )
                            str_value = Variable().treat_complex_string(value)

                            log_values = (
                                user_id,
                                "Registro",
                                """Tomou um empréstimo no valor
                                de R$ {} associado a conta {}.
                                """.format(str_value, account))
                            QueryExecutor().register_log_query(
                                log_values,
                            )

                            st.subheader(
                                body=":pencil: Comprovante de Empréstimo"
                            )

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            Receipts().generate_receipt(
                                'emprestimos',
                                id,
                                description,
                                value,
                                str(date),
                                category,
                                account
                            )
                        else:
                            with st.expander(
                                label="Informações",
                                expanded=True
                            ):
                                if description == "":
                                    st.error(body="A descrição está vazia.")
                                if category == "Selecione uma opção":
                                    st.error(body="Selecione uma categoria.")
                                if value > account_available_value:
                                    st.error(
                                        body="""
                                        O valor do empréstimo não pode
                                        ser maior que o valor
                                        disponível em conta.
                                        """
                                    )

    def make_new_loan(self):
        """
        Coleta os dados do empréstimo que está sendo concedido pelo usuário.
        """

        col1, col2, col3 = st.columns(3)
        user_current_accounts = self.get_user_current_accounts()
        if len(user_current_accounts) == 0:
            with col2:
                st.info(
                    body="Você ainda não possui contas ou cartões cadastrados."
                )
        elif (
            len(user_current_accounts) >= 1
            ) and (
                user_current_accounts[0]
            ) != (
                "Selecione uma opção"
        ):

            benefited_quantity = QueryExecutor().simple_consult_query(
                query=benefited_quantity_query,
                params=(user_id, user_document)
            )
            benefited_quantity = int(QueryExecutor().treat_simple_result(
                benefited_quantity,
                TO_REMOVE_LIST
                )
            )

            if benefited_quantity == 0:
                with col2:
                    st.warning(body="Você ainda não cadastrou beneficiados.")

            elif benefited_quantity >= 1:

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):

                        id = QueryExecutor().simple_consult_brute_query(
                            last_loan_id_query
                        )
                        id = QueryExecutor().treat_simple_result(
                            id,
                            TO_REMOVE_LIST
                        )
                        id = int(id) + 1

                        description = st.text_input(
                            label=":lower_left_ballpoint_pen: Descrição",
                            placeholder="Informe uma descrição",
                            help="Descrição breve do empréstimo.",
                            max_chars=25
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
                        account = st.selectbox(
                            label=":bank: Conta",
                            options=user_current_accounts
                        )

                        beneficiaries = QueryExecutor().simple_consult_query(
                            beneficiaries_query,
                            (user_document, user_id)
                        )
                        beneficiaries = (
                            QueryExecutor().treat_numerous_simple_result(
                                beneficiaries,
                                TO_REMOVE_LIST
                            )
                        )
                        benefited = st.selectbox(
                            label="Beneficiado",
                            options=beneficiaries
                        )
                        creditor_name_document = (
                            QueryExecutor().complex_consult_query(
                                creditor_doc_name_query
                            )
                        )
                        creditor_name_document = (
                            QueryExecutor().treat_complex_result(
                                creditor_name_document,
                                TO_REMOVE_LIST
                            )
                        )
                        creditor_name = creditor_name_document[0]
                        creditor_document = creditor_name_document[1]

                        benefited_doc_name = (
                            QueryExecutor().complex_consult_query(
                                benefited_doc_name_query,
                                params=(benefited,)
                            )
                        )
                        benefited_doc_name = (
                            QueryExecutor().treat_complex_result(
                                benefited_doc_name,
                                TO_REMOVE_LIST
                            )
                        )
                        benefited_name = benefited_doc_name[0]
                        benefited_document = benefited_doc_name[1]

                        confirm_values_check_box = st.checkbox(
                            label="Confirmar Dados"
                        )

                    generate_receipt_button = st.button(
                        label=":pencil: Gerar Comprovante",
                        key="generate_receipt_button",
                    )

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

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
                        with col2:
                            with st.spinner("Aguarde..."):
                                sleep(2.5)
                            st.subheader(
                                body=":white_check_mark: Validação de dados"
                            )
                            with st.expander(
                                label="Informações",
                                expanded=True
                            ):
                                str_selected_account_revenues = (
                                    QueryExecutor().simple_consult_query(
                                        query=total_account_revenue_query,
                                        params=(
                                            account,
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
                                    (selected_account_revenues)
                                    - (selected_account_expenses),
                                    2
                                )

                        if (
                            description != ""
                            ) and (
                                value >= 0.01
                            ) and (
                                value <= account_available_value
                            ) and (
                                date
                            ) and (
                                category != "Selecione uma opção"
                            ) and (
                                account != "Selecione uma opção"
                        ):
                            with col2:
                                with st.expander(
                                    label="Informações",
                                    expanded=True
                                ):
                                    st.success(body="Dados válidos.")

                            expense_values = (
                                description,
                                value,
                                date,
                                actual_horary,
                                category,
                                account_id,
                                creditor_name,
                                creditor_document,
                                "S"
                            )
                            QueryExecutor().insert_query(
                                insert_expense_query,
                                expense_values,
                                "Despesa registrado com sucesso!",
                                "Erro ao registrar despesa:"
                            )

                            loan_values = (
                                description,
                                value,
                                0,
                                date,
                                actual_horary,
                                category,
                                account_id,
                                benefited_name,
                                benefited_document,
                                user_id,
                                creditor_document,
                                "N"
                            )
                            QueryExecutor().insert_query(
                                insert_loan_query,
                                loan_values,
                                "Empréstimo registrado com sucesso!",
                                "Erro ao registrar empréstimo:"
                            )

                            str_value = Variable().treat_complex_string(value)

                            log_values = (
                                user_id,
                                "Registro",
                                """
                                Registrou um empréstimo no valor de
                                R$ {} a partir da conta {}.
                                """.format(str_value, account))
                            QueryExecutor().register_log_query(
                                log_values,
                            )
                            st.subheader(
                                body=":pencil: Comprovante de Empréstimo")
                            with st.spinner("Aguarde..."):
                                sleep(1)
                            Receipts().generate_receipt(
                                'emprestimos',
                                id,
                                description,
                                value,
                                str(date),
                                category,
                                account
                            )

                        else:
                            with col2:
                                with st.expander(
                                    label="Informações",
                                    expanded=True
                                ):
                                    if description == "":
                                        st.error(
                                            body="A descrição está vazia."
                                        )
                                    if category == "Selecione uma opção":
                                        st.error(
                                            body="Selecione uma categoria."
                                        )
                                    if value > account_available_value:
                                        account_available_value = str(
                                            account_available_value
                                        )
                                        account_available_value = (
                                            account_available_value.replace(
                                                ".",
                                                ","
                                            )
                                        )
                                        last_two_values = (
                                            account_available_value[-2:]
                                        )
                                        if last_two_values == ",0":
                                            account_available_value = (
                                                account_available_value + "0"
                                            )
                                        st.error(
                                            body="""
                                            O valor do empréstimo não pode ser
                                            maior que o valor em conta.
                                            """
                                        )
                                        st.info(
                                            body="""
                                            Valor disponível para a conta {}:
                                            R$ {}.
                                            """.format(
                                                account,
                                                account_available_value
                                            )
                                        )


class MakeNewLoan:
    """
    Classe que representa a realização de novos empréstimos.
    """
    def get_user_current_accounts(self):
        """
        Consulta as contas correntes do usuário.

        Returns
        -------
        user_current_accounts : list
            A lista com as contas correntes do usuário.
        """

        user_current_accounts = QueryExecutor().complex_consult_query(
            query=user_current_accounts_query,
            params=(user_id, user_document)
        )
        user_current_accounts = QueryExecutor().treat_simple_results(
            user_current_accounts,
            TO_REMOVE_LIST
        )

        return user_current_accounts

    def main_menu(self):
        """
        Coleta os dados do empréstimo que está sendo concedido pelo usuário.
        """

        col1, col2, col3 = st.columns(3)

        user_current_accounts = self.get_user_current_accounts()

        if len(user_current_accounts) == 0:
            with col2:
                st.info(
                    body="""
                    Você ainda não possui contas ou cartões."""
                )

        elif (
            len(user_current_accounts) >= 1
            ) and (
                user_current_accounts[0]
                ) != "Selecione uma opção":

            benefited_quantity = QueryExecutor().simple_consult_query(
                query=benefited_quantity_query,
                params=(user_id, user_document)
            )
            benefited_quantity = int(QueryExecutor().treat_simple_result(
                benefited_quantity,
                TO_REMOVE_LIST
                )
            )

            if benefited_quantity == 0:
                with col2:
                    st.warning(body="Você ainda não cadastrou beneficiados.")

            elif benefited_quantity >= 1:

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):

                        id = QueryExecutor().simple_consult_query(
                            last_loan_id_query,
                            ()
                        )
                        id = QueryExecutor().treat_simple_result(
                            id,
                            TO_REMOVE_LIST
                        )
                        id = int(id) + 1

                        description = st.text_input(
                            label=":lower_left_ballpoint_pen: Descrição",
                            placeholder="Informe uma descrição",
                            help="Descrição breve do empréstimo.",
                            max_chars=25
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
                        account = st.selectbox(
                            label=":bank: Conta",
                            options=user_current_accounts
                        )

                        beneficiaries = QueryExecutor().complex_consult_query(
                            query=beneficiaries_query,
                            params=(user_id, user_document)
                        )
                        beneficiaries = (
                            QueryExecutor().treat_simple_results(
                                beneficiaries,
                                TO_REMOVE_LIST
                            )
                        )
                        benefited = st.selectbox(
                            label="Beneficiado",
                            options=beneficiaries
                        )

                        creditor_name_document = (
                            QueryExecutor().complex_consult_query(
                                creditor_doc_name_query,
                                params=(user_id, user_document)
                            )
                        )
                        creditor_name_document = (
                            QueryExecutor().treat_complex_result(
                                creditor_name_document,
                                TO_REMOVE_LIST
                            )
                        )
                        creditor_document = creditor_name_document[1]

                        benefited_doc_name = (
                            QueryExecutor().complex_consult_query(
                                query=benefited_doc_name_query,
                                params=(benefited,)
                            )
                        )
                        benefited_doc_name = (
                            QueryExecutor().treat_complex_result(
                                benefited_doc_name,
                                TO_REMOVE_LIST
                            )
                        )
                        benefited_name = benefited_doc_name[0]
                        benefited_document = benefited_doc_name[1]

                        confirm_values_check_box = st.checkbox(
                            label="Confirmar Dados"
                        )

                    generate_receipt_button = st.button(
                        label=":pencil: Gerar Comprovante",
                        key="generate_receipt_button",
                    )

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

                        benefited_id = QueryExecutor().simple_consult_query(
                            choosed_benefited_id_query,
                            (benefited_name, benefited_document)
                        )

                        benefited_id = QueryExecutor().treat_simple_result(
                            benefited_id,
                            TO_REMOVE_LIST
                        )
                        benefited_id = int(benefited_id)

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

                        with col2:

                            with st.spinner("Aguarde..."):
                                sleep(2.5)

                            st.subheader(
                                body=":white_check_mark: Validação de dados"
                            )

                            with st.expander(
                                label="Informações",
                                expanded=True
                            ):
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
                                        query=total_account_expense_query,
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
                                        TO_REMOVE_LIST)
                                )
                                selected_account_expenses = float(
                                    str_selected_account_expenses
                                )

                                account_available_value = round(
                                    (
                                        (selected_account_revenues)
                                        - (selected_account_expenses)
                                    ),
                                    2
                                )

                        if (
                            description != ""
                            ) and (
                                (value >= 0.01)
                            ) and (
                                value <= account_available_value
                            ) and (
                                date
                            ) and (
                                category != "Selecione uma opção"
                                ) and account != "Selecione uma opção":

                            with col2:
                                with st.expander(
                                    label="Informações",
                                    expanded=True
                                ):
                                    st.success(body="Dados válidos.")

                            expense_values = (
                                description,
                                value,
                                date,
                                actual_horary,
                                category,
                                account_id,
                                user_id,
                                creditor_document,
                                "S"
                            )
                            QueryExecutor().insert_query(
                                insert_expense_query,
                                expense_values,
                                "Despesa registrado com sucesso!",
                                "Erro ao registrar despesa:"
                            )

                            loan_values = (
                                description,
                                value,
                                0,
                                date,
                                actual_horary,
                                category,
                                account_id,
                                benefited_id,
                                benefited_document,
                                user_id,
                                creditor_document,
                                "N"
                            )
                            QueryExecutor().insert_query(
                                insert_loan_query,
                                loan_values,
                                "Empréstimo registrado com sucesso!",
                                "Erro ao registrar empréstimo:"
                            )

                            str_value = Variable().treat_complex_string(value)

                            log_values = (
                                user_id,
                                "Registro",
                                """
                                Registrou um empréstimo no valor de R$ {}
                                a partir da conta {}.
                            """.format(str_value, account)
                            )
                            QueryExecutor().register_log_query(
                                log_values,
                            )
                            st.subheader(
                                body=":pencil: Comprovante de Empréstimo"
                            )
                            with st.spinner("Aguarde..."):
                                sleep(1)

                            Receipts().generate_receipt(
                                'emprestimos',
                                id,
                                description,
                                value,
                                str(date),
                                category,
                                account
                            )

                        else:
                            with col2:
                                with st.expander(
                                    label="Informações",
                                    expanded=True
                                ):
                                    if description == "":
                                        st.error(
                                            body="A descrição está vazia."
                                        )
                                    if category == "Selecione uma opção":
                                        st.error(
                                            body="Selecione uma categoria."
                                        )
                                    if value > account_available_value:
                                        account_available_value = str(
                                            account_available_value
                                        )
                                        account_available_value = (
                                            account_available_value.replace(
                                                ".", ","
                                            )
                                        )
                                        last_two_values = (
                                            account_available_value[-2:]
                                        )
                                        if last_two_values == ",0":
                                            account_available_value = (
                                                account_available_value + "0"
                                            )
                                        st.error(
                                            body="""
                                                 O valor do empréstimo
                                                 não pode ser maior que o valor
                                                  disponível em conta.
                                                 """
                                            )
                                        st.info(
                                            body="""
                                                Valor disponível para
                                                a conta {}: R$ {}.
                                                """.format(
                                                    account,
                                                    account_available_value
                                                )
                                        )
