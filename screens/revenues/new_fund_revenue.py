from data.cache.session_state import logged_user
from dictionary.sql import last_revenue_id_query, user_fund_accounts_query
from dictionary.user_stats import user_name, user_document
from dictionary.vars import to_remove_list
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep
import streamlit as st


class NewFundRevenue:
    """
    Classe que representa o cadastro de uma nova receita de fundo de garantia.
    """

    def get_user_fund_accounts(self):
        """
        Consulta as contas de fundo de garantia do usuário.

        Returns
        -------
        user_fund_accounts: list = A lista com as contas de fundo de garantia do usuário.
        """
        user_fund_accounts = QueryExecutor().complex_consult_query(
            user_fund_accounts_query)
        user_fund_accounts = QueryExecutor().treat_numerous_simple_result(
            user_fund_accounts, to_remove_list)
        return user_fund_accounts

    def main_menu(self):
        """
        Coleta os dados da nova receita de fundo de garantia.
        """

        user_fund_accounts = self.get_user_fund_accounts()

        col4, col5, col6 = st.columns(3)

        if len(user_fund_accounts) == 0:
            with col5:
                st.info(body="Você não possui fundos de garantia cadastrados.")

        elif len(user_fund_accounts) >= 1:

            with col4:

                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados", expanded=True):

                    id = QueryExecutor().simple_consult_query(
                        last_revenue_id_query)
                    id = QueryExecutor().treat_simple_result(
                        id, to_remove_list)
                    id = int(id) + 1

                    options = {
                        "Sim": "S",
                        "Não": "N"
                    }

                    description = st.text_input(
                        label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição", key="new_fund_description")
                    value = st.number_input(
                        label=":dollar: Valor", min_value=0.01)
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(label=":card_index_dividers: Categoria", options=[
                                            "Depósito", "Rendimentos"])
                    account = st.selectbox(
                        label=":bank: Conta", options=user_fund_accounts)
                    received = st.selectbox(
                        label=":inbox_tray: Recebido", options=options.keys())

                    confirm_values_check_box = st.checkbox(
                        label="Confirmar Dados")

            send_revenue_button = st.button(
                label=":pencil: Gerar Comprovante", key="send_revenue_button")

            with col6:
                if send_revenue_button and confirm_values_check_box:

                    received = options[received]

                    with col5:

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        st.subheader(body="Validação de Dados")

                        data_validation_expander = st.expander(
                            label="Informações", expanded=True)

                    if (
                        description != ""
                        and value >= 0.01
                        and date != ""
                        and category != "Selecione uma opção"
                        and account != "Selecione uma opção"
                    ):

                        with data_validation_expander:
                            st.success(body="Dados válidos.")

                        actual_horary = GetActualTime().get_actual_time()

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
                        QueryExecutor().insert_query(
                            revenue_query, values, "Receita registrada com sucesso!", "Erro ao registrar receita:")

                        str_value = Variable().treat_complex_string(value)

                        log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                        log_values = (logged_user, "Registro", "Registrou uma receita no valor de R$ {} associada a conta {}.".format(
                            str_value, account))
                        QueryExecutor().insert_query(
                            log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                        st.subheader(
                            body=":pencil: Comprovante de Receita")

                        with st.spinner("Aguarde..."):
                            sleep(2.5)

                        Receipts().generate_receipt(
                            'receitas', id, description, value, str(date), category, account)

                    else:
                        with data_validation_expander:
                            if description == '':
                                st.error(body="A descrição está vazia.")
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
