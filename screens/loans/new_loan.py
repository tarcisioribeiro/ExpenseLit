import streamlit as st
from data.cache.session_state import logged_user, logged_user_password
from dictionary.vars import expense_categories, to_remove_list
from dictionary.sql import last_loan_id_query, beneficiaries_query, creditor_doc_name_query, user_current_accounts_query, creditors_query, doc_name_query, total_account_revenue_query, total_account_expense_query
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from screens.reports.receipts import Receipts
from time import sleep


class NewLoan:
    def __init__(self):

        query_executor = QueryExecutor()
        receipt_executor = Receipts()
        call_time = GetActualTime()

        col1, col2, col3 = st.columns(3)

        user_current_accounts = query_executor.complex_consult_query(user_current_accounts_query)
        user_current_accounts = query_executor.treat_numerous_simple_result(user_current_accounts, to_remove_list)

        def take_new_loan():

            if len(user_current_accounts) == 0:
                with col2:
                    st.info(body="Você ainda não possui contas ou cartões cadastrados.")

            elif (
                len(user_current_accounts) >= 1
                and user_current_accounts[0] != "Selecione uma opção"
            ):
                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):
                        id = query_executor.simple_consult_query(last_loan_id_query)
                        id = query_executor.treat_simple_result(id, to_remove_list)
                        id = int(id) + 1

                        description = st.text_input(label=":lower_left_ballpoint_pen: Descrição",placeholder="Informe uma descrição")
                        value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(label=":card_index_dividers: Categoria", options=expense_categories,)
                        account = st.selectbox(label=":bank: Conta", options=user_current_accounts)

                        total_account_revenue_query.format(
                            account, logged_user, logged_user_password
                        )

                        total_account_expense_query: str = """
                                    SELECT 
                                        CAST(SUM(despesas.valor) AS DECIMAL (10, 2))
                                    FROM
                                        despesas
                                            INNER JOIN
                                        usuarios ON despesas.proprietario_despesa = usuarios.nome
                                            AND despesas.documento_proprietario_despesa = usuarios.cpf
                                    WHERE
                                        despesas.pago = 'S'
                                            AND despesas.conta = '{}'
                                            AND usuarios.login = '{}'
                                            AND usuarios.senha = '{}';"""
                        total_account_expense_query.format(
                            account, logged_user, logged_user_password
                        )

                        creditors = query_executor.complex_consult_query(creditors_query)
                        creditors = query_executor.treat_numerous_simple_result(creditors, to_remove_list)
                        creditor = st.selectbox(label="Credor", options=creditors)

                        creditor_doc_name_query = """
                            SELECT 
                                credores.nome,
                                credores.cpf_cnpj
                            FROM
                                credores
                            WHERE
                                credores.nome = '{}';""".format(creditor)

                        creditor_name_document = query_executor.complex_consult_query(creditor_doc_name_query)
                        creditor_name_document = query_executor.treat_complex_result(creditor_name_document, to_remove_list)
                        creditor_name = creditor_name_document[0]
                        creditor_document = creditor_name_document[1]

                        benefited_doc_name = query_executor.complex_consult_query(doc_name_query)
                        benefited_doc_name = query_executor.treat_complex_result(benefited_doc_name, to_remove_list)
                        benefited_name = benefited_doc_name[0]
                        benefited_document = benefited_doc_name[1]

                        confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                    generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button",)

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

                        actual_horary = call_time.get_actual_time()

                        with col2:
                            with st.spinner("Aguarde..."):
                                sleep(1)
                            st.subheader(body="Validação de Dados")

                            data_validation_expander = st.expander(label="Informações", expanded=True)

                            with data_validation_expander:
                                str_selected_account_revenues = (query_executor.simple_consult_query(total_account_revenue_query))
                                str_selected_account_revenues = (query_executor.treat_simple_result(str_selected_account_revenues, to_remove_list))
                                selected_account_revenues = float(str_selected_account_revenues)

                                str_selected_account_expenses = (query_executor.simple_consult_query(total_account_expense_query))
                                str_selected_account_expenses = (query_executor.treat_simple_result(str_selected_account_expenses, to_remove_list))
                                selected_account_expenses = float(str_selected_account_expenses)

                                account_available_value = round(selected_account_revenues - selected_account_expenses, 2)

                        if (
                            description != ""
                            and value >= 0.01
                            and date
                            and category != "Selecione uma opção"
                            and account != "Selecione uma opção"
                        ):
                            with data_validation_expander:
                                st.success(body="Dados válidos.")

                            expense_query = '''INSERT
                                                INTO
                                                despesas (descricao,
                                                valor,
                                                data,
                                                horario,
                                                categoria,
                                                conta,
                                                proprietario_despesa,
                                                documento_proprietario_despesa,
                                                pago)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            
                            expense_values = (
                                description,
                                value,
                                date,
                                actual_horary,
                                category,
                                account,
                                creditor_name,
                                creditor_document,
                                "S",
                            )

                            query_executor.insert_query(expense_query, expense_values, "Despesa registrado com sucesso!", "Erro ao registrar despesa:")

                            loan_query = '''INSERT INTO 
                                                emprestimos
                                                (descricao,
                                                valor,
                                                valor_pago,
                                                data,
                                                horario,
                                                categoria,
                                                conta,
                                                devedor,
                                                documento_devedor,
                                                credor,
                                                documento_credor,
                                                pago) 
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            
                            loan_values = (
                                description,
                                value,
                                0,
                                date,
                                actual_horary,
                                category,
                                account,
                                benefited_name,
                                benefited_document,
                                creditor_name,
                                creditor_document,
                                "N",
                            )

                            query_executor.insert_query(loan_query, loan_values, "Empréstimo registrado com sucesso!", "Erro ao registrar empréstimo:")

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Tomou um empréstimo no valor de R$ {} associado a conta {}.".format(value, account))
                            query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            st.subheader(body=":pencil: Comprovante de empréstimo")

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            receipt_executor.generate_receipt('emprestimos', id, description, value, str(date), category, account)

                        else:
                            with data_validation_expander:
                                if description == "":
                                    st.error(body="A descrição está vazia.")
                                if category == "Selecione uma opção":
                                    st.error(body="Selecione uma categoria.")
                                if value > account_available_value:
                                    st.error(
                                        body="O valor do empréstimo não pode ser maior que o valor disponível em conta."
                                    )

        def make_new_loan():

            if len(user_current_accounts) == 0:
                with col2:
                    st.info(
                        body="Você ainda não possui contas ou cartões cadastrados.")

            elif (
                len(user_current_accounts) >= 1
                and user_current_accounts[0] != "Selecione uma opção"
            ):
                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):

                        id = query_executor.simple_consult_query(
                            last_loan_id_query)
                        id = query_executor.treat_simple_result(
                            id, to_remove_list)
                        id = int(id) + 1

                        description = st.text_input(
                            label=":lower_left_ballpoint_pen: Descrição",
                            placeholder="Informe uma descrição",
                        )
                        value = st.number_input(
                            label=":dollar: Valor", step=0.01, min_value=0.01
                        )
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(
                            label=":card_index_dividers: Categoria",
                            options=expense_categories,
                        )
                        account = st.selectbox(
                            label=":bank: Conta", options=user_current_accounts
                        )

                        total_account_revenue_query: str = """
                                    SELECT 
                                        CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 ))
                                    FROM
                                        receitas
                                            INNER JOIN
                                        usuarios ON receitas.proprietario_receita = usuarios.nome
                                            AND receitas.documento_proprietario_receita = usuarios.cpf
                                    WHERE
                                        receitas.recebido = 'S'
                                            AND receitas.conta = '{}'
                                            AND usuarios.login = '{}'
                                            AND usuarios.senha = '{}';""".format(
                            account, logged_user, logged_user_password
                        )

                        total_account_expense_query: str = """
                                    SELECT 
                                        CAST(SUM(despesas.valor) AS DECIMAL (10 , 2 ))
                                    FROM
                                        despesas
                                            INNER JOIN
                                        usuarios ON despesas.proprietario_despesa = usuarios.nome
                                            AND despesas.documento_proprietario_despesa = usuarios.cpf
                                    WHERE
                                        despesas.pago = 'S'
                                            AND despesas.conta = '{}'
                                            AND usuarios.login = '{}'
                                            AND usuarios.senha = '{}';""".format(
                            account, logged_user, logged_user_password
                        )

                        beneficiaries = query_executor.complex_consult_query(beneficiaries_query)
                        beneficiaries = query_executor.treat_numerous_simple_result(beneficiaries, to_remove_list)
                        benefited = st.selectbox(label="Beneficiado", options=beneficiaries)

                        creditor_name_document = query_executor.complex_consult_query(creditor_doc_name_query)
                        creditor_name_document = query_executor.treat_complex_result(creditor_name_document, to_remove_list)
                        creditor_name = creditor_name_document[0]
                        creditor_document = creditor_name_document[1]

                        benefited_doc_name_query = """
                                    SELECT 
                                        beneficiados.nome,
                                        beneficiados.cpf_cnpj
                                    FROM
                                        beneficiados
                                    WHERE
                                        beneficiados.nome = '{}';""".format(benefited)
                        benefited_doc_name = query_executor.complex_consult_query(benefited_doc_name_query)
                        benefited_doc_name = query_executor.treat_complex_result(benefited_doc_name, to_remove_list)
                        benefited_name = benefited_doc_name[0]
                        benefited_document = benefited_doc_name[1]

                        confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                    generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button",)

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

                        actual_horary = call_time.get_actual_time()

                        with col2:

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            st.subheader(body="Validação de Dados")

                            data_validation_expander = st.expander(label="Informações", expanded=True)

                            with data_validation_expander:
                                str_selected_account_revenues = (query_executor.simple_consult_query(total_account_revenue_query))
                                str_selected_account_revenues = (query_executor.treat_simple_result(str_selected_account_revenues, to_remove_list))
                                selected_account_revenues = float(str_selected_account_revenues)

                                str_selected_account_expenses = (query_executor.simple_consult_query(total_account_expense_query))
                                str_selected_account_expenses = (query_executor.treat_simple_result(str_selected_account_expenses, to_remove_list))
                                selected_account_expenses = float(str_selected_account_expenses)

                                account_available_value = round(selected_account_revenues - selected_account_expenses, 2)

                        if (
                            description != ""
                            and value >= 0.01
                            and date
                            and category != "Selecione uma opção"
                            and account != "Selecione uma opção"
                        ):
                            with data_validation_expander:
                                st.success(body="Dados válidos.")

                            expense_query = '''INSERT
                                                INTO
                                                despesas (descricao,
                                                valor,
                                                data,
                                                horario,
                                                categoria,
                                                conta,
                                                proprietario_despesa,
                                                documento_proprietario_despesa,
                                                pago)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            
                            expense_values = (
                                description,
                                value,
                                date,
                                actual_horary,
                                category,
                                account,
                                creditor_name,
                                creditor_document,
                                "S",
                            )

                            query_executor.insert_query(expense_query, expense_values, "Despesa registrado com sucesso!", "Erro ao registrar despesa:")

                            loan_query = '''INSERT INTO 
                                                emprestimos (descricao,
                                                valor,
                                                valor_pago,
                                                data,
                                                horario,
                                                categoria,
                                                conta,
                                                devedor,
                                                documento_devedor,
                                                credor,
                                                documento_credor, pago) 
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            
                            loan_values = (
                                description,
                                value,
                                0,
                                date,
                                actual_horary,
                                category,
                                account,
                                benefited_name,
                                benefited_document,
                                creditor_name,
                                creditor_document,
                                "N",
                            )

                            query_executor.insert_query(loan_query, loan_values, "Empréstimo registrado com sucesso!", "Erro ao registrar empréstimo:")

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Registrou um empréstimo no valor de R$ {} a partir da conta {}.".format(value, account))
                            query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            st.subheader(body=":pencil: Comprovante de empréstimo")

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            receipt_executor.generate_receipt('emprestimos', id, description, value, str(date), category, account)

                        else:
                            with data_validation_expander:
                                if description == "":
                                    st.error(body="A descrição está vazia.")
                                if category == "Selecione uma opção":
                                    st.error(body="Selecione uma categoria.")
                                if value > account_available_value:
                                    st.error(
                                        body="O valor do empréstimo não pode ser maior que o valor disponível em conta."
                                    )

        self.make_loan = make_new_loan
        self.take_loan = take_new_loan
