from data.cache.session_state import logged_user, logged_user_password
from dictionary.sql import user_current_accounts_query, expenses_statement_query, revenues_statement_query
from dictionary.vars import to_remove_list
from functions.query_executor import QueryExecutor
from functions.variables import Variables
from time import sleep
import pandas as pd
import streamlit as st


class AccountStatement:

    def __init__(self):

        query_executor = QueryExecutor()
        variable = Variables()

        def mount_statement_query(statement_type: str, accounts: list, initial_data: str, final_data: str):

            statement_query_list = []

            str_accounts = '''('''

            for i in range(0, len(accounts)):
                if i < (len(accounts) - 1):
                    str_accounts += "'" + str(accounts[i]) + "'" + ''', '''
                elif i == len(accounts) - 1:
                    str_accounts += "'" + str(accounts[i]) + "'"

            str_accounts = str_accounts + ''')'''

            complete_expenses_statement_query = expenses_statement_query.format(initial_data, final_data, str_accounts, logged_user, logged_user_password)
            complete_revenues_statement_query = revenues_statement_query.format(initial_data, final_data, str_accounts, logged_user, logged_user_password)

            if statement_type == 'Despesas':
                statement_query_list.append(complete_expenses_statement_query)
            elif statement_type == 'Receitas':
                statement_query_list.append(complete_revenues_statement_query)
            elif statement_type == 'Despesas e Receitas':
                statement_query_list.append(complete_expenses_statement_query)
                statement_query_list.append(complete_revenues_statement_query)
            
            return statement_query_list

        def consult_statement(statement_query_list: list):

            for i in range(len(statement_query_list)):
                empty_list = query_executor.complex_compund_query(statement_query_list[i], 6, 'statement_')

                description, value, date, time, category, account = (empty_list)

                if len(description) == 0 and len(value) == 0 and len(date) == 0 and len(time) == 0 and len(category) == 0 and len(account) == 0:
                    with st.expander(label="Relatório", expanded=True):
                        st.info(body="Nao há registros neste período.")

                elif len(description) > 0 and len(value) > 0 and len(date) > 0 and len(time) > 0 and len(category) > 0 and len(account) > 0: 

                    aux_str = ''''''

                    for i in range(0, len(time)):
                        aux_str = str(time[i])
                        time[i] = aux_str

                    with st.expander(label="Relatório", expanded=True):

                        loan_data_df = pd.DataFrame(
                            {
                                "Descrição": description,
                                "Valor": value,
                                "Data": date,
                                "Horário": time,
                                "Categoria": category,
                                "Conta": account,
                            }
                        )

                        loan_data_df["Valor"] = loan_data_df["Valor"].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
                        loan_data_df["Data"] = pd.to_datetime(loan_data_df["Data"]).dt.strftime("%d/%m/%Y")
                        st.dataframe(loan_data_df, hide_index=True, use_container_width=True)
            
            return value

        def main_menu():

            user_current_accounts = query_executor.complex_consult_query(user_current_accounts_query)
            user_current_accounts = query_executor.treat_numerous_simple_result(user_current_accounts, to_remove_list)

            col4, col5, col6 = st.columns(3)

            if len(user_current_accounts) > 0:

                with col4:

                    with st.expander(label="Dados", expanded=True):

                        statement_option = st.selectbox(label="Tipos de extrato", options=["Selecione uma opção", "Despesas", "Receitas", "Despesas e Receitas"])
                        selected_accounts = st.multiselect(label="Contas", options=user_current_accounts, placeholder="Escolha a(s) conta(s)")
                        initial_data = st.date_input(label="Data de início")
                        final_data = st.date_input(label="Data de fim")
                        confirm_choice = st.checkbox(label="Confirmar dados")

                    consult_tables = st.button(label=":chart: Gerar Relatórios")

                if confirm_choice and consult_tables:

                    with col5:

                        with st.spinner(text="Aguarde..."):
                            sleep(1)
                    
                        if statement_option != "Selecione uma opção" and len(selected_accounts) > 0 and (initial_data <= final_data):
                                query_list = mount_statement_query(statement_option, selected_accounts, initial_data, final_data)

                                with st.spinner(text="Aguarde..."):
                                    sleep(1)
                                value = consult_statement(query_list)

                                with col6:
                                    with st.spinner(text="Aguarde..."):
                                        sleep(1)

                                    total_value = 0
                                    for i in range(0, len(value)):
                                        total_value += value[i]
                                        medium_value = round((total_value / len(value)), 2)
                                        
                                    medium_value = str(medium_value)
                                    medium_value = medium_value.replace(".", ",")
                                    total_value = str(total_value)
                                    total_value = total_value.replace(".", ",")

                                    with st.expander(label="Dados", expanded=True):
                                        st.info(body="Quantidade de {}: {}.".format(statement_option.lower(), len(value)))
                                        st.info(body="Valor total das {}: R$ {}.".format(statement_option.lower(), total_value))
                                        st.info(body="Valor médio das {}: R$ {}.".format(statement_option.lower(), medium_value))

                                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                    log_values = (logged_user, "Consulta", "Consultou o relatório de {} entre o período de {} a {}.".format(statement_option, initial_data, final_data))
                                    query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                        elif (len(selected_accounts) == 0) or (initial_data > final_data) or (statement_option == "Selecione uma opção"):
                            with st.expander(label="Avisos", expanded=True):
                                if statement_option == "Selecione uma opção":
                                    st.error(body="Selecione um tipo de extrato.")
                                if len(selected_accounts) == 0:
                                    st.error(body="Nenhuma conta selecionada.")
                                if initial_data > final_data:
                                    st.error(body="A data inicial não pode ser maior que a final.")

            elif len(user_current_accounts) == 0:
                with col5:
                    st.warning(body="Você ainda não possui contas cadastradas.")

        self.main_menu = main_menu
