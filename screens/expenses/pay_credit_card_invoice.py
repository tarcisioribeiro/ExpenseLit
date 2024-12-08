from data.cache.session_state import logged_user, logged_user_password
from dictionary.sql import owner_cards_query, card_invoices_query
from dictionary.vars import today, to_remove_list, actual_year, decimal_values
from dictionary.user_stats import user_name, user_document
from functions.credit_card import Credit_Card
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep
import pandas as pd
import streamlit as st


class CreditCardInvoice:
    def __init__(self):
        credit_card = Credit_Card()
        generate_receipt = Receipts()
        query_executor = QueryExecutor()
        call_time = GetActualTime()
        variable = Variable()

        def show_expenses(selected_card: str, selected_month: str):
        
            month_data = selected_month.split()
            month_data.pop(1)
            month_data[1] = int(month_data[1])

            month_name = month_data[0]
            month_year = month_data[1]

            month_expenses = credit_card.month_expenses(selected_card, month_year, month_name)

            str_month_expenses = str(month_expenses)
            str_month_expenses = str_month_expenses.replace(".", ",")
            last_two_digits = str_month_expenses[-2:]
            if last_two_digits in decimal_values:
                str_month_expenses = str_month_expenses + "0"

            if month_expenses == 0:
                with st.expander(label="Informação",expanded=True):
                    st.info(body="Você não tem valores a pagar neste cartão no mês de {}.".format(selected_month))

            elif month_expenses > 0:
                id_list = credit_card.get_card_id_month_expenses(selected_card, month_year, month_name)
                descricao_list, valor_list, data_list, categoria_list, parcela_list = (credit_card.month_complete_expenses(selected_card, month_year, month_name))

                credit_card_month_expenses_list_df = pd.DataFrame({"Descrição": descricao_list, "Valor": valor_list, "Data": data_list, "Categoria": categoria_list, "Parcela": parcela_list,})
                credit_card_month_expenses_list_df["Valor"] = (credit_card_month_expenses_list_df["Valor"].apply(lambda x: f"R$ {x:.2f}".replace(".", ",")))
                credit_card_month_expenses_list_df["Data"] = pd.to_datetime(credit_card_month_expenses_list_df["Data"]).dt.strftime("%d/%m/%Y")         

                st.subheader(body=":credit_card: Fatura de {}".format(selected_month))

                with st.expander(label="Valores", expanded=True):
                    st.info(body="Valor total da fatura: :heavy_dollar_sign:{}".format(str_month_expenses))
                    st.data_editor(credit_card_month_expenses_list_df, hide_index=True, use_container_width=True)
                    confirm_values_checkbox = st.checkbox(label="Confirmar valores")

                description = "Fatura de Cartão Mês de {}".format(selected_month)
                actual_horary = call_time.get_actual_time()

                pay_button = st.button(label=":pencil: Pagar Fatura")
                expense_query = "INSERT INTO despesas (descricao, valor, data, horario, categoria, conta, proprietario_despesa, documento_proprietario_despesa, pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (description, month_expenses, today, actual_horary, "Fatura Cartão", selected_card, user_name, user_document, "S")

                update_invoice_query = '''UPDATE fechamentos_cartao SET fechado = 'S' WHERE nome_cartao = '{}' AND mes = '{}' AND ano = '{}' AND documento_titular = {};'''.format(selected_card, selected_month, actual_year, user_document)
                    
                if confirm_values_checkbox and pay_button:
                    query_executor.update_table_registers("despesas_cartao_credito", "despesa_cartao", id_list)
                    query_executor.insert_query(expense_query, values, "Fatura paga com sucesso!", "")
                    query_executor.update_table_unique_register(update_invoice_query, "Fatura fechada com sucesso!", "Falha ao fechar fatura:")

                    log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                    log_values = (logged_user, "Registro", "Registrou uma despesa no valor de R$ {} associada a conta {}.".format(month_expenses, selected_card))
                    query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)

                    st.subheader(body="Comprovante")
                    with st.expander(label="Arquivo", expanded=True):
                        generate_receipt.generate_receipt("despesas", id_list[0], description="Fatura Cartão de {}".format(selected_month), value=month_expenses, date=today, category="Fatura Cartão", account=selected_card)


        def show_update_credit_card_invoices():

            col1, col2, col3 = st.columns(3)

            user_cards = query_executor.complex_consult_query(owner_cards_query)
            user_cards = query_executor.treat_numerous_simple_result(user_cards, to_remove_list)

            if len(user_cards) == 0:
                with col2:
                    st.info(body="Você ainda não possui cartões cadastrados.")

            elif len(user_cards) >= 1:
                with col3:
                    cl1, cl2 = st.columns(2)
                    with cl2:
                        selected_card = st.selectbox(label="Selecione o cartão", options=user_cards)

                complete_card_invoices_query = card_invoices_query.format(selected_card, logged_user, logged_user_password)
                card_invoices_data = query_executor.complex_consult_query(complete_card_invoices_query)
                card_invoices_data = query_executor.treat_numerous_simple_result(card_invoices_data, to_remove_list)

                with cl2:
                    selected_month = st.selectbox(label="Selecione o mês", options=card_invoices_data)

                with col1:
                    show_expenses(selected_card, selected_month)

        self.main_menu = show_update_credit_card_invoices
