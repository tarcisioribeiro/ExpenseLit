from data.cache.session_state import logged_user
from dictionary.vars import accounts, accounts_type, today, actual_horary, to_remove_list
from dictionary.sql import user_all_current_accounts_query
from dictionary.user_stats import user_name, user_document
from functions.query_executor import QueryExecutor
import streamlit as st


class UpdateAccounts:

    def __init__(self):
        
        query_executor = QueryExecutor()

        col1, col2, col3 = st.columns(3)

        def get_new_account():

            with col1:

                with st.expander(label="Dados cadastrais", expanded=True):
                    
                    account_name = st.selectbox(label="Nome da conta", options=accounts)
                    account_type = st.selectbox(label="Tipo da conta", options=accounts_type)
                    get_account_first_value = st.number_input(label="Valor inicial", step=0.01, min_value=0.01)
                    confirm_values_ckecbox = st.checkbox(label="Confirmar Dados")

                register_account = st.button(label=":floppy_disk: Registrar Conta")

                if confirm_values_ckecbox and register_account:
                    insert_account_query = """INSERT INTO contas (nome_conta, tipo_conta, proprietario_conta, documento_proprietario_conta) VALUES (%s, %s, %s, %s)"""
                    new_account_values = (
                        account_name,
                        account_type,
                        user_name,
                        user_document,
                    )

                    query_executor.insert_query(
                        insert_account_query,
                        new_account_values,
                        "Conta cadastrada com sucesso!",
                        "Erro ao cadastrar conta:",
                    )

                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                    log_values = (logged_user, "Cadastro", "Cadastrou a conta {}.".format(account_name))
                    query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                    new_account_first_revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_revenue_values = (
                        "Aporte Inicial",
                        get_account_first_value,
                        today,
                        actual_horary,
                        "Depósito",
                        account_name,
                        user_name,
                        user_document,
                        "S",
                    )

                    new_account_first_future_revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_future_revenue_values = (
                        "Aporte Inicial",
                        0,
                        '2099-12-31',
                        actual_horary,
                        "Depósito",
                        account_name,
                        user_name,
                        user_document,
                        "N",
                    )

                    new_account_first_expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_expense_values = (
                        "Valor Inicial",
                        0,
                        today,
                        actual_horary,
                        "Ajuste",
                        account_name,
                        user_name,
                        user_document,
                        "S",
                    )

                    new_account_first_future_expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_future_expense_values = (
                        "Valor Inicial",
                        0,
                        '2099-12-31',
                        actual_horary,
                        "Ajuste",
                        account_name,
                        user_name,
                        user_document,
                        "N",
                    )

                    query_executor.insert_query(
                        new_account_first_revenue_query,
                        new_account_first_revenue_values,
                        "Aporte inicial registrado com sucesso!",
                        "Erro ao registrar aporte inicial:",
                    )

                    query_executor.insert_query(
                        new_account_first_future_revenue_query,
                        new_account_first_future_revenue_values,
                        "Aporte inicial registrado com sucesso!",
                        "Erro ao registrar aporte inicial:",
                    )
                    

                    query_executor.insert_query(
                        new_account_first_expense_query,
                        new_account_first_expense_values,
                        "Valor inicial registrado com sucesso!",
                        "Erro ao registrar valor inicial:",
                    )

                    query_executor.insert_query(
                        new_account_first_future_expense_query,
                        new_account_first_future_expense_values,
                        "Valor inicial registrado com sucesso!",
                        "Erro ao registrar valor inicial:",
                    )

        def update_account():

            user_accounts = query_executor.complex_consult_query(user_all_current_accounts_query)
            user_accounts = query_executor.treat_numerous_simple_result(user_accounts, to_remove_list)

            with col1:
                
                with st.expander(label="Dados", expanded=True):
                    account_selected = st.selectbox(label="Contas", options=user_accounts)
                    account_type = st.selectbox(label="Tipo de conta", options=["Conta Corrente", "Conta Móvel", "Fundo de Garantia", "Vale Alimentação"])
                    innactive_selected_account = st.selectbox(label="Inativar Conta", options=["S", "N"])
                    confirm_account_checkbox = st.checkbox(label="Confirmar dados")
                        
                update_button = st.button(label=":floppy_disk: Atualizar conta")

                if update_button and confirm_account_checkbox:
                        
                    update_account_query = '''UPDATE contas SET inativa = '{}', tipo_conta = '{}' WHERE nome_conta = '{}' AND proprietario_conta = '{}' AND documento_proprietario_conta = {}'''.format(innactive_selected_account, account_type, account_selected, user_name, user_document)
                    query_executor.update_table_unique_register(update_account_query, "Conta atualizada com sucesso!", "Erro ao atualizar conta:")

                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                    log_values = (logged_user, "Atualização", "Atualizou a conta {}.".format(account_selected))
                    query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

        def show_accounts_interface():

            with col3:
                cm_cl1, cm_cl2 = st.columns(2)

                with cm_cl2:
                    account_selected_option = st.selectbox(label="Menu", options=["Cadastrar Conta", "Atualizar Conta"])

            if account_selected_option == "Cadastrar Conta":
                get_new_account()

            if account_selected_option == "Atualizar Conta":
                update_account()

        self.show_interface = show_accounts_interface
