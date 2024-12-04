from data.cache.session_state import logged_user
from dictionary.sql import last_revenue_id_query, user_fund_accounts_query
from dictionary.user_stats import user_name, user_document
from dictionary.vars import to_remove_list
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from screens.reports.receipts import Receipts
from time import sleep
import streamlit as st


class NewFundRevenue:
    """
    Classe responsável pelo cadastro de novas receitas provenientes de fundos de garantia.

    Attributes
    ----------
    new_fund_revenue()
        Apresenta a tela que receberá os dados da nova receita de fundo de garantia, a inserindo no banco de dados assim que o usuário confirmar seu cadastro.
    """

    def new_fund_revenue(self):
        """
        Apresenta a tela que receberá os dados da nova receita de fundo de garantia, a inserindo no banco de dados assim que o usuário confirmar seu cadastro.
        """

        query_executor = QueryExecutor()
        receipt_executor = Receipts()
        call_time = GetActualTime()

        user_fund_accounts = query_executor.complex_consult_query(
            user_fund_accounts_query
        )
        user_fund_accounts = query_executor.treat_numerous_simple_result(
            user_fund_accounts, to_remove_list
        )

        col4, col5, col6 = st.columns(3)

        if len(user_fund_accounts) == 0:
            with col5:
                st.info(body="Você não possui fundos de garantia cadastrados.")

        elif len(user_fund_accounts) >= 1:

            with col4:

                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Dados", expanded=True):

                    id = query_executor.simple_consult_query(last_revenue_id_query)
                    id = query_executor.treat_simple_result(id, to_remove_list)
                    id = int(id) + 1

                    description = st.text_input(
                        label=":lower_left_ballpoint_pen: Descrição",
                        placeholder="Informe uma descrição",
                        key="new_fund_description",
                    )
                    value = st.number_input(label=":dollar: Valor", min_value=0.01)
                    date = st.date_input(label=":date: Data")
                    category = st.selectbox(
                        label=":card_index_dividers: Categoria",
                        options=["Depósito", "Rendimentos"],
                    )
                    account = st.selectbox(
                        label=":bank: Conta", options=user_fund_accounts
                    )
                    received = st.selectbox(
                        label=":inbox_tray: Recebido", options=["S", "N"]
                    )

                    confirm_values_check_box = st.checkbox(label="Confirmar Dados")

            send_revenue_button = st.button(
                label=":pencil: Gerar Comprovante", key="send_revenue_button"
            )

            with col6:
                if send_revenue_button and confirm_values_check_box:

                    with col5:

                        with st.spinner("Aguarde..."):
                            sleep(1)

                        st.subheader(body="Validação de Dados")

                        data_validation_expander = st.expander(
                            label="Informações", expanded=True
                        )

                    if (
                        description != ""
                        and value >= 0.01
                        and date != ""
                        and category != "Selecione uma opção"
                        and account != "Selecione uma opção"
                    ):

                        with data_validation_expander:
                            st.success(body="Dados válidos.")

                        actual_horary = call_time.get_actual_time()

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
                            revenue_query,
                            values,
                            "Receita registrada com sucesso!",
                            "Erro ao registrar receita:",
                        )

                        log_query = """INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);"""
                        if received == "S":
                            log_values = (
                                logged_user,
                                "Registro",
                                "Registrou uma receita no valor de R$ {} associada a conta {}.".format(
                                    value, account
                                ),
                            )
                        elif received == "N":
                            log_values = (
                                logged_user,
                                "Registro",
                                "Registrou uma receita não recebida no valor de R$ {} associada a conta {}.".format(
                                    value, account
                                ),
                            )
                        query_executor.insert_query(
                            log_query,
                            log_values,
                            "Log gravado.",
                            "Erro ao gravar log:",
                        )

                        st.subheader(body=":pencil: Comprovante de receita")

                        with st.spinner("Aguarde..."):
                            sleep(1)

                        receipt_executor.generate_receipt(
                            "receitas",
                            id,
                            description,
                            value,
                            str(date),
                            category,
                            account,
                        )

                    else:
                        with data_validation_expander:
                            if description == "":
                                st.error(body="A descrição está vazia.")
                            if category == "Selecione uma opção":
                                st.error(body="Selecione uma categoria.")
