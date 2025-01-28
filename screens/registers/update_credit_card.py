from data.cache.session_state import logged_user
from datetime import date
from dictionary.vars import to_remove_list, today, decimal_values
from dictionary.app_vars import months, years
from dictionary.sql import owner_cards_query, user_current_accounts_query, credit_card_expire_date_query
from functions.credit_card import Credit_Card
from functions.login import Login
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from functions.variable import Variable
from time import sleep
import streamlit as st


class UpdateCreditCards:
    """
    Classe que representa o cadastro e atualização dos dados dos cartões de crédito do usuário.
    """

    def get_today_datetime(self):

        today_list = today.split("-")
        for i in range(0, len(today_list)):
            int_aux = int(today_list[i])
            today_list[i] = int_aux

        today_datetime = date(today_list[0], today_list[1], today_list[2])

        return today_datetime

    def get_new_credit_card(self):
        """
        Realiza o cadastro de um novo cartão de crédito.
        """
        user_name, user_document = Login().get_user_doc_name()

        col1, col2, col3 = st.columns(3)

        user_current_accounts = QueryExecutor().complex_consult_query(query=user_current_accounts_query, params=(user_name, user_document))
        user_current_accounts = QueryExecutor().treat_numerous_simple_result(user_current_accounts, to_remove_list)

        if len(user_current_accounts) == 0:
            with col2:
                st.warning(
                    body="Você ainda não possui contas cadastradas.")

        elif len(user_current_accounts) >= 1:
            with col1:

                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados cadastrais", expanded=True):
                    card_name = st.text_input(
                        label=":lower_left_ballpoint_pen: Nome do cartão")
                    card_number = st.text_input(
                        label=":lower_left_ballpoint_pen: Número do Cartão", help="O número do cartão não deve conter espaços.")
                    owner_name = st.text_input(
                        label=":lower_left_ballpoint_pen: Nome do Titular")
                    expire_date = st.date_input(
                        label=":calendar: Data de validade")

                confirm_credit_card_values = st.checkbox(
                    label="Confirmar dados")

            with col2:
                st.subheader(body="")
                with st.expander(label="Dados confidenciais", expanded=True):
                    security_code = st.text_input(
                        label=":lock: Código de segurança", max_chars=3, type="password")
                    confirm_security_code = st.text_input(
                        label=":lock: Confirme o código de segurança", max_chars=3, type="password")
                    credit_limit_value = st.number_input(
                        label=":dollar: Limite do cartão", step=0.01, min_value=0.01)
                    associated_account = st.selectbox(
                        label=":bank: Conta associada", options=user_current_accounts)

                send_form_button = st.button(
                    label=":floppy_disk: Cadastrar cartão")

                if send_form_button and confirm_credit_card_values:
                    today_datetime = self.get_today_datetime()

                    with col3:
                        cm_cl1, cm_cl2 = st.columns(2)
                        with cm_cl2:
                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)
                            is_card_valid = Documents().validate_credit_card(card_number=card_number)
                            is_document_valid = (Documents().validate_owner_document(owner_document=user_document))

                            if card_name != "" and card_number != "" and owner_name != "" and security_code != "" and confirm_security_code != "" and (security_code == confirm_security_code) and (today_datetime < expire_date):
                                if is_document_valid == True and is_card_valid == True:
                                    st.success(
                                        body="Número de cartão válido.")
                                    st.success(body="Documento Válido.")

                                    new_credit_card_query = """INSERT INTO cartao_credito (nome_cartao, numero_cartao, nome_titular, proprietario_cartao, documento_titular, data_validade, codigo_seguranca, limite_credito, limite_maximo, conta_associada)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                                    new_credit_card_values = (card_name, card_number, owner_name, user_name, user_document,
                                                              expire_date, security_code, credit_limit_value, credit_limit_value, associated_account)
                                    QueryExecutor().insert_query(
                                        new_credit_card_query, new_credit_card_values, "Cartão cadastrado com sucesso!", "Erro ao cadastrar cartão")

                                    log_query = '''INSERT INTO logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                    log_values = (logged_user, "Cadastro", "Cadastrou o cartão {} associado a conta {}.".format(
                                        card_name, associated_account))
                                    QueryExecutor().insert_query(
                                        log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                                elif is_card_valid == False and is_document_valid == True:
                                    st.error(
                                        body="Número de cartão inválido.")
                                    st.success(body="Documento Válido.")

                                elif is_document_valid == False and is_card_valid == True:
                                    st.success(
                                        body="Número de cartão válido.")
                                    st.error(body="Documento inválido.")

                                elif is_document_valid == False and is_card_valid == False:
                                    st.error(
                                        body="Número de cartão inválido.")
                                    st.error(body="Documento inválido.")

                            elif card_name == "" or card_number == "" or owner_name == "" or security_code == "" or confirm_security_code == "" and (security_code != confirm_security_code) or (today_datetime >= expire_date):
                                with cm_cl2:
                                    if card_name == "":
                                        st.error(
                                            body="O nome do cartão deve ser preenchido.")
                                    if card_number == "":
                                        st.error(
                                            body="O número do cartão deve ser preenchido.")
                                    if owner_name == "":
                                        st.error(
                                            body="O nome do proprietário do cartão deve ser preenchido.")
                                    if today_datetime >= expire_date:
                                        st.error(
                                            body="A data de validade do cartão não pode ser menor ou igual a data atual.")
                                    if security_code != confirm_security_code:
                                        st.error(
                                            body="Os códigos de segurança não coincidem.")

                elif send_form_button and confirm_credit_card_values == False:
                    with col3:
                        cm_cl1, cm_cl2 = st.columns(2)
                    with cm_cl2:
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        st.warning(
                            body="Revise e confirme os dados antes de prosseguir.")

    def update_credit_card(self):
        """
        Atualiza os dados do cartão de crédito.
        """
        user_name, user_document = Login().get_user_doc_name()

        col1, col2, col3 = st.columns(3)

        credit_cards = QueryExecutor().complex_consult_query(owner_cards_query)
        credit_cards = QueryExecutor().treat_numerous_simple_result(credit_cards, to_remove_list)

        with col3:

            cc1, cc2 = st.columns(2)

            with cc2:
                card = st.selectbox(
                    label="Escolha um cartão", options=credit_cards)

        with col1:
            st.subheader(body=":computer: Entrada de Dados")

            cc_max_limit_query = '''SELECT limite_maximo FROM cartao_credito WHERE nome_cartao = '{}' AND proprietario_cartao = '{}' AND documento_titular = {}'''.format(card, user_name, user_document)
            cc_max_limit = QueryExecutor().simple_consult_brute_query(cc_max_limit_query)
            cc_max_limit = QueryExecutor().treat_simple_result(cc_max_limit, to_remove_list)
            cc_max_limit = float(cc_max_limit)

            inactive_options = {
                "Sim": "S",
                "Não": "N",
            }

            with st.expander(label="Dados", expanded=True):
                new_limit = st.number_input(
                    label=":heavy_dollar_sign: Limite", min_value=0.00, max_value=cc_max_limit, step=0.01)
                inactive = st.selectbox(
                    label="Inativo", options=inactive_options.keys())
                confirm_values = st.checkbox(label="Confirmar Dados")

        send_data_button = st.button(
            label=":floppy_disk: Atualizar valores")

        if confirm_values and send_data_button:

            inactive = inactive_options[inactive]
            new_limit_query = '''UPDATE cartao_credito SET limite_credito = {}, inativo = '{}' WHERE nome_cartao = '{}' AND proprietario_cartao = '{}' AND documento_titular = {};'''.format(
                new_limit, inactive, card, user_name, user_document)

            with col2:
                with st.spinner(text='Aguarde...'):
                    sleep(2.5)

                    formatted_limit = Variable().treat_complex_string(
                        new_limit)

                    st.subheader(
                        body=":white_check_mark: Validação de Dados")
                    with st.expander(label="Avisos", expanded=True):
                        st.info(body="Novo limite: R$ {}".format(
                            formatted_limit))

                    QueryExecutor().update_table_unique_register(
                        new_limit_query, "Limite atualizado com sucesso!", "Erro ao atualizar limite:")

                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                    log_values = (
                        logged_user, "Registro", "Atualizou o limite do cartão {}.".format(card))
                    QueryExecutor().insert_query(
                        log_query, log_values, "Log gravado.", "Erro ao gravar log:")

    def update_credit_card_invoices(self):
        """
        Realiza o cadastro dos fechamentos de fatura do cartão de crédito.
        """
        user_name, user_document = Login().get_user_doc_name()

        col1, col2, col3 = st.columns(3)

        credit_cards = QueryExecutor().complex_consult_query(
            owner_cards_query)
        credit_cards = QueryExecutor().treat_numerous_simple_result(
            credit_cards, to_remove_list)

        if len(credit_cards) == 0:
            with col2:
                st.warning(
                    body="Você ainda não possui cartões cadastrados.")

        elif len(credit_cards) >= 1:
            with col1:
                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados da fatura", expanded=True):
                    card_name = st.selectbox(
                        label=":credit_card: Cartão", options=credit_cards)
                    card_number, owner_name, owner_document, card_code = Credit_Card().credit_card_key(
                        card=card_name)
                    year = st.selectbox(
                        label=":calendar: Ano", options=years)
                    month = st.selectbox(
                        label=":calendar: Mês", options=months)
                    beggining_invoice_date = st.date_input(
                        label=":calendar: Início da Fatura")
                    ending_invoice_date = st.date_input(
                        label=":calendar: Fim da Fatura")
                    confirm_invoice_data = st.checkbox(
                        label="Confirmar dados")

                register_invoice = st.button(
                    label=":floppy_disk: Registrar fechamento")

                if register_invoice and confirm_invoice_data == True:

                    credit_card_expire_date = QueryExecutor().simple_consult_query(query=credit_card_expire_date_query, params=(user_document, card_name, user_name))
                    credit_card_expire_date = QueryExecutor().treat_simple_result(credit_card_expire_date, to_remove_list)
                    credit_card_expire_date = credit_card_expire_date.split()
                    credit_card_expire_date_formatted = date(int(credit_card_expire_date[0]), int(credit_card_expire_date[1]), int(credit_card_expire_date[2]))
                    str_credit_card_expire_date_formatted = credit_card_expire_date_formatted.strftime('%d/%m/%Y')

                    with col2:

                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)

                        st.subheader(
                            body=":white_check_mark: Validação dos Dados")

                        with st.expander(label="Aviso", expanded=True):

                            if (beggining_invoice_date < ending_invoice_date) and beggining_invoice_date <= credit_card_expire_date_formatted and ending_invoice_date <= credit_card_expire_date_formatted:
                                st.success(body="Dados válidos.")
                                st.info(
                                    body=":credit_card: Cartão: {}".format(card_name))
                                st.info(
                                    body=":calendar: Mês: {}".format(month))
                                st.info(body=":calendar: Início da fatura: {}".format(
                                    beggining_invoice_date.strftime('%d/%m/%Y')))
                                st.info(body=":calendar: Fim da fatura: {}".format(
                                    ending_invoice_date.strftime('%d/%m/%Y')))

                                new_credit_card_invoice_query = """INSERT INTO fechamentos_cartao (nome_cartao, numero_cartao, documento_titular, ano, mes, data_comeco_fatura, data_fim_fatura) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                                new_credit_card_invoice_values = (
                                    card_name, card_number, owner_document, year, month, beggining_invoice_date, ending_invoice_date)

                                QueryExecutor().insert_query(
                                    new_credit_card_invoice_query, new_credit_card_invoice_values, "Fechamento cadastrado com sucesso!", "Erro ao cadastrar fechamento:")

                                log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                log_values = (
                                    logged_user, "Cadastro", "Cadastrou um fechamento do cartão {}.".format(card_name))
                                QueryExecutor().insert_query(
                                    log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            elif beggining_invoice_date > ending_invoice_date or beggining_invoice_date > credit_card_expire_date_formatted or ending_invoice_date > credit_card_expire_date_formatted:
                                if beggining_invoice_date >= ending_invoice_date:
                                    st.error(
                                        body="A data de ínicio da fatura não pode ser igual ou superior a data do fim da fatura.")
                                if beggining_invoice_date > credit_card_expire_date_formatted:
                                    st.error(
                                        body="A data de início da fatura não pode exceder a validade do cartão.")
                                    st.info(body="A data de validade do cartão é {}.".format(
                                        str_credit_card_expire_date_formatted))
                                if ending_invoice_date > credit_card_expire_date_formatted:
                                    st.error(
                                        body="A data de fim da fatura não pode exceder a validade do cartão.")
                                    st.info(body="A data de validade do cartão é {}.".format(
                                        str_credit_card_expire_date_formatted))
                                if beggining_invoice_date < ending_invoice_date:
                                    st.success(
                                        body="Datas da fatura válidas.")

                elif register_invoice and confirm_invoice_data == False:
                    with col2:
                        st.subheader(body="")
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        with st.expander(label="Aviso", expanded=True):
                            st.warning(
                                body="Confirme os dados antes de prosseguir.")

    def main_menu(self):
        """
        Exibe o menu.
        """

        cc_menu_options = {
            "Cadastrar cartão": self.get_new_credit_card,
            "Atualizar cartão": self.update_credit_card,
            "Atualizar vencimentos de fatura": self.update_credit_card_invoices
        }

        col1, col2, col3 = st.columns(3)

        with col3:
            cm_cl1, cm_cl2 = st.columns(2)

        with cm_cl2:
            cc_selected_option = st.selectbox(
                label="Menu", options=cc_menu_options)

        if cc_selected_option:
            call_function = cc_menu_options[cc_selected_option]
            call_function()
