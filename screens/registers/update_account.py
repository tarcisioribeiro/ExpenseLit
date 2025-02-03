from dictionary.vars import accounts_type, today, actual_horary, to_remove_list, SAVE_FOLDER, decimal_values, special_caracters_dictionary, default_account_image
from dictionary.app_vars import account_models
from dictionary.sql import user_all_current_accounts_query
from functions.login import Login
from functions.query_executor import QueryExecutor
from PIL import Image
from time import sleep
import os
import streamlit as st


class UpdateAccounts:
    """
    Classe que representa o cadastro e atualização dos dados das contas do usuário.
    """

    def get_new_account(self):
        """
        Coleta os dados e cadastra uma nova conta.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.subheader(body=":computer: Entrada de Dados")

            with st.expander(label="Dados cadastrais", expanded=True):

                account_name = st.selectbox(
                    label=":lower_left_ballpoint_pen: Nome da conta", options=account_models)
                account_type = st.selectbox(
                    label=":card_index_dividers: Tipo da conta", options=accounts_type)
                get_account_first_value = st.number_input(
                    label=":heavy_dollar_sign: Valor inicial", step=0.01, min_value=0.01, help="Não é possível cadastrar uma conta sem um valor inicial.")
                get_account_image = st.file_uploader(label=":camera: Imagem da conta", type=[
                    'png', 'jpg'], help="O envio da imagem não é obrigatório.")
                confirm_values_ckecbox = st.checkbox(
                    label="Confirmar Dados")

            register_account = st.button(
                label=":floppy_disk: Registrar Conta")

            if confirm_values_ckecbox and register_account:
                with col2:
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)

                    st.subheader(
                        body=":white_check_mark: Validação de Dados")
                    data_expander = st.expander(
                        label="Dados", expanded=True)

                    with data_expander:
                        str_value = str(get_account_first_value)
                        str_value = str_value.replace(".", ",")
                        last_two_values = str_value[-2:]
                        if last_two_values in decimal_values:
                            str_value = str_value + "0"
                        st.info(
                            body="Nome da conta: {}".format(account_name))
                        st.info(
                            body="Tipo da conta: {}".format(account_type))
                        st.info(
                            body="Aporte inicial: :heavy_dollar_sign: {}".format(str_value))

                    if type(get_account_image).__name__ != "NoneType":
                        image = Image.open(get_account_image)
                        name, ext = os.path.splitext(default_account_image)

                        new_file_name = SAVE_FOLDER + name + ext
                        library_file_name = name + ext

                        save_path = os.path.join(
                            SAVE_FOLDER, new_file_name)
                        image.save(save_path)

                        with data_expander:
                            st.success(
                                body="A imagem foi salva em: {}".format(save_path))

                        insert_account_query = """INSERT INTO contas (nome_conta, tipo_conta, proprietario_conta, documento_proprietario_conta, caminho_arquivo_imagem) VALUES (%s, %s, %s, %s, %s)"""
                        new_account_values = (
                            account_name, account_type, user_name, user_document, library_file_name)
                        QueryExecutor().insert_query(
                            insert_account_query, new_account_values, "Conta cadastrada com sucesso!", "Erro ao cadastrar conta:")

                    elif type(get_account_image).__name__ == "NoneType":
                        library_file_name = default_account_image

                        insert_account_query = """INSERT INTO contas (nome_conta, tipo_conta, proprietario_conta, documento_proprietario_conta, caminho_arquivo_imagem) VALUES (%s, %s, %s, %s, %s)"""
                        new_account_values = (
                            account_name, account_type, user_name, user_document, library_file_name)
                        QueryExecutor().insert_query(
                            insert_account_query, new_account_values, "Conta cadastrada com sucesso!", "Erro ao cadastrar conta:")

                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                    log_values = (logged_user, "Cadastro",
                                  "Cadastrou a conta {}.".format(account_name))
                    QueryExecutor().insert_query(
                        log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                    new_account_first_revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_revenue_values = (
                        "Aporte Inicial", get_account_first_value, today, actual_horary, "Depósito", account_name, user_name, user_document, "S")

                    new_account_first_future_revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_future_revenue_values = (
                        "Aporte Inicial", 0, '2099-12-31', actual_horary, "Depósito", account_name, user_name, user_document, "N")

                    new_account_first_expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_expense_values = (
                        "Valor Inicial", 0, today, actual_horary, "Ajuste", account_name, user_name, user_document, "S")

                    new_account_first_future_expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    new_account_first_future_expense_values = (
                        "Valor Inicial", 0, '2099-12-31', actual_horary, "Ajuste", account_name, user_name, user_document, "N")

                    QueryExecutor().insert_query(new_account_first_revenue_query, new_account_first_revenue_values,
                                                 "Aporte inicial registrado com sucesso!", "Erro ao registrar aporte inicial:")
                    QueryExecutor().insert_query(new_account_first_future_revenue_query, new_account_first_future_revenue_values,
                                                 "Aporte inicial registrado com sucesso!", "Erro ao registrar aporte inicial:")
                    QueryExecutor().insert_query(new_account_first_expense_query, new_account_first_expense_values,
                                                 "Valor inicial registrado com sucesso!", "Erro ao registrar valor inicial:")
                    QueryExecutor().insert_query(new_account_first_future_expense_query, new_account_first_future_expense_values,
                                                 "Valor inicial registrado com sucesso!", "Erro ao registrar valor inicial:")

            elif confirm_values_ckecbox == False and register_account:
                with col3:
                    cm_cl1, cm_cl2 = st.columns(2)

                with cm_cl2:
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)
                    st.warning(
                        body="Revise e confirme os dados antes de prosseguir.")

    def update_account(self):
        """
        Realiza a atualização dos dados da conta do usuário.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col1, col2, col3 = st.columns(3)

        user_accounts = QueryExecutor().complex_consult_query(
            user_all_current_accounts_query)
        user_accounts = QueryExecutor().treat_numerous_simple_result(
            user_accounts, to_remove_list)

        options = {
            "Sim": "S",
            "Não": "N"
        }

        with col1:

            with st.expander(label="Dados", expanded=True):
                account_selected = st.selectbox(
                    label="Contas", options=user_accounts)
                account_type = st.selectbox(label="Tipo de conta", options=[
                                            "Conta Corrente", "Conta Móvel", "Fundo de Garantia", "Vale Alimentação"])
                innactive_selected_account = st.selectbox(
                    label="Inativar Conta", options=options.keys())
                confirm_account_checkbox = st.checkbox(
                    label="Confirmar dados")

            update_button = st.button(
                label=":floppy_disk: Atualizar conta")

            if update_button and confirm_account_checkbox:

                innactive_selected_account = options[innactive_selected_account]

                update_account_query = '''UPDATE contas SET inativa = '{}', tipo_conta = '{}' WHERE nome_conta = '{}' AND proprietario_conta = '{}' AND documento_proprietario_conta = {}'''.format(
                    innactive_selected_account, account_type, account_selected, user_name, user_document)
                QueryExecutor().update_table_unique_register(
                    update_account_query, "Conta atualizada com sucesso!", "Erro ao atualizar conta:")

                log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                log_values = (logged_user, "Atualização",
                              "Atualizou a conta {}.".format(account_selected))
                QueryExecutor().insert_query(
                    log_query, log_values, "Log gravado.", "Erro ao gravar log:")

    def main_menu(self):
        """
        Exibe o menu.
        """
        col1, col2, col3 = st.columns(3)

        with col3:
            cm_cl1, cm_cl2 = st.columns(2)

            with cm_cl2:
                account_selected_option = st.selectbox(
                    label="Menu", options=["Cadastrar Conta", "Atualizar Conta"])

        if account_selected_option == "Cadastrar Conta":
            self.get_new_account()

        if account_selected_option == "Atualizar Conta":
            self.update_account()
