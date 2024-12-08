import mysql.connector
import streamlit as st
from data.cache.session_state import logged_user
from datetime import timedelta
from dictionary.db_config import db_config
from dictionary.vars import expense_categories, to_remove_list, decimal_values
from dictionary.sql import last_credit_card_expense_id_query, owner_cards_query
from functions.credit_card import Credit_Card
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from screens.reports.receipts import Receipts
from time import sleep


class NewCreditCardExpense:
    def __init__(self):

        call_credit_card = Credit_Card()
        query_executor = QueryExecutor()
        call_time = GetActualTime()

        receipt_executor = Receipts()

        def get_last_credit_card_expense_id():
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute(last_credit_card_expense_id_query)

                result = cursor.fetchone()

                if result is not None:
                    id = result[0]
                    return id
                else:
                    return 0

            except mysql.connector.Error as err:
                st.toast(f"Erro ao consultar o id da última despesa de cartão: {err}")
            finally:
                if connection.is_connected():
                    connection.close()

        def insert_new_credit_card_expense(query, values):
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                st.toast("Despesa registrada com sucesso.")
            except mysql.connector.Error as err:
                st.toast(f"Erro ao inserir despesa de cartão de crédito: {err}")
            finally:
                if connection.is_connected():
                    connection.close()

        def new_credit_card_expense():

            user_cards = query_executor.complex_consult_query(owner_cards_query)
            user_cards = query_executor.treat_numerous_simple_result(user_cards, to_remove_list)         

            col1, col2, col3 = st.columns(3)

            if len(user_cards) == 0:

                with col2:
                    st.info("Você ainda não possui cartões cadastrados.")

            elif len(user_cards) >= 1 and user_cards[0] != "Selecione uma opção":

                with col1:
                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Dados da despesa", expanded=True):

                        input_id = int(get_last_credit_card_expense_id()) + 1
                        description = st.text_input(label=":lower_left_ballpoint_pen: Descrição", placeholder="Informe uma descrição")
                        value = st.number_input(label=":dollar: Valor", step=0.01, min_value=0.01)
                        date = st.date_input(label=":date: Data")
                        category = st.selectbox(label=":card_index_dividers: Categoria", options=expense_categories)
                        card = st.selectbox(label=":credit_card: Cartão", options=user_cards)
                        remaining_limit = call_credit_card.card_remaining_limit(selected_card=card)

                        str_remaining_limit = str(remaining_limit)
                        str_remaining_limit = str_remaining_limit.replace(".", ",")

                        last_two_digits = str_remaining_limit[-2:]
                        if last_two_digits in decimal_values:
                            str_remaining_limit = str_remaining_limit + "0"

                        parcel = st.number_input(label=":pencil: Parcelas", min_value=1, step=1)
                        inputed_credit_card_code = st.number_input(label=":credit_card: Informe o código do cartão", step=1)

                        (
                            credit_card_number,
                            credit_card_owner,
                            credit_card_owner_document,
                            credit_card_code
                        ) = call_credit_card.credit_card_key(card=card)

                        confirm_values_checkbox = st.checkbox(label="Confirmar Dados")

                    generate_receipt_button = st.button(
                        label=":pencil: Gerar Comprovante", key="generate_receipt_button"
                    )


                with col3:
                    if confirm_values_checkbox and generate_receipt_button:

                        with col2:
                            
                            with st.spinner("Aguarde..."):
                                sleep(1)
                    
                            st.subheader(body="Validação de Dados")

                            data_expander = st.expander(label="Avisos", expanded=True)

                            with data_expander:
                                st.info(body="Limite restante do cartão: R$ {}".format(str_remaining_limit))

                        if (
                            description != ""
                            and value >= 0.01 and value <= remaining_limit
                            and date
                            and category != "Selecione uma opção"
                            and card != "Selecione uma opção"
                            and inputed_credit_card_code == credit_card_code
                        ):
                            with data_expander:
                                st.success(body="Dados válidos.")

                            st.subheader(body=":pencil: Comprovante de despesa de cartão")
                            with st.spinner("Aguarde..."):
                                sleep(1)

                            for i in range(0, parcel):
                                if i >= 1:
                                    date += timedelta(days=30)

                                actual_horary = call_time.get_actual_time()

                                credit_card_expense_query = "INSERT INTO despesas_cartao_credito (descricao, valor, data, horario, categoria, cartao, numero_cartao, proprietario_despesa_cartao, doc_proprietario_cartao, parcela, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                values = (
                                    description,
                                    (value / parcel),
                                    date,
                                    actual_horary,
                                    category,
                                    card,
                                    credit_card_number,
                                    credit_card_owner,
                                    credit_card_owner_document,
                                    i + 1,
                                    "N",
                                )
                                insert_new_credit_card_expense(credit_card_expense_query, values)

                                log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                log_values = (logged_user, "Registro", "Registrou uma despesa de cartão no valor de R$ {} associada a conta {}.".format(value, card))
                                query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            receipt_executor.generate_receipt('despesas_cartao_credito', input_id, description, value, str(date), category, card)

                        else:
                            with data_expander:
                                if value > remaining_limit:
                                    st.error(body="O valor da despesa é maior que o limite restante.")
                                if description == "":
                                    st.error(body="A descrição está vazia.")
                                if category == "Selecione uma opção":
                                    st.error(body="Selecione uma categoria.")
                                if inputed_credit_card_code != credit_card_code:
                                    st.error(body="Código do cartão inválido.")

        self.main_menu = new_credit_card_expense
        self.insert_credit_card_expense = insert_new_credit_card_expense
