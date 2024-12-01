from data.cache.session_state import logged_user
from dictionary.vars import months, years, to_remove_list
from dictionary.user_stats import user_name, user_document
from dictionary.sql import owner_cards_query, user_current_accounts_query
from functions.credit_card import Credit_Card
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from time import sleep
import streamlit as st


class UpdateCreditCards:
    def __init__(self):

        call_credit_card = Credit_Card()
        query_executor = QueryExecutor()
        call_document = Documents()

        col1, col2, col3 = st.columns(3)

        def get_new_credit_card():

            user_current_accounts = query_executor.complex_consult_query(user_current_accounts_query)
            user_current_accounts = query_executor.treat_numerous_simple_result(user_current_accounts, to_remove_list)

            if len(user_current_accounts) == 0:
                with col2:
                    st.warning(body="Você ainda não possui contas cadastradas.")

            elif len(user_current_accounts) >= 1:
                with col1:
                    with st.expander(label="Dados cadastrais", expanded=True):
                        card_name = st.text_input(label="Nome do cartão")
                        card_number = st.text_input(label="Número do Cartão")
                        owner_name = st.text_input(label="Nome do Titular")

                with col2:
                    with st.expander(label="Dados confidenciais", expanded=True):
                        expire_date = st.date_input(label="Data de validade")
                        security_code = st.number_input(
                            label="Código de segurança",
                            step=1,
                            min_value=1,
                            max_value=999,
                        )
                        credit_limit_value = st.number_input(
                            label="Limite do cartão", step=0.01, min_value=0.01
                        )
                        associated_account = st.selectbox(
                            label="Conta associada", options=user_current_accounts
                        )

                    send_form_button = st.button(label="Cadastrar cartão")

                    if send_form_button:
                        with col3:
                            with st.expander(label="Validação dos dados", expanded=True):
                                is_card_valid = call_document.validate_credit_card(card_number=card_number)
                                is_document_valid = (call_document.validate_owner_document(owner_document=user_document))

                                if (
                                    card_name != ""
                                    and card_number != ""
                                    and owner_name != ""
                                    and expire_date != ""
                                    and security_code > 0
                                    and credit_limit_value >= 0.01
                                    and associated_account != "Selecione uma opção"
                                ):
                                    if (
                                        is_document_valid == True
                                        and is_card_valid == True
                                    ):
                                        st.success(body="Número de cartão válido.")
                                        st.success(body="Documento Válido.")

                                        new_credit_card_query = """INSERT INTO cartao_credito (nome_cartao, numero_cartao, nome_titular, proprietario_cartao, documento_titular, data_validade, codigo_seguranca, limite_credito, conta_associada)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                                        new_credit_card_values = (
                                            card_name,
                                            card_number,
                                            owner_name,
                                            user_name,
                                            user_document,
                                            expire_date,
                                            security_code,
                                            credit_limit_value,
                                            associated_account,
                                        )

                                        query_executor.insert_query(new_credit_card_query, new_credit_card_values, "Cartão cadastrado com sucesso!", "Erro ao cadastrar cartão")

                                        log_query = '''INSERT INTO logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                        log_values = (logged_user, "Cadastro", "Cadastrou o cartão {} associado a conta {}.".format(card_name, associated_account))
                                        query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                                    elif (
                                        is_card_valid == False and is_document_valid == True):
                                        st.error(body="Número de cartão inválido.")
                                        st.success(body="Documento Válido.")

                                    elif (is_document_valid == False and is_card_valid == True):
                                        st.success(body="Número de cartão válido.")
                                        st.error(body="Documento inválido.")

                                    elif (is_document_valid == False and is_card_valid == False):
                                        st.error(body="Número de cartão inválido.")
                                        st.error(body="Documento inválido.")

                                else:
                                    st.error(body="Algum dado não foi informado. Revise-os.")

        def update_credit_card():

            credit_cards = query_executor.complex_consult_query(owner_cards_query)
            credit_cards = query_executor.treat_numerous_simple_result(credit_cards, to_remove_list)

            with col3:

                cc1, cc2 = st.columns(2)

                with cc2:

                    card = st.selectbox(label="Escolha um cartão", options=credit_cards)

            with col1:

                    cc_max_limit_query = '''
                    SELECT 
                        limite_maximo
                    FROM
                        cartao_credito
                    WHERE
                        nome_cartao = '{}'
                    AND proprietario_cartao = '{}'
                    AND documento_titular = {}'''.format(card, user_name, user_document)
                    cc_max_limit = query_executor.simple_consult_query(cc_max_limit_query)
                    cc_max_limit = query_executor.treat_simple_result(cc_max_limit, to_remove_list)

                    cc_max_limit = float(cc_max_limit)
                    cc_max_limit = int(cc_max_limit)

                    sleep(1)

                    with st.expander(label="Dados", expanded=True):

                        new_limit = st.number_input(label="Limite", min_value=0, max_value=cc_max_limit, step=1)
                        inactive = st.selectbox(label="Inativo", options=["S","N"])
                        confirm_values = st.checkbox(label="Confirmar Dados")

            send_data_button = st.button(label="Atualizar valores")

            if confirm_values and send_data_button:

                new_limit_query = '''
                UPDATE cartao_credito 
                SET 
                    limite_credito = {},
                    inativo = '{}'
                WHERE
                    nome_cartao = '{}'
                    AND proprietario_cartao = '{}'
                    AND documento_titular = {};'''.format(new_limit, inactive, card, user_name, user_document)

                with col2:
                    with st.spinner(text='Aguarde...'):
                        sleep(1)
                        query_executor.update_table_unique_register(new_limit_query, "Limite atualizado com sucesso!", "Erro ao atualizar limite:")

                        log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                        log_values = (logged_user, "Registro", "Atualizou o limite do cartão {}.".format(card))
                        query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

        def update_credit_card_invoices():

            credit_cards = query_executor.complex_consult_query(owner_cards_query)
            credit_cards = query_executor.treat_numerous_simple_result(credit_cards, to_remove_list)

            if len(credit_cards) == 0:
                with col2:
                    st.warning(body="Você ainda não possui cartões cadastrados.")

            elif len(credit_cards) >= 1:
                with col1:
                    with st.expander(label="Dados da fatura", expanded=True):
                        card_name = st.selectbox(label="Cartão", options=credit_cards)
                        card_number, owner_name, owner_document, card_code = call_credit_card.credit_card_key(card=card_name)
                        year = st.selectbox(label="Ano", options=years)
                        month = st.selectbox(label="Mês", options=months)

                        if year != '' or year > 0:

                            beggining_invoice_date = st.date_input(label="Início")
                            ending_invoice_date = st.date_input(label="Fim")

                    register_invoice = st.button(label=":floppy_disk: Registrar fechamento")

                    with col2:
                        data_expander = st.expander(label="Validação dos dados", expanded=True)

                    if register_invoice:

                        with col2:
                            with st.expander(label="Validação dos dados", expanded=True):

                                if card_name != "" and month != "" and beggining_invoice_date < ending_invoice_date:

                                    with data_expander:
                                        st.success(body="Dados válidos.")

                                    new_credit_card_invoice_query = """INSERT INTO fechamentos_cartao (nome_cartao, numero_cartao, documento_titular, ano, mes, data_comeco_fatura, data_fim_fatura) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                                    new_credit_card_invoice_values = (
                                        card_name,
                                        card_number,
                                        owner_document,
                                        year,
                                        month,
                                        beggining_invoice_date,
                                        ending_invoice_date,
                                    )

                                    query_executor.insert_query(new_credit_card_invoice_query, new_credit_card_invoice_values, "Fechamento cadastrado com sucesso!", "Erro ao cadastrar fechamento:")

                                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                    log_values = (logged_user, "Cadastro", "Cadastrou um fechamento do cartão {}.".format(card_name))
                                    query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                                else:
                                    if beggining_invoice_date >= ending_invoice_date:
                                        st.error(body="O ano informado é inválido.")
                                        st.error(body="A data de ínicio da fatura não pode ser superior a data do fim da fatura.")
                                    elif beggining_invoice_date < ending_invoice_date:
                                        st.error(body="O ano informado é inválido.")
                                        st.success(body="Datas da fatura válidas.")
                                    elif beggining_invoice_date >= ending_invoice_date:
                                        st.success(body="O ano informado é válido.")
                                        st.error(body="A data de ínicio da fatura não pode ser superior a data do fim da fatura.")

        def show_interface():

            with col3:
                cm_cl1, cm_cl2 = st.columns(2)

                cc_menu_options = [
            "Cadastrar cartão",
            "Atualizar cartão",
            "Atualizar vencimentos de fatura",
            ]

                with cm_cl2:
                    cc_selected_option = st.selectbox(
                        label="Menu", options=cc_menu_options
                    )

            if cc_selected_option == "Cadastrar cartão":
                get_new_credit_card()

            if cc_selected_option == "Atualizar cartão":
                update_credit_card()

            if cc_selected_option == "Atualizar vencimentos de fatura":
                update_credit_card_invoices()

        self.credit_cards_interface = show_interface
