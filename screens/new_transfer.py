import streamlit as st
from data.cache.session_state import logged_user, logged_user_password
from dictionary.vars import transfer_categories, to_remove_list
from dictionary.sql import (
    last_transfer_id_query,
    doc_name_query,
    user_current_accounts_query,
    total_account_revenue_query,
    total_account_expense_query,
)
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from screens.reports.receipts import Receipts
from time import sleep


class NewTransfer:
    """
    Classe que representa no programa a transferência de valores entre contas.

    Atribbutes
    ----------
    new_transfer()
        Realiza a coleta dos dados da transferência e a efetua.
    """

    def get_transfer(self):
        """
        Apresenta na tela os dados que devem ser informados para que seja efetuada a transferência.
        """

        query_executor = QueryExecutor()
        receipt_executor = Receipts()
        call_time = GetActualTime()

        st.subheader(body=":currency_exchange: Nova Transferência")

        st.divider()

        col1, col2, col3 = st.columns(3)

        user_current_accounts = query_executor.complex_consult_query(
            user_current_accounts_query
        )
        user_current_accounts = query_executor.treat_numerous_simple_result(
            user_current_accounts, to_remove_list
        )

        if len(user_current_accounts) == 0:
            with col2:
                st.info(body="Você ainda não possui contas cadastradas.")
        elif len(user_current_accounts) == 1:
            with col2:
                st.info(
                    body="Você ainda não possui outra conta cadastrada para realizar transferências."
                )
        elif len(user_current_accounts) >= 2:

            with col1:
                st.subheader(body=":computer: Entrada de Dados")
                with st.expander(label="Dados", expanded=True):
                    to_treat_id = query_executor.simple_consult_query(
                        last_transfer_id_query
                    )
                    id = (
                        int(
                            query_executor.treat_simple_result(
                                to_treat_id, to_remove_list
                            )
                        )
                        + 1
                    )

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
                        options=transfer_categories,
                    )
                    origin_account = st.selectbox(
                        label=":bank: Conta de Origem", options=user_current_accounts
                    )
                    destiny_account = st.selectbox(
                        label=":bank: Conta de Destino", options=user_current_accounts
                    )
                    transfered = st.selectbox(
                        label=":inbox_tray: Transferido", options=["S", "N"]
                    )

                    user_doc_name = query_executor.complex_consult_query(
                        query=doc_name_query
                    )
                    treated_user_doc_name = query_executor.treat_complex_result(
                        user_doc_name, to_remove_list
                    )

                    confirm_values_check_box = st.checkbox(label="Confirmar Dados")

                    total_account_revenue_complete_query = (
                        total_account_revenue_query.format(
                            origin_account, logged_user, logged_user_password
                        )
                    )

                    total_account_expense_complete_query = (
                        total_account_expense_query.format(
                            origin_account, logged_user, logged_user_password
                        )
                    )

                generate_receipt_button = st.button(
                    label=":pencil: Gerar Comprovante", key="generate_receipt_button"
                )

            with col3:
                if confirm_values_check_box and generate_receipt_button:

                    with col2:

                        with st.spinner("Aguarde..."):
                            sleep(1)

                        st.subheader(body="Validação de Dados")

                        data_validation_expander = st.expander(
                            label="Informações", expanded=True
                        )

                        with data_validation_expander:
                            str_selected_account_revenues = (
                                query_executor.simple_consult_query(
                                    total_account_revenue_complete_query
                                )
                            )
                            str_selected_account_revenues = (
                                query_executor.treat_simple_result(
                                    str_selected_account_revenues, to_remove_list
                                )
                            )
                            selected_account_revenues = float(
                                str_selected_account_revenues
                            )

                            str_selected_account_expenses = (
                                query_executor.simple_consult_query(
                                    total_account_expense_complete_query
                                )
                            )
                            str_selected_account_expenses = (
                                query_executor.treat_simple_result(
                                    str_selected_account_expenses, to_remove_list
                                )
                            )
                            selected_account_expenses = float(
                                str_selected_account_expenses
                            )

                            account_available_value = round(
                                selected_account_revenues - selected_account_expenses, 2
                            )

                    with data_validation_expander:

                        st.info(
                            body="Saldo disponível da conta de origem: R$ {}".format(
                                account_available_value
                            )
                        )

                    if (
                        description != ""
                        and value >= 0.01
                        and value <= account_available_value
                        and date
                        and category != "Selecione uma opção"
                        and origin_account != "Selecione uma opção"
                        and destiny_account != "Selecione uma opção"
                        and destiny_account != origin_account
                    ):
                        with data_validation_expander:
                            st.success(body="Dados Válidos.")

                        actual_horary = call_time.get_actual_time()
                        revenue_owner_name = treated_user_doc_name[0]
                        revenue_owner_document = treated_user_doc_name[1]

                        transfer_query = "INSERT INTO transferencias (descricao, valor, data, horario, categoria, conta_origem, conta_destino, proprietario_transferencia, documento_proprietario_transferencia, transferido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

                        transfer_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            origin_account,
                            destiny_account,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered,
                        )
                        expense_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            origin_account,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered,
                        )
                        revenue_values = (
                            description,
                            value,
                            date,
                            actual_horary,
                            category,
                            destiny_account,
                            revenue_owner_name,
                            revenue_owner_document,
                            transfered,
                        )

                        query_executor.insert_query(
                            transfer_query,
                            transfer_values,
                            "Transferência registrada com sucesso!",
                            "Erro ao registrar transferência:",
                        )
                        query_executor.insert_query(
                            expense_query,
                            expense_values,
                            "Despesa registrada com sucesso!",
                            "Erro ao registrar despesa:",
                        )
                        query_executor.insert_query(
                            revenue_query,
                            revenue_values,
                            "Receita registrada com sucesso!",
                            "Erro ao registrar receita:",
                        )

                        log_query = """INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);"""
                        log_values = (
                            logged_user,
                            "Registro",
                            "Registrou uma transferência no valor de R$ {} da conta {} para a conta {}.".format(
                                value, origin_account, destiny_account
                            ),
                        )
                        query_executor.insert_query(
                            log_query, log_values, "Log gravado.", "Erro ao gravar log:"
                        )

                        st.subheader(body=":pencil: Comprovante de Transferência")

                        with st.spinner("Aguarde..."):
                            sleep(1)

                        receipt_executor.generate_transfer_receipt(
                            id,
                            description,
                            value,
                            date,
                            category,
                            origin_account,
                            destiny_account,
                        )

                    else:
                        with data_validation_expander:
                            if description == "":
                                st.error(body="A descrição está vazia.")
                            if value > account_available_value:
                                st.error(
                                    body="O valor da transferência não pode exceder o valor disponível da conta de origem."
                                )
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
                            if origin_account == destiny_account:
                                st.error(
                                    body="A conta de origem e a conta de destino não podem ser a mesma."
                                )
