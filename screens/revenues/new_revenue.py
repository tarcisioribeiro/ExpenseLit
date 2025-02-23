from dictionary.vars import revenue_categories, to_remove_list
from dictionary.sql import last_revenue_id_query, user_current_accounts_query
from functions.query_executor import QueryExecutor
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep
import streamlit as st


class NewCurrentRevenue:
    """
    Classe que representa o cadastro de uma nova receita em contas correntes.
    """

    def get_user_current_accounts(self):
        """
        Consulta as contas correntes do usuário.

        Returns
        -------
        user_current_accounts : list
            A lista com as contas correntes do usuário.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")

        user_current_accounts = QueryExecutor().complex_consult_query(query=user_current_accounts_query, params=(user_name, user_document))
        user_current_accounts = QueryExecutor().treat_numerous_simple_result(user_current_accounts, to_remove_list)

        return user_current_accounts

    def main_menu(self):
        """
        Realiza a coleta dos dados da nova receita e a insere no banco de dados.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        user_current_accounts = self.get_user_current_accounts()

        col4, col5, col6 = st.columns(3)

        if len(user_current_accounts) == 0:
            with col5:
                st.info("Você ainda não possui contas correntes cadastradas.")

        elif len(user_current_accounts) >= 1:

            with col4:

                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados", expanded=True):

                    options = {
                        "Sim": "S",
                        "Não": "N"
                    }

                    id = QueryExecutor().simple_consult_brute_query(last_revenue_id_query)
                    id = QueryExecutor().treat_simple_result(id, to_remove_list)
                    id = int(id) + 1

                    description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição", max_chars=25, help="Descrição simples para a receita.")
                    value = st.number_input(
                        label=":dollar: Valor", min_value=0.01)
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(
                        label=":card_index_dividers: Categoria", options=revenue_categories)
                    account = st.selectbox(
                        label=":bank: Conta", options=user_current_accounts)
                    received = st.selectbox(
                        label=":inbox_tray: Recebido", options=options.keys())

                    confirm_values_check_box = st.checkbox(
                        label="Confirmar Dados")

                send_revenue_button = st.button(
                    label=":pencil: Gerar Comprovante", key="send_revenue_button")

            with col6:

                if confirm_values_check_box and send_revenue_button:

                    received = options[received]

                    with col5:
                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        st.subheader(
                            body=":white_check_mark: Validação de Dados")

                    if description != "" and category != "Selecione uma opção":
                        with col5:
                            with st.expander(label="Informações", expanded=True):
                                st.success(body="Dados Válidos.")

                        actual_horary = GetActualTime().get_actual_time()

                        revenue_query = "INSERT INTO receitas (descricao, valor, data, horario, categoria, conta, proprietario_receita, documento_proprietario_receita, recebido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        values = (description, value, date, actual_horary,
                                  category, account, user_name, user_document, received)
                        QueryExecutor().insert_query(
                            revenue_query, values, "Receita registrada com sucesso!", "Erro ao registrar receita:")

                        str_value = Variable().treat_complex_string(value)

                        log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                        log_values = (logged_user, "Registro", "Registrou uma receita no valor de R$ {} associada a conta {}.".format(
                            str_value, account))
                        QueryExecutor().insert_query(
                            log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        st.subheader(body=":pencil: Comprovante de Receita")
                        Receipts().generate_receipt(
                            'receitas', id, description, value, str(date), category, account)

                    elif description == "" or category == "Selecione uma opção":
                        with col5:
                            with st.expander(label="Informações", expanded=True):
                                if description == "":
                                    st.error(
                                        body="A descrição deve ser preenchida.")
                                if category == "Selecione uma opção":
                                    st.error(
                                        body="Informe uma categoria de receita.")
