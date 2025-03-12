import streamlit as st
from dictionary.vars import transfer_categories, to_remove_list
from dictionary.sql import last_transfer_id_query, user_current_accounts_query, total_account_revenue_query, total_account_expense_query, user_fund_accounts_query
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep


class NewTransfer:
    """
    Classe responsável pela realização de transferências entre contas.
    """

    def new_fund_account_transfer(self):
        """
        Realiza a coleta dos dados da transferência do fundo de garantia e a insere no banco de dados.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col4, col5, col6 = st.columns(3)

        user_fund_accounts = QueryExecutor().complex_consult_query(query=user_fund_accounts_query, params=(user_name, user_document))
        user_fund_accounts = QueryExecutor().treat_numerous_simple_result(user_fund_accounts, to_remove_list)

        user_current_accounts = QueryExecutor().complex_consult_query(query=user_current_accounts_query, params=(user_name, user_document))
        user_current_accounts = QueryExecutor().treat_numerous_simple_result(user_current_accounts, to_remove_list)

        if len(user_fund_accounts) == 0 and len(user_current_accounts) == 0:
            with col5:
                st.info(body="Você ainda não possui contas correntes e contas de fundo de garantia cadastradas.")
        if len(user_current_accounts) == 0:
            with col5:
                st.info(body="Você ainda não possui contas correntes cadastradas.")
        if len(user_fund_accounts) == 0:
            with col5:
                st.info(body="Você ainda não possui contas de fundo de garantia cadastradas.")
        elif len(user_fund_accounts) >= 1 and len(user_current_accounts) >= 1:

            with col4:
                st.subheader(body=":computer: Entrada de Dados")

                to_treat_id = QueryExecutor().simple_consult_brute_query(last_transfer_id_query)
                id = (int(QueryExecutor().treat_simple_result(to_treat_id, to_remove_list)) + 1)

                options = {
                    "Sim": "S",
                    "Não": "N"
                }

                with st.expander(label="Dados", expanded=True):
                    description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição", help="Descrição breve da transferência.", max_chars=50)
                    value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(label=":card_index_dividers: Categoria", options=transfer_categories)
                    origin_account = st.selectbox(label=":bank: Conta de Origem", options=user_fund_accounts)
                    destiny_account = st.selectbox(label=":bank: Conta de Destino", options=user_current_accounts)
                    transfered = st.selectbox(label=":inbox_tray: Transferido", options=options.keys())

                    confirm_values_check_box = st.checkbox(label="Confirmar dados")

                generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button")

            with col6:
                if confirm_values_check_box and generate_receipt_button:
                    transfered = options[transfered]
                    with col5:
                        with st.spinner("Aguarde..."):
                            sleep(2.5)
                        st.subheader(body=":white_check_mark: Validação de dados")
                        data_validation_expander = st.expander(label="Informações", expanded=True)

                        with data_validation_expander:
                            str_selected_account_revenues = QueryExecutor().simple_consult_query(query=total_account_revenue_query, params=(origin_account, user_name, user_document))
                            str_selected_account_revenues = QueryExecutor().treat_simple_result(str_selected_account_revenues, to_remove_list)
                            selected_account_revenues = float(str_selected_account_revenues)

                            str_selected_account_expenses = QueryExecutor().simple_consult_query(query=total_account_expense_query, params=(origin_account, user_name, user_document))
                            str_selected_account_expenses = QueryExecutor().treat_simple_result(str_selected_account_expenses, to_remove_list)
                            selected_account_expenses = float(str_selected_account_expenses)

                            account_available_value = round(selected_account_revenues - selected_account_expenses, 2)
                            str_account_available_value = Variable().treat_complex_string(account_available_value)

                    with data_validation_expander:
                        st.info(body="Saldo disponível da conta de origem: R$ {}".format(str_account_available_value))

                    if description != "" and value <= account_available_value and category != "Selecione uma opção" and destiny_account != origin_account:
                        with data_validation_expander:
                            st.success(body="Dados Válidos.")

                        actual_horary = GetActualTime().get_actual_time()
                        revenue_owner_name, revenue_owner_document = Login().get_user_data(return_option="user_doc_name")

                        transfer_query = "INSERT INTO transferencias (descricao, valor, data, horario, categoria, conta_origem, conta_destino, proprietario_transferencia, documento_proprietario_transferencia, transferido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

                        transfer_values = (description, value, date, actual_horary, category, origin_account, destiny_account, revenue_owner_name, revenue_owner_document, transfered)
                        expense_values = (description, value, date, actual_horary, category, origin_account, revenue_owner_name, revenue_owner_document, transfered)
                        revenue_values = (description, value, date, actual_horary, category, destiny_account, revenue_owner_name, revenue_owner_document, transfered)
                        QueryExecutor().insert_query(transfer_query, transfer_values, "Transferência registrada com sucesso!", "Erro ao registrar transferência:",)
                        QueryExecutor().insert_query(expense_query, expense_values, "Despesa registrada com sucesso!", "Erro ao registrar despesa:")
                        QueryExecutor().insert_query(revenue_query, revenue_values, "Receita registrada com sucesso!", "Erro ao registrar receita:")

                        str_value = Variable().treat_complex_string(value)

                        log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                        log_values = (logged_user, "Registro", "Registrou uma transferência no valor de R$ {} da conta {} para a conta {}.".format(str_value, origin_account, destiny_account))
                        QueryExecutor().insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                        st.subheader(body=":pencil: Comprovante de Transferência")

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        Receipts().generate_transfer_receipt(id, description, value, date, category, origin_account, destiny_account)

                    elif description == "" or value > account_available_value or category == "Selecione uma opção" or destiny_account == origin_account:
                        with data_validation_expander:
                            if description == "":
                                st.error(body="A descrição está vazia.")
                            if value > account_available_value:
                                st.error(body="O valor da transferência não pode exceder o valor disponível da conta de origem.")
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
                            if origin_account == destiny_account:
                                st.error(body="A conta de origem e a conta de destino não podem ser a mesma.")

                elif confirm_values_check_box == False and generate_receipt_button:
                    with col5:
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        st.subheader(body=":white_check_mark: Validação de Dados")
                        with st.expander(label="Aviso", expanded=True):
                            st.warning(body="Confirme os dados antes de prosseguir.")

    def new_current_account_transfer(self):
        """
        Coleta os dados da nova transferência e a insere no banco de dados.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col4, col5, col6 = st.columns(3)

        user_current_accounts = QueryExecutor().complex_consult_query(query=user_current_accounts_query, params=(user_name, user_document))
        user_current_accounts = QueryExecutor().treat_numerous_simple_result(user_current_accounts, to_remove_list)

        if len(user_current_accounts) == 0:
            with col5:
                st.info(body="Você ainda não possui contas cadastradas.")
        elif len(user_current_accounts) == 1:
            with col5:
                st.info(body="Você ainda não possui outra conta cadastrada para realizar transferências.")
        elif len(user_current_accounts) >= 2:

            with col4:
                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados", expanded=True):
                    to_treat_id = QueryExecutor().simple_consult_brute_query(last_transfer_id_query)
                    id = (int(QueryExecutor().treat_simple_result(to_treat_id, to_remove_list)) + 1)

                    options = {
                        "Sim": "S",
                        "Não": "N"
                    }

                    description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição", help="Descrição breve da transferência.", max_chars=50)
                    value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(label=":card_index_dividers: Categoria", options=transfer_categories)
                    origin_account = st.selectbox(label=":bank: Conta de Origem", options=user_current_accounts)
                    destiny_account = st.selectbox(label=":bank: Conta de Destino", options=user_current_accounts)
                    transfered = st.selectbox(label=":inbox_tray: Transferido", options=options)

                    confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button")

            with col6:
                if confirm_values_check_box and generate_receipt_button:
                    transfered = options[transfered]
                    with col5:
                        with st.spinner("Aguarde..."):
                            sleep(2.5)
                        st.subheader(body=":white_check_mark: Validação de dados")
                        data_validation_expander = st.expander(label="Informações", expanded=True)

                        with data_validation_expander:
                            str_selected_account_revenues = QueryExecutor().simple_consult_query(query=total_account_revenue_query, params=(origin_account, user_name, user_document))
                            str_selected_account_revenues = QueryExecutor().treat_simple_result(str_selected_account_revenues, to_remove_list)
                            selected_account_revenues = float(str_selected_account_revenues)

                            str_selected_account_expenses = QueryExecutor().simple_consult_query(query=total_account_expense_query, params=(origin_account, user_name, user_document))
                            str_selected_account_expenses = QueryExecutor().treat_simple_result(str_selected_account_expenses, to_remove_list)
                            selected_account_expenses = float(str_selected_account_expenses)

                            account_available_value = round(selected_account_revenues - selected_account_expenses, 2)
                            str_account_available_value = Variable().treat_complex_string(account_available_value)

                    with data_validation_expander:
                        st.info(body="Saldo disponível da conta de origem: R$ {}".format(str_account_available_value))

                    if description != "" and value <= account_available_value and category != "Selecione uma opção" and destiny_account != origin_account:
                        with data_validation_expander:
                            st.success(body="Dados Válidos.")

                        actual_horary = GetActualTime().get_actual_time()
                        revenue_owner_name, revenue_owner_document = Login().get_user_data(return_option="user_doc_name")

                        transfer_query = "INSERT INTO transferencias (descricao, valor, data, horario, categoria, conta_origem, conta_destino, proprietario_transferencia, documento_proprietario_transferencia, transferido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

                        transfer_values = (description, value, date, actual_horary, category, origin_account, destiny_account, revenue_owner_name, revenue_owner_document, transfered)
                        expense_values = (description, value, date, actual_horary, category, origin_account, revenue_owner_name, revenue_owner_document, transfered)
                        revenue_values = (description, value, date, actual_horary, category, destiny_account, revenue_owner_name, revenue_owner_document, transfered)
                        QueryExecutor().insert_query(transfer_query, transfer_values, "Transferência registrada com sucesso!", "Erro ao registrar transferência:",)
                        QueryExecutor().insert_query(expense_query, expense_values, "Despesa registrada com sucesso!", "Erro ao registrar despesa:")
                        QueryExecutor().insert_query(revenue_query, revenue_values, "Receita registrada com sucesso!", "Erro ao registrar receita:")

                        str_value = Variable().treat_complex_string(value)

                        log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                        log_values = (logged_user, "Registro", "Registrou uma transferência no valor de R$ {} da conta {} para a conta {}.".format(str_value, origin_account, destiny_account))
                        QueryExecutor().insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                        st.subheader(body=":pencil: Comprovante de Transferência")

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        Receipts().generate_transfer_receipt(id, description, value, date, category, origin_account, destiny_account)

                    elif description == "" or value > account_available_value or category == "Selecione uma opção" or destiny_account == origin_account:
                        with data_validation_expander:
                            if description == "":
                                st.error(body="A descrição está vazia.")
                            if value > account_available_value:
                                st.error(body="O valor da transferência não pode exceder o valor disponível da conta de origem.")
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
                            if origin_account == destiny_account:
                                st.error(body="A conta de origem e a conta de destino não podem ser a mesma.")

                elif confirm_values_check_box == False and generate_receipt_button:
                    with col5:
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        st.subheader(body=":white_check_mark: Validação de Dados")
                        with st.expander(label="Aviso", expanded=True):
                            st.warning(body="Confirme os dados antes de prosseguir.")

    def main_menu(self):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.header(body=":currency_exchange: Nova Transferência")

        menu_options = {
            "Transferência entre Contas Correntes": self.new_current_account_transfer,
            "Transferência de Fundo de Garantia": self.new_fund_account_transfer
        }

        with col2:
            selected_option = st.selectbox(label="Menu", options=menu_options.keys())

        st.divider()

        if selected_option:
            selected_option = menu_options[selected_option]
            selected_option()
