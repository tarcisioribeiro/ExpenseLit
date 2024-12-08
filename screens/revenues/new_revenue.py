from data.cache.session_state import logged_user
from dictionary.user_stats import user_name, user_document
from dictionary.vars import revenue_categories, to_remove_list
from dictionary.sql import last_revenue_id_query, user_current_accounts_query
from functions.query_executor import QueryExecutor
from functions.get_actual_time import GetActualTime
from screens.reports.receipts import Receipts
from time import sleep
import streamlit as st


class NewCurrentRevenue:
    def __init__(self):

        query_executor = QueryExecutor()
        receipt_executor = Receipts()
        call_actual_time = GetActualTime()

        user_current_accounts = query_executor.complex_consult_query(user_current_accounts_query)
        user_current_accounts = query_executor.treat_numerous_simple_result(user_current_accounts, to_remove_list)


        def new_revenue():

            col4, col5, col6 = st.columns(3)

            if len(user_current_accounts) == 0: 
                   with col5:
                       st.info("Você ainda não possui contas correntes cadastradas.")

            elif len(user_current_accounts) >= 1:

                with col4:

                    st.subheader(body=":computer: Entrada de dados")

                    with st.expander(label="Dados", expanded=True):

                        id = query_executor.simple_consult_query(last_revenue_id_query)
                        id = query_executor.treat_simple_result(id, to_remove_list)
                        id = int(id) + 1

                        description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição")
                        value = st.number_input(label=":dollar: Valor", min_value=0.01)
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(label=":card_index_dividers: Categoria", options=revenue_categories)
                        account = st.selectbox(label=":bank: Conta", options=user_current_accounts)
                        received = st.selectbox(label=":inbox_tray: Recebido", options=["S", "N"])

                        confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                    send_revenue_button = st.button(label=":pencil: Gerar Comprovante", key="send_revenue_button")

                with col6:

                    if confirm_values_check_box and send_revenue_button:

                        with col5:
                            with st.spinner("Aguarde..."):
                                sleep(1)

                            st.subheader(body="Validação de Dados")

                            data_validation_expander = st.expander(label="Informações", expanded=True)

                        if (
                            description != ""
                            and value >= 0.01
                            and date != ""
                            and category != "Selecione uma opção"
                            and account != "Selecione uma opção"
                        ):
                            with data_validation_expander:
                                st.success(body="Dados Válidos.")

                            actual_horary = call_actual_time.get_actual_time()

                            revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            values = (
                                description,
                                value,
                                date,
                                actual_horary,
                                category,
                                account,
                                user_name,
                                user_document,
                                received,
                            )
                            query_executor.insert_query(
                                revenue_query, values, "Receita registrada com sucesso!", "Erro ao registrar receita:")
                            
                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            if received == 'S':
                                log_values = (logged_user, "Registro", "Registrou uma receita no valor de R$ {} associada a conta {}.".format(value, account))
                            elif received == 'N':
                                log_values = (logged_user, "Registro", "Registrou uma receita não recebida no valor de R$ {} associada a conta {}.".format(value, account))
                            query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            with st.spinner("Aguarde..."):
                                sleep(1)

                            st.subheader(
                                body=":pencil: Comprovante de receita")

                            receipt_executor.generate_receipt(
                                'receitas', id, description, value, str(date), category, account)

                        else:
                            with data_validation_expander:
                                st.error(
                                    body=":warning: Algum dado está errado, revise-os.")

        self.main_menu = new_revenue
