import streamlit as st
from data.cache.session_state import logged_user, logged_user_password
from dictionary.sql import last_expense_id_query, user_current_accounts_query, total_account_revenue_query, total_account_expense_query
from dictionary.user_stats import user_name, user_document
from dictionary.vars import to_remove_list, expense_categories, decimal_values
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from screens.reports.receipts import Receipts
from time import sleep


class NewCurrentExpense:
    def __init__(self):

        call_time = GetActualTime()
        query_executor = QueryExecutor()
        receipt_executor = Receipts()

        def new_expense():     

            user_current_accounts = query_executor.complex_consult_query(user_current_accounts_query)
            user_current_accounts = query_executor.treat_numerous_simple_result(user_current_accounts, to_remove_list)

            col1, col2, col3 = st.columns(3)

            if len(user_current_accounts) == 0:

                with col2:
                    st.info(body="Você ainda não possui contas cadastradas.")

            elif len(user_current_accounts) >= 1 and user_current_accounts[0] != "Selecione uma opção":

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados", expanded=True):

                        id = query_executor.simple_consult_query(last_expense_id_query)
                        id = query_executor.treat_simple_result(id, to_remove_list)

                        options = {
                            "Sim": "S",
                            "Não": "N"
                        }

                        id = int(id) + 1
                        description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição")
                        value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(label=":card_index_dividers: Categoria", options=expense_categories)
                        account = st.selectbox(label=":bank: Conta", options=user_current_accounts)
                        payed = st.selectbox(label=":outbox_tray: Pago", options=options.keys())

                        confirm_values_check_box = st.checkbox(label="Confirmar dados")

                        total_account_revenue_complete_query = total_account_revenue_query.format(account, logged_user, logged_user_password)
                        total_account_expense_complete_query = total_account_expense_query.format(account, logged_user, logged_user_password)
                        
                    generate_receipt_button = st.button(label=":pencil: Gerar Comprovante", key="generate_receipt_button")                    

                with col3:
                    
                    if confirm_values_check_box and generate_receipt_button:

                        payed = options[payed]

                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)

                            st.subheader(body=":white_check_mark: Validação de Dados")

                            data_validation_expander = st.expander(label="Informações", expanded=True)


                            with data_validation_expander:

                                str_selected_account_revenues = query_executor.simple_consult_query(total_account_revenue_complete_query)
                                str_selected_account_revenues = query_executor.treat_simple_result(str_selected_account_revenues, to_remove_list)
                                selected_account_revenues = float(str_selected_account_revenues)

                                str_selected_account_expenses = query_executor.simple_consult_query(total_account_expense_complete_query)
                                str_selected_account_expenses = query_executor.treat_simple_result(str_selected_account_expenses, to_remove_list)
                                selected_account_expenses = float(str_selected_account_expenses)

                                account_available_value = round(selected_account_revenues - selected_account_expenses, 2)
                                available_value = str(account_available_value)
                                available_value = available_value.replace(".", ",")
                                last_two_digits = available_value[-2:]
                                if last_two_digits in decimal_values:
                                    available_value = available_value + "0"


                        with data_validation_expander:
                            st.info(body="Valor disponível da conta {}: R$ {}".format(account, available_value))

                        if description != "" and value <= account_available_value and category != "Selecione uma opção":
                            with data_validation_expander:
                                st.success(body="Dados Válidos.")

                            actual_horary = call_time.get_actual_time()                      
                            expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            values = (description, value, date, actual_horary, category, account, user_name, user_document, payed)
                            query_executor.insert_query(expense_query, values, "Despesa registrada com sucesso!", "Erro ao registrar despesa:")

                            str_value = str(value)
                            str_value = str_value.replace(".", ",")
                            last_two_digits = str_value[-2:]
                            if last_two_digits in decimal_values:
                                str_value = str_value + "0"

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Registrou uma despesa no valor de R$ {} associada a conta {}.".format(str_value, account))
                            query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            st.subheader(body=":pencil: Comprovante de Despesa")

                            with st.spinner("Aguarde..."):
                                sleep(2.5)

                            receipt_executor.generate_receipt('despesas', id, description, value, str(date), category, account)

                        else:
                            with data_validation_expander:
                                if description == "":
                                    st.error(body="A descrição está vazia.")
                                if category == "Selecione uma opção":
                                    st.error(body="Selecione uma categoria.")
                                if value > account_available_value:
                                    st.error(body="O valor da despesa não pode ser maior que o valor disponível em conta.")

        self.main_menu = new_expense
