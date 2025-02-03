import streamlit as st
import pandas as pd
from dictionary.sql import not_payed_loans_query, user_current_accounts_query, last_expense_id_query
from dictionary.vars import to_remove_list, today
from functions.query_executor import QueryExecutor
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep


class PayLoan:
    """
    Classe que representa o pagamento dos empréstimos tomados pelo usuário.
    """

    def main_menu(self):
        """
        Exibe os empréstimos tomados pelo usuário.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        not_payed_loans = QueryExecutor().complex_compund_query(query=not_payed_loans_query, list_quantity=9, params=(user_name, user_document))

        if len(not_payed_loans[0]) >= 1:

            col4, col5, col6 = st.columns(3)

            with col4:

                id, description, total_value, payed_value, remaining_value, date, category, account, creditor = not_payed_loans

                loan_data_df = pd.DataFrame(
                    {
                        "Descrição": description,
                        "Valor Total": total_value,
                        "Valor Pago": payed_value,
                        "Valor a Pagar": remaining_value,
                        "Data": date,
                        "Categoria": category,
                        "Conta": account,
                        "Credor": creditor
                    }
                )

                loan_data_df["Valor Total"] = loan_data_df["Valor Total"].apply(
                    lambda x: f"R$ {x:.2f}".replace(".", ","))
                loan_data_df["Valor Pago"] = loan_data_df["Valor Pago"].apply(
                    lambda x: f"R$ {x:.2f}".replace(".", ","))
                loan_data_df["Valor a Pagar"] = loan_data_df["Valor a Pagar"].apply(
                    lambda x: f"R$ {x:.2f}".replace(".", ","))
                loan_data_df["Data"] = pd.to_datetime(
                    loan_data_df["Data"]).dt.strftime("%d/%m/%Y")

                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Valores", expanded=True):

                    st.dataframe(loan_data_df, hide_index=True,
                                 use_container_width=True)

                    total_loan_value = 0
                    for i in range(0, len(remaining_value)):
                        total_loan_value += remaining_value[i]

                    total_loan_value = str(total_loan_value)
                    total_loan_value = total_loan_value.replace(".", ",")

                    st.info(body="Valor total: :heavy_dollar_sign: {}".format(
                        total_loan_value))

                    user_accounts = QueryExecutor().complex_consult_query(
                        user_current_accounts_query)
                    user_accounts = QueryExecutor().treat_numerous_simple_result(
                        user_accounts, to_remove_list)

                    debt = st.selectbox(
                        label="Selecionar dívida", options=description)

                    paying_max_value_query = '''
                        SELECT
                            DISTINCT(emprestimos.valor - \
                                        emprestimos.valor_pago)
                        FROM
                            emprestimos
                                INNER JOIN
                            contas ON contas.proprietario_conta = emprestimos.devedor
                                AND contas.documento_proprietario_conta = emprestimos.documento_devedor
                                INNER JOIN
                            usuarios ON usuarios.nome = emprestimos.devedor
                                AND usuarios.cpf = emprestimos.documento_devedor
                        WHERE
                            emprestimos.pago = 'N'
                                AND emprestimos.descricao = '{}'
                    '''.format(debt)

                    payed_actual_value_query = '''
                        SELECT
                            DISTINCT(emprestimos.valor_pago)
                        FROM
                            emprestimos
                                INNER JOIN
                            contas ON contas.proprietario_conta = emprestimos.devedor
                                AND contas.documento_proprietario_conta = emprestimos.documento_devedor
                                INNER JOIN
                            usuarios ON usuarios.nome = emprestimos.devedor
                                AND usuarios.cpf = emprestimos.documento_devedor
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
                            contas ON contas.proprietario_conta = emprestimos.devedor
                                AND contas.documento_proprietario_conta = emprestimos.documento_devedor
                                INNER JOIN
                            usuarios ON usuarios.nome = emprestimos.devedor
                                AND usuarios.cpf = emprestimos.documento_devedor
                        WHERE
                            emprestimos.pago = 'N'
                                AND emprestimos.descricao = '{}'
                    '''.format(debt)

                    benefited_name, benefited_document = Login().get_user_data(return_option="user_doc_name")

                    paying_max_value = QueryExecutor().simple_consult_brute_query(paying_max_value_query)
                    paying_max_value = QueryExecutor().treat_simple_result(paying_max_value, to_remove_list)
                    paying_max_value = float(paying_max_value)

                    payed_actual_value = QueryExecutor().simple_consult_brute_query(payed_actual_value_query)
                    payed_actual_value = QueryExecutor().treat_simple_result(payed_actual_value, to_remove_list)
                    payed_actual_value = float(payed_actual_value)

                    total_actual_value = QueryExecutor().simple_consult_brute_query(total_actual_value_query)
                    total_actual_value = QueryExecutor().treat_simple_result(total_actual_value, to_remove_list)
                    total_actual_value = float(total_actual_value)

                    paying_value = st.number_input(
                        label="Valor", min_value=0.00, max_value=paying_max_value, step=0.01)
                    selected_account = st.selectbox(
                        label="Conta", options=user_accounts)

                    confirm_values = st.checkbox(label="Confirmar valores")

                pay_button = st.button(
                    label=":floppy_disk: Pagar valor de empréstimo")

            with col5:

                if confirm_values:

                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)

                    st.subheader(
                        body=":white_check_mark: Validação de Dados")

                    if paying_value > 0:

                        with col5:

                            with st.expander(label="Dados", expanded=True):

                                to_pay_value = (
                                    paying_value + payed_actual_value)
                                str_paying_value = Variable().treat_complex_string(
                                    paying_value)

                                st.info(body="Valor sendo pago: :heavy_dollar_sign: {}".format(
                                    str_paying_value))

                                str_to_pay_value = Variable().treat_complex_string(
                                    to_pay_value)

                                st.info(body="Valor pago atualizado: :heavy_dollar_sign: {}".format(
                                    str_to_pay_value))

                                remaining_to_pay_value = total_actual_value - \
                                    (paying_value + payed_actual_value)
                                str_remaining_to_pay_value = Variable().treat_complex_string(
                                    remaining_to_pay_value)

                                st.info('Valor restante a pagar: :heavy_dollar_sign: {}'.format(
                                    str_remaining_to_pay_value))

                        loan_payed = 'N'

                        if remaining_to_pay_value == 0:
                            loan_payed = 'S'

                    elif paying_value == 0:

                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)

                        with col5:
                            with st.expander(label="Aviso", expanded=True):
                                st.warning(
                                    body="O valor pago precisa ser maior do que 0.")

                if confirm_values and pay_button:

                    actual_horary = GetActualTime().get_actual_time()

                    if paying_value > 0:

                        expense_query = '''INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                        values = (
                            'Pagamento de empréstimo - {}'.format(debt),
                            paying_value,
                            today,
                            actual_horary,
                            'Pagamento de Empréstimo',
                            selected_account,
                            benefited_name,
                            benefited_document,
                            'S'
                        )

                        QueryExecutor().insert_query(
                            expense_query, values, "Valor de empréstimo pago com sucesso!", "Erro ao pagar valor do empréstimo:")

                        update_loan_query = '''UPDATE emprestimos SET valor_pago = {}, pago = "{}" WHERE descricao = "{}" AND pago = "{}" AND devedor = "{}" AND documento_devedor = {}'''.format(
                            to_pay_value, loan_payed, debt, 'N', benefited_name, benefited_document)
                        QueryExecutor().update_table_unique_register(
                            update_loan_query, "Empréstimo atualizado com sucesso!", "Erro ao atualizar valores do empréstimo:")

                        last_expense_id = QueryExecutor().simple_consult_brute_query(last_expense_id_query)
                        last_expense_id = QueryExecutor().treat_simple_result(last_expense_id, to_remove_list)
                        last_expense_id = int(last_expense_id)

                        with col6:
                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)

                            st.subheader(
                                body=":pencil: Comprovante de Pagamento de Empréstimo")

                            Receipts().generate_receipt(table="despesas", id=last_expense_id, description=debt,
                                                        value=paying_value, date=today, category='Pagamento de Empréstimo', account=selected_account)

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Pagou R$ {} de um empréstimo tomado na conta {}.".format(
                                str_paying_value, account))
                            QueryExecutor().insert_query(
                                log_query, log_values, "Log gravado.", "Erro ao gravar log:")

        elif len(not_payed_loans[0]) == 0:

            col4, col5, col6 = st.columns(3)

            with col5:

                st.info(body="Você não tem valores a pagar.")
