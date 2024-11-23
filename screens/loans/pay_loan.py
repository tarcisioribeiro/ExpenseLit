import streamlit as st
import pandas as pd
from data.cache.session_state import logged_user
from dictionary.sql import (
    not_payed_loans_query,
    user_current_accounts_query,
    doc_name_query,
    last_expense_id_query,
)
from dictionary.vars import to_remove_list, today
from functions.query_executor import QueryExecutor
from functions.get_actual_time import GetActualTime
from screens.reports.receipts import Receipts
from time import sleep


class PayLoan:
    """
    Classe contendo os métodos e interface para o pagamento de empréstimos.

    Atributos:
        show_loans = faz a chamada da interface de pagamento de empréstimos.

    Métodos:
        show_loans() = Exibe os empréstimos não pagos.

    """

    def show_loans(self):
        """
        Exibe os empréstimos não pagos.
        """

        query_executor = QueryExecutor()
        call_time = GetActualTime()

        not_payed_loans = query_executor.complex_compund_query(
            not_payed_loans_query, 9, "not_payed_loan"
        )

        if len(not_payed_loans[0]) >= 1:

            col4, col5 = st.columns(2)

            with col4:

                (
                    id,
                    description,
                    total_value,
                    payed_value,
                    remaining_value,
                    date,
                    category,
                    account,
                    creditor,
                ) = not_payed_loans

                loan_data_df = pd.DataFrame(
                    {
                        "Descrição": description,
                        "Valor Total": total_value,
                        "Valor Pago": payed_value,
                        "Valor a Pagar": remaining_value,
                        "Data": date,
                        "Categoria": category,
                        "Conta": account,
                        "Credor": creditor,
                    }
                )

                loan_data_df["Valor Total"] = loan_data_df["Valor Total"].apply(
                    lambda x: f"R$ {x:.2f}"
                )
                loan_data_df["Valor Pago"] = loan_data_df["Valor Pago"].apply(
                    lambda x: f"R$ {x:.2f}"
                )
                loan_data_df["Valor a Pagar"] = loan_data_df["Valor a Pagar"].apply(
                    lambda x: f"R$ {x:.2f}"
                )
                loan_data_df["Data"] = pd.to_datetime(loan_data_df["Data"]).dt.strftime(
                    "%d/%m/%Y"
                )

                with st.expander(label="Valores", expanded=True):

                    st.dataframe(
                        loan_data_df, hide_index=True, use_container_width=True
                    )

                    total_loan_value = 0
                    for i in range(0, len(remaining_value)):
                        total_loan_value += remaining_value[i]

                    st.info(
                        body="Valor total: :heavy_dollar_sign: {}".format(
                            total_loan_value
                        )
                    )

            with col5:

                with st.expander(label="Seleção de dados", expanded=True):

                    user_accounts = query_executor.complex_consult_query(
                        user_current_accounts_query
                    )
                    user_accounts = query_executor.treat_numerous_simple_result(
                        user_accounts, to_remove_list
                    )

                    debt = st.selectbox(label="Selecionar dívida", options=description)

                    paying_max_value_query = """
                            SELECT 
                                DISTINCT(emprestimos.valor - emprestimos.valor_pago)
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
                        """.format(
                        debt
                    )

                    payed_actual_value_query = """
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
                        """.format(
                        debt
                    )

                    total_actual_value_query = """
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
                        """.format(
                        debt
                    )

                    benefited_doc_name = query_executor.complex_consult_query(
                        doc_name_query
                    )
                    benefited_doc_name = query_executor.treat_complex_result(
                        benefited_doc_name, to_remove_list
                    )
                    benefited_name = benefited_doc_name[0]
                    benefited_document = benefited_doc_name[1]

                    paying_max_value = query_executor.simple_consult_query(
                        paying_max_value_query
                    )
                    paying_max_value = query_executor.treat_simple_result(
                        paying_max_value, to_remove_list
                    )
                    paying_max_value = float(paying_max_value)

                    payed_actual_value = query_executor.simple_consult_query(
                        payed_actual_value_query
                    )
                    payed_actual_value = query_executor.treat_simple_result(
                        payed_actual_value, to_remove_list
                    )
                    payed_actual_value = float(payed_actual_value)

                    total_actual_value = query_executor.simple_consult_query(
                        total_actual_value_query
                    )
                    total_actual_value = query_executor.treat_simple_result(
                        total_actual_value, to_remove_list
                    )
                    total_actual_value = float(total_actual_value)

                    paying_value = st.number_input(
                        label="Valor",
                        min_value=0.00,
                        max_value=paying_max_value,
                        step=0.01,
                    )
                    selected_account = st.selectbox(
                        label="Conta", options=user_accounts
                    )

                    confirm_values = st.checkbox(label="Confirmar valores")

                pay_button = st.button(label=":floppy_disk: Pagar valor de empréstimo")

            st.divider()

            col6, col7 = st.columns(2)

            with col6:

                if confirm_values:

                    with st.spinner(text="Aguarde..."):
                        sleep(1)

                    if paying_value > 0:

                        with st.expander(label="Dados", expanded=True):

                            to_pay_value = paying_value + payed_actual_value
                            st.info(
                                body="Valor sendo pago: :heavy_dollar_sign: {}".format(
                                    paying_value
                                )
                            )
                            st.info(
                                body="Valor pago atualizado: :heavy_dollar_sign: {}".format(
                                    to_pay_value
                                )
                            )
                            remaining_to_pay_value = total_actual_value - (
                                paying_value + payed_actual_value
                            )
                            st.info(
                                "Valor restante a pagar: :heavy_dollar_sign: {}".format(
                                    remaining_to_pay_value
                                )
                            )

                        loan_payed = "N"

                        if remaining_to_pay_value == 0:
                            loan_payed = "S"

                    elif paying_value == 0:

                        with st.spinner(text="Aguarde..."):
                            sleep(1)

                        with st.expander(label="Aviso", expanded=True):
                            st.warning(body="O valor pago precisa ser maior do que 0.")

                if confirm_values and pay_button:

                    actual_horary = call_time.get_actual_time()

                    expense_query = """INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    values = (
                        "Pagamento de empréstimo - {}".format(debt),
                        paying_value,
                        today,
                        actual_horary,
                        "Pagamento de Empréstimo",
                        selected_account,
                        benefited_name,
                        benefited_document,
                        "S",
                    )

                    query_executor.insert_query(
                        expense_query,
                        values,
                        "Valor de empréstimo pago com sucesso!",
                        "Erro ao pagar valor do empréstimo:",
                    )

                    update_loan_query = """UPDATE emprestimos SET valor_pago = {}, pago = "{}" WHERE descricao = "{}" AND pago = "{}" AND devedor = "{}" AND documento_devedor = {}""".format(
                        to_pay_value,
                        loan_payed,
                        debt,
                        "N",
                        benefited_name,
                        benefited_document,
                    )
                    query_executor.update_table_unique_register(
                        update_loan_query,
                        "Empréstimo atualizado com sucesso!",
                        "Erro ao atualizar valores do empréstimo:",
                    )

                    last_expense_id = query_executor.simple_consult_query(
                        last_expense_id_query
                    )
                    last_expense_id = query_executor.treat_simple_result(
                        last_expense_id, to_remove_list
                    )
                    last_expense_id = int(last_expense_id)

                    with col7:
                        receipt_generator = Receipts()
                        receipt_generator.generate_receipt(
                            table="despesas",
                            id=last_expense_id,
                            description="Pagamento de empréstimo - {}".format(debt),
                            value=paying_value,
                            date=today,
                            category="Pagamento de Empréstimo",
                            account=selected_account,
                        )

                        log_query = """INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);"""
                        log_values = (
                            logged_user,
                            "Registro",
                            "Pagou R$ {} de um empréstimo tomado na conta {}.".format(
                                paying_value, account
                            ),
                        )
                        query_executor.insert_query(
                            log_query, log_values, "Log gravado.", "Erro ao gravar log:"
                        )

        elif len(not_payed_loans[0]) == 0:

            col4, col5, col6 = st.columns(3)

            with col5:

                st.info(body="Você não tem valores a pagar.")