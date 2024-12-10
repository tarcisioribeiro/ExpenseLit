import streamlit as st
import pandas as pd
from data.cache.session_state import logged_user
from dictionary.sql import not_received_loans_query, user_current_accounts_query, doc_name_query, last_revenue_id_query
from dictionary.vars import to_remove_list, today, decimal_values
from functions.query_executor import QueryExecutor
from functions.get_actual_time import GetActualTime
from screens.reports.receipts import Receipts
from time import sleep


class ReceiveLoan:
    def __init__(self):

        call_time = GetActualTime()
        query_executor = QueryExecutor()
        receipt_generator = Receipts()

        def show_not_received_loans():
            
            not_received_loans = query_executor.complex_compund_query(not_received_loans_query, 9, "not_received_loan")
            
            if len(not_received_loans[0]) >= 1:

                col4, col5, col6 = st.columns(3)

                with col4:

                    id, description, total_value, received_value, remaining_value, date, category, account, benefited = not_received_loans

                    loan_data_df = pd.DataFrame({"Descrição": description, "Valor Total": total_value, "Valor Recebido": received_value, "Valor a Receber": remaining_value, "Data": date, "Categoria": category, "Conta": account, "Devedor": benefited})

                    loan_data_df["Valor Total"] = loan_data_df["Valor Total"].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
                    loan_data_df["Valor Recebido"] = loan_data_df["Valor Recebido"].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
                    loan_data_df["Valor a Receber"] = loan_data_df["Valor a Receber"].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
                    loan_data_df["Data"] = pd.to_datetime(loan_data_df["Data"]).dt.strftime("%d/%m/%Y")

                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Valores", expanded=True):

                        st.dataframe(loan_data_df, hide_index=True, use_container_width=True)

                        total_loan_value = 0
                        for i in range(0, len(remaining_value)):
                            total_loan_value += remaining_value[i]
                        
                        total_loan_value = str(total_loan_value)
                        total_loan_value = total_loan_value.replace(".", ",")
                        
                        st.info(body="Valor total: :heavy_dollar_sign: {}".format(total_loan_value))

                        user_accounts = query_executor.complex_consult_query(user_current_accounts_query)
                        user_accounts = query_executor.treat_numerous_simple_result(user_accounts, to_remove_list)

                        debt = st.selectbox(label="Selecionar dívida", options=description)

                        receiving_max_value_query = '''
                            SELECT 
                                DISTINCT(emprestimos.valor - emprestimos.valor_pago)
                            FROM
                                emprestimos
                                    INNER JOIN
                                contas ON contas.proprietario_conta = emprestimos.credor
                                    AND contas.documento_proprietario_conta = emprestimos.documento_credor
                                    INNER JOIN
                                usuarios ON usuarios.nome = emprestimos.credor
                                    AND usuarios.cpf = emprestimos.documento_credor
                            WHERE
                                emprestimos.pago = 'N'
                                    AND emprestimos.descricao = '{}'
                        '''.format(debt)

                        received_actual_value_query = '''
                            SELECT 
                                DISTINCT(emprestimos.valor_pago)
                            FROM
                                emprestimos
                                    INNER JOIN
                                contas ON contas.proprietario_conta = emprestimos.credor
                                    AND contas.documento_proprietario_conta = emprestimos.documento_credor
                                    INNER JOIN
                                usuarios ON usuarios.nome = emprestimos.credor
                                    AND usuarios.cpf = emprestimos.documento_credor
                            WHERE
                                emprestimos.pago = 'N'
                                    AND emprestimos.descricao = '{}'
                        '''.format(debt)

                        total_actual_value_query = '''
                            SELECT 
                                DISTINCT(emprestimos.valor)
                            FROM
                                emprestimos
                                    INNER JOIN
                                contas ON contas.proprietario_conta = emprestimos.credor
                                    AND contas.documento_proprietario_conta = emprestimos.documento_credor
                                    INNER JOIN
                                usuarios ON usuarios.nome = emprestimos.credor
                                    AND usuarios.cpf = emprestimos.documento_credor
                            WHERE
                                emprestimos.pago = 'N'
                                    AND emprestimos.descricao = '{}'
                        '''.format(debt)

                        creditor_doc_name = query_executor.complex_consult_query(doc_name_query)
                        creditor_doc_name = query_executor.treat_complex_result(creditor_doc_name, to_remove_list)
                        benefited_name = creditor_doc_name[0]
                        benefited_document = creditor_doc_name[1]

                        receiving_max_value = query_executor.simple_consult_query(receiving_max_value_query)
                        receiving_max_value = query_executor.treat_simple_result(receiving_max_value, to_remove_list)
                        receiving_max_value = float(receiving_max_value)

                        received_actual_value = query_executor.simple_consult_query(received_actual_value_query)
                        received_actual_value = query_executor.treat_simple_result(received_actual_value, to_remove_list)
                        received_actual_value = float(received_actual_value)

                        total_actual_value = query_executor.simple_consult_query(total_actual_value_query)
                        total_actual_value = query_executor.treat_simple_result(total_actual_value, to_remove_list)
                        total_actual_value = float(total_actual_value)

                        receiving_value = st.number_input(label="Valor", min_value=0.00, max_value=receiving_max_value, step=0.01)
                        selected_account = st.selectbox(label="Conta", options=user_accounts)

                        confirm_values = st.checkbox(label="Confirmar valores")

                    receive_button = st.button(label=":floppy_disk: Receber valor de empréstimo")

                with col5:

                    if confirm_values:

                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)

                        st.subheader(body=":white_check_mark: Validação de Dados")

                        if receiving_value > 0:

                            with col5:

                                with st.expander(label="Dados", expanded=True):

                                    to_receive_value = (receiving_value + received_actual_value)
                                    str_paying_value = str(receiving_value)
                                    str_paying_value = str_paying_value.replace(".", ",")
                                    last_two_digits = str_paying_value[-2:]
                                    if last_two_digits in decimal_values:
                                        str_paying_value = str_paying_value + "0"

                                    st.info(body="Valor sendo pago: :heavy_dollar_sign: {}".format(str_paying_value))

                                    str_to_receive_value = str(to_receive_value)
                                    str_to_receive_value = str_to_receive_value.replace(".", ",")
                                    last_two_digits = str_to_receive_value[-2:]
                                    if last_two_digits in decimal_values:
                                        str_to_receive_value = str_to_receive_value + "0"

                                    st.info(body="Valor pago atualizado: :heavy_dollar_sign: {}".format(str_to_receive_value))

                                    remaining_to_pay_value = total_actual_value - (receiving_value + received_actual_value)
                                    str_remaining_to_pay_value = str(remaining_to_pay_value)
                                    str_remaining_to_pay_value = str_remaining_to_pay_value.replace(".", ",")
                                    last_two_digits = str_remaining_to_pay_value[-2:]
                                    
                                    if last_two_digits in decimal_values:
                                        str_remaining_to_pay_value = str_remaining_to_pay_value + "0"

                                    st.info('Valor restante a pagar: :heavy_dollar_sign: {}'.format(str_remaining_to_pay_value))

                            loan_payed = 'N'

                            if remaining_to_pay_value == 0:
                                loan_payed = 'S'
                        
                        elif receiving_value == 0:

                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)

                            with col5:
                                with st.expander(label="Aviso", expanded=True):
                                    st.warning(body="O valor recebido precisa ser maior do que 0.")

                    if confirm_values and receive_button:

                        actual_horary = call_time.get_actual_time()

                        if receiving_value > 0:

                            revenue_query = '''INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                            values = (
                                        debt,
                                        receiving_value,
                                        today,
                                        actual_horary,
                                        'Recebimento de Empréstimo',
                                        selected_account,
                                        benefited_name,
                                        benefited_document,
                                        'S'
                                    )

                            query_executor.insert_query(revenue_query, values, "Valor de empréstimo recebido com sucesso!", "Erro ao receber valor do empréstimo:")

                            update_loan_query = '''UPDATE emprestimos SET valor_pago = {}, pago = "{}" WHERE descricao = "{}" AND pago = "{}" AND credor = "{}" AND documento_credor = {}'''.format(to_receive_value, loan_payed, debt, 'N', benefited_name, benefited_document)
                            query_executor.update_table_unique_register(update_loan_query, "Empréstimo atualizado com sucesso!", "Erro ao atualizar valores do empréstimo:")

                            last_revenue_id = query_executor.simple_consult_query(last_revenue_id_query)
                            last_revenue_id = query_executor.treat_simple_result(last_revenue_id, to_remove_list)
                            last_revenue_id = int(last_revenue_id)

                            with col6:
                                with st.spinner(text="Aguarde..."):
                                    sleep(2.5)

                                st.subheader(body=":pencil: Comprovante de Recebimento de Empréstimo")

                                str_receiving_value = str(received_value)
                                str_receiving_value = str_receiving_value.replace(".", "")
                                last_two_digits = str_receiving_value[-2:]
                                if last_two_digits in decimal_values:
                                    str_receiving_value = str_receiving_value + "0"

                                receipt_generator.generate_receipt(table="receitas", id=last_revenue_id, description=debt, value=receiving_value, date=today, category='Pagamento de Empréstimo', account=selected_account)

                                log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                log_values = (logged_user, "Registro", "Recebeu R$ {} de um empréstimo realizado na conta {}.".format(str_receiving_value, account))
                                query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

            elif len(not_received_loans[0]) == 0:

                col4, col5, col6 = st.columns(3)

                with col5:

                    st.info(body="Você não tem valores a receber.")

        self.main_menu = show_not_received_loans