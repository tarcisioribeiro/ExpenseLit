import streamlit as st
from dictionary.vars import expense_categories, to_remove_list
from dictionary.sql import last_loan_id_query, creditor_doc_name_query, user_current_accounts_query, creditors_query, total_account_revenue_query, total_account_expense_query
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from functions.login import Login
from screens.reports.receipts import Receipts
from time import sleep


class TakeNewLoan:
    def get_user_current_accounts(self):
        """
        Consulta as contas correntes do usuário.

        Returns
        -------
        user_current_accounts: list = A lista com as contas correntes do usuário.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")

        user_current_accounts = QueryExecutor().complex_consult_query(query=user_current_accounts_query, params=(user_name, user_document))
        user_current_accounts = QueryExecutor().treat_numerous_simple_result(user_current_accounts, to_remove_list)

        return user_current_accounts

    def main_menu(self):
        """
        Coleta os dados do novo empréstimo tomado pelo cliente.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col1, col2, col3 = st.columns(3)

        user_current_accounts = self.get_user_current_accounts()

        if len(user_current_accounts) == 0:
            with col2:
                st.info(body="Você ainda não possui contas ou cartões cadastrados.")

        elif len(user_current_accounts) >= 1 and user_current_accounts[0] != "Selecione uma opção":

            creditors_quantity_query = '''SELECT COUNT(id_credor) FROM credores WHERE credores.documento <> %s OR credores.nome <> %s;'''

            creditors_quantity = QueryExecutor().simple_consult_query(query=creditors_quantity_query, params=(user_document, user_name))
            creditors_quantity = int(QueryExecutor().treat_simple_result(creditors_quantity, to_remove_list))

            if creditors_quantity == 0:
                with col2:
                    st.warning(
                        body="Você ainda não cadastrou credores.")

            elif creditors_quantity >= 1:

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):
                        id = QueryExecutor().simple_consult_brute_query(last_loan_id_query)
                        id = QueryExecutor().treat_simple_result(id, to_remove_list)
                        id = int(id) + 1

                        description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição", help="Descrição do empréstimo tomado.", max_chars=25)
                        value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(label=":card_index_dividers: Categoria", options=expense_categories,)
                        account = st.selectbox(label=":bank: Conta", options=user_current_accounts)

                        creditors = QueryExecutor().complex_consult_query(creditors_query, params=(user_name, user_document))
                        creditors = QueryExecutor().treat_numerous_simple_result(creditors, to_remove_list)
                        creditor = st.selectbox(label="Credor", options=creditors)

                        creditor_doc_name_query = """
                                SELECT 
                                    credores.nome,
                                    credores.documento
                                FROM
                                    credores
                                WHERE
                                    credores.nome = %s;"""

                        creditor_name_document = QueryExecutor().complex_consult_query(creditor_doc_name_query, params=(creditor, ))
                        creditor_name_document = QueryExecutor().treat_complex_result(creditor_name_document, to_remove_list)
                        creditor_name = creditor_name_document[0]
                        creditor_document = creditor_name_document[1]
                        benefited_name, benefited_document = Login().get_user_data(return_option="user_doc_name")
                        confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                    generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button",)

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

                        actual_horary = GetActualTime().get_actual_time()

                        with col2:
                            with st.spinner("Aguarde..."):
                                sleep(2.5)
                            st.subheader(body=":white_check_mark: Validação de dados")

                            with st.expander(label="Informações", expanded=True):
                                str_selected_account_revenues = (QueryExecutor().simple_consult_query(query=total_account_revenue_query, params=(account, user_name, user_document)))
                                str_selected_account_revenues = (QueryExecutor().treat_simple_result(str_selected_account_revenues, to_remove_list))
                                selected_account_revenues = float(str_selected_account_revenues)

                                str_selected_account_expenses = (QueryExecutor().simple_consult_query(query=total_account_expense_query, params=(account, user_name, user_document)))
                                str_selected_account_expenses = (QueryExecutor().treat_simple_result(str_selected_account_expenses, to_remove_list))
                                selected_account_expenses = float(str_selected_account_expenses)

                                account_available_value = round(
                                    selected_account_revenues - selected_account_expenses, 2)

                        if description != "" and value >= 0.01 and date and category != "Selecione uma opção" and account != "Selecione uma opção":
                            with col2:
                                description = "Empréstimo - " + description

                                with st.expander(label="Informações", expanded=True):
                                    st.success(body="Dados válidos.")

                            expense_query = '''INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            expense_values = (description, value, date, actual_horary, category, account, creditor_name, creditor_document, "S")
                            QueryExecutor().insert_query(expense_query, expense_values, "Despesa registrada com sucesso!", "Erro ao registrar despesa:")

                            revenue_query = '''INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            revenue_values = (description, value, date, actual_horary, category, account, user_name, user_document, "S")
                            QueryExecutor().insert_query(revenue_query, revenue_values, "Receita registrada com sucesso!", "Erro ao registrar receita:")

                            loan_query = '''INSERT INTO emprestimos(descricao,valor,valor_pago,data,horario,categoria,conta,devedor,documento_devedor,credor,documento_credor,pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            loan_values = (description, value, 0, date, actual_horary, category, account, benefited_name, benefited_document, creditor_name, creditor_document, "N")
                            QueryExecutor().insert_query(loan_query, loan_values, "Empréstimo registrado com sucesso!", "Erro ao registrar empréstimo:")

                            str_value = Variable().treat_complex_string(value)

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Tomou um empréstimo no valor de R$ {} associado a conta {}.".format(str_value, account))
                            QueryExecutor().insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            st.subheader(body=":pencil: Comprovante de Empréstimo")

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            Receipts().generate_receipt('emprestimos', id, description, value, str(date), category, account)

                        else:
                            with st.expander(label="Informações", expanded=True):
                                if description == "":
                                    st.error(body="A descrição está vazia.")
                                if category == "Selecione uma opção":
                                    st.error(body="Selecione uma categoria.")
                                if value > account_available_value:
                                    st.error(body="O valor do empréstimo não pode ser maior que o valor disponível em conta.")

    def make_new_loan(self):
        """
        Coleta os dados do empréstimo que está sendo concedido pelo usuário.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col1, col2, col3 = st.columns(3)

        user_current_accounts = self.get_user_current_accounts()

        if len(user_current_accounts) == 0:
            with col2:
                st.info(body="Você ainda não possui contas ou cartões cadastrados.")

        elif len(user_current_accounts) >= 1 and user_current_accounts[0] != "Selecione uma opção":

            benefited_quantity_query = '''SELECT COUNT(id_beneficiado) FROM beneficiados WHERE beneficiados.documento <> %s OR beneficiados.nome <> %s;'''

            benefited_quantity = QueryExecutor().simple_consult_query(query=benefited_quantity_query, params=(user_name, user_document))
            benefited_quantity = int(QueryExecutor().treat_simple_result(benefited_quantity, to_remove_list))

            if benefited_quantity == 0:
                with col2:
                    st.warning(body="Você ainda não cadastrou beneficiados.")

            elif benefited_quantity >= 1:

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):

                        id = QueryExecutor().simple_consult_brute_query(last_loan_id_query)
                        id = QueryExecutor().treat_simple_result(id, to_remove_list)
                        id = int(id) + 1

                        description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição", help="Descrição breve do empréstimo.", max_chars=25)
                        value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(label=":card_index_dividers: Categoria", options=expense_categories,)
                        account = st.selectbox(label=":bank: Conta", options=user_current_accounts)

                        beneficiaries_query = '''SELECT nome FROM beneficiados WHERE beneficiados.documento <> {} OR beneficiados.nome <> '{}';'''.format(user_document, user_name)
                        beneficiaries = QueryExecutor().complex_consult_query(beneficiaries_query)
                        beneficiaries = QueryExecutor().treat_numerous_simple_result(beneficiaries, to_remove_list)
                        benefited = st.selectbox(label="Beneficiado", options=beneficiaries)

                        creditor_name_document = QueryExecutor().complex_consult_query(creditor_doc_name_query)
                        creditor_name_document = QueryExecutor().treat_complex_result(creditor_name_document, to_remove_list)
                        creditor_name = creditor_name_document[0]
                        creditor_document = creditor_name_document[1]

                        benefited_doc_name_query = """
                                        SELECT 
                                            beneficiados.nome,
                                            beneficiados.documento
                                        FROM
                                            beneficiados
                                        WHERE
                                            beneficiados.nome = %s;"""
                        benefited_doc_name = QueryExecutor().complex_consult_query(benefited_doc_name_query, params=(benefited, ))
                        benefited_doc_name = QueryExecutor().treat_complex_result(benefited_doc_name, to_remove_list)
                        benefited_name = benefited_doc_name[0]
                        benefited_document = benefited_doc_name[1]

                        confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                    generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button",)

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

                        actual_horary = GetActualTime().get_actual_time()

                        with col2:

                            with st.spinner("Aguarde..."):
                                sleep(2.5)

                            st.subheader(body=":white_check_mark: Validação de dados")

                            with st.expander(label="Informações", expanded=True):

                                str_selected_account_revenues = (QueryExecutor().simple_consult_query(query=total_account_revenue_query, params=(account, user_name, user_document)))
                                str_selected_account_revenues = (QueryExecutor().treat_simple_result(str_selected_account_revenues, to_remove_list))
                                selected_account_revenues = float(str_selected_account_revenues)

                                str_selected_account_expenses = (QueryExecutor().simple_consult_query(query=total_account_expense_query, params=(account, user_name, user_document)))
                                str_selected_account_expenses = (QueryExecutor().treat_simple_result(str_selected_account_expenses, to_remove_list))
                                selected_account_expenses = float(str_selected_account_expenses)

                                account_available_value = round(selected_account_revenues - selected_account_expenses, 2)

                        if description != "" and ((value >= 0.01) and (value <= account_available_value)) and date and category != "Selecione uma opção" and account != "Selecione uma opção":

                            with col2:
                                with st.expander(label="Informações", expanded=True):
                                    st.success(body="Dados válidos.")

                            expense_query = '''INSERT INTO despesas (descricao,valor,data,horario,categoria,conta,proprietario_despesa,documento_proprietario_despesa,pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            expense_values = (description, value, date, actual_horary,category, account, creditor_name, creditor_document, "S")
                            QueryExecutor().insert_query(expense_query, expense_values, "Despesa registrado com sucesso!", "Erro ao registrar despesa:")

                            loan_query = '''INSERT INTO emprestimos (descricao,valor,valor_pago,data,horario,categoria,conta,devedor,documento_devedor,credor,documento_credor, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            loan_values = (description, value, 0, date, actual_horary, category, account,benefited_name, benefited_document, creditor_name, creditor_document, "N")
                            QueryExecutor().insert_query(loan_query, loan_values, "Empréstimo registrado com sucesso!", "Erro ao registrar empréstimo:")

                            str_value = Variable().treat_complex_string(value)

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Registrou um empréstimo no valor de R$ {} a partir da conta {}.".format(str_value, account))
                            QueryExecutor().insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            st.subheader(
                                body=":pencil: Comprovante de Empréstimo")

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            Receipts().generate_receipt('emprestimos', id, description, value, str(date), category, account)

                        else:
                            with col2:
                                with st.expander(label="Informações", expanded=True):
                                    if description == "":
                                        st.error(body="A descrição está vazia.")
                                    if category == "Selecione uma opção":
                                        st.error(body="Selecione uma categoria.")
                                    if value > account_available_value:
                                        account_available_value = str(account_available_value)
                                        account_available_value = account_available_value.replace(".", ",")
                                        last_two_values = account_available_value[-2:]
                                        if last_two_values == ",0":
                                            account_available_value = account_available_value + "0"
                                        st.error(body="O valor do empréstimo não pode ser maior que o valor disponível em conta.")
                                        st.info(body="Valor disponível para a conta {}: R$ {}.".format(account, account_available_value))
                                        
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
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")

        user_current_accounts = QueryExecutor().complex_consult_query(query=user_current_accounts_query, params=(user_name, user_document))
        user_current_accounts = QueryExecutor().treat_numerous_simple_result(user_current_accounts, to_remove_list)

        return user_current_accounts

    def main_menu(self):
        """
        Coleta os dados do empréstimo que está sendo concedido pelo usuário.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col1, col2, col3 = st.columns(3)

        user_current_accounts = self.get_user_current_accounts()

        if len(user_current_accounts) == 0:
            with col2:
                st.info(body="Você ainda não possui contas ou cartões cadastrados.")

        elif len(user_current_accounts) >= 1 and user_current_accounts[0] != "Selecione uma opção":

            benefited_quantity_query = '''SELECT COUNT(id_beneficiado) FROM beneficiados WHERE beneficiados.documento <> %s OR beneficiados.nome <> %s;'''

            benefited_quantity = QueryExecutor().simple_consult_query(query=benefited_quantity_query, params=(user_name, user_document))
            benefited_quantity = int(QueryExecutor().treat_simple_result(benefited_quantity, to_remove_list))

            if benefited_quantity == 0:
                with col2:
                    st.warning(body="Você ainda não cadastrou beneficiados.")

            elif benefited_quantity >= 1:

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):

                        id = QueryExecutor().simple_consult_brute_query(last_loan_id_query)
                        id = QueryExecutor().treat_simple_result(id, to_remove_list)
                        id = int(id) + 1

                        description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição", help="Descrição breve do empréstimo.", max_chars=25)
                        value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(label=":card_index_dividers: Categoria", options=expense_categories,)
                        account = st.selectbox(label=":bank: Conta", options=user_current_accounts)

                        beneficiaries_query = '''SELECT nome FROM beneficiados WHERE beneficiados.documento <> %s OR beneficiados.nome <> %s;'''
                        beneficiaries = QueryExecutor().complex_consult_query(query=beneficiaries_query, params=(user_document, user_name))
                        beneficiaries = QueryExecutor().treat_numerous_simple_result(beneficiaries, to_remove_list)
                        benefited = st.selectbox(label="Beneficiado", options=beneficiaries)

                        creditor_name_document = QueryExecutor().complex_consult_query(creditor_doc_name_query, params=(user_name, user_document))
                        creditor_name_document = QueryExecutor().treat_complex_result(creditor_name_document, to_remove_list)
                        creditor_name = creditor_name_document[0]
                        creditor_document = creditor_name_document[1]

                        benefited_doc_name_query = """
                                        SELECT 
                                            beneficiados.nome,
                                            beneficiados.documento
                                        FROM
                                            beneficiados
                                        WHERE
                                            beneficiados.nome = %s;"""
                        benefited_doc_name = QueryExecutor().complex_consult_query(query=benefited_doc_name_query, params=(benefited,))
                        benefited_doc_name = QueryExecutor().treat_complex_result(benefited_doc_name, to_remove_list)
                        benefited_name = benefited_doc_name[0]
                        benefited_document = benefited_doc_name[1]

                        confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                    generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button",)

                with col3:
                    if confirm_values_check_box and generate_receipt_button:

                        actual_horary = GetActualTime().get_actual_time()

                        with col2:

                            with st.spinner("Aguarde..."):
                                sleep(2.5)

                            st.subheader(body=":white_check_mark: Validação de dados")

                            with st.expander(label="Informações", expanded=True):

                                str_selected_account_revenues = (QueryExecutor().simple_consult_query(query=total_account_revenue_query, params=(account, user_name, user_document)))
                                str_selected_account_revenues = (QueryExecutor().treat_simple_result(str_selected_account_revenues, to_remove_list))
                                selected_account_revenues = float(str_selected_account_revenues)

                                str_selected_account_expenses = (QueryExecutor().simple_consult_query(query=total_account_expense_query, params=(account, user_name, user_document)))
                                str_selected_account_expenses = (QueryExecutor().treat_simple_result(str_selected_account_expenses, to_remove_list))
                                selected_account_expenses = float(str_selected_account_expenses)

                                account_available_value = round(selected_account_revenues - selected_account_expenses, 2)

                        if description != "" and ((value >= 0.01) and (value <= account_available_value)) and date and category != "Selecione uma opção" and account != "Selecione uma opção":

                            with col2:
                                with st.expander(label="Informações", expanded=True):
                                    st.success(body="Dados válidos.")

                            expense_query = '''INSERT INTO despesas (descricao,valor,data,horario,categoria,conta,proprietario_despesa,documento_proprietario_despesa,pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            expense_values = (description, value, date, actual_horary, category, account, creditor_name, creditor_document, "S")
                            QueryExecutor().insert_query(expense_query, expense_values, "Despesa registrado com sucesso!", "Erro ao registrar despesa:")

                            loan_query = '''INSERT INTO emprestimos (descricao,valor,valor_pago,data,horario,categoria,conta,devedor,documento_devedor,credor,documento_credor, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            loan_values = (description, value, 0, date, actual_horary, category, account, benefited_name, benefited_document, creditor_name, creditor_document, "N")
                            QueryExecutor().insert_query(loan_query, loan_values, "Empréstimo registrado com sucesso!", "Erro ao registrar empréstimo:")

                            str_value = Variable().treat_complex_string(value)

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Registrou um empréstimo no valor de R$ {} a partir da conta {}.".format(str_value, account))
                            QueryExecutor().insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            st.subheader(body=":pencil: Comprovante de Empréstimo")

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            Receipts().generate_receipt('emprestimos', id, description, value, str(date), category, account)

                        else:
                            with col2:
                                with st.expander(label="Informações", expanded=True):
                                    if description == "":
                                        st.error(body="A descrição está vazia.")
                                    if category == "Selecione uma opção":
                                        st.error(body="Selecione uma categoria.")
                                    if value > account_available_value:
                                        account_available_value = str(account_available_value)
                                        account_available_value = account_available_value.replace(".", ",")
                                        last_two_values = account_available_value[-2:]
                                        if last_two_values == ",0":
                                            account_available_value = account_available_value + "0"
                                        st.error(body="O valor do empréstimo não pode ser maior que o valor disponível em conta.")
                                        st.info(body="Valor disponível para a conta {}: R$ {}.".format(account, account_available_value))
