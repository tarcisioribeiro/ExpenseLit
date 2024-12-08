from data.cache.session_state import logged_user
from datetime import datetime
from dictionary.sql import not_received_revenue_query
from dictionary.vars import to_remove_list
from functions.query_executor import QueryExecutor
from screens.reports.receipts import Receipts
from time import sleep
import pandas as pd
import streamlit as st


class ConfirmRevenue:

    def __init__(self):

        query_executor = QueryExecutor()
        receipt_executor = Receipts()

        def get_not_received_revenue_id(description: str, value: float, date: str, time: str, category: str, account: str):

            get_id_query = """SELECT id FROM receitas WHERE descricao = "{}" AND valor = {} AND data = "{}" AND horario = "{}" AND categoria = "{}" AND conta = "{}";""".format(description, value, date, time, category, account)
            id = query_executor.simple_consult_query(get_id_query)
            id = query_executor.treat_simple_result(id, to_remove_list)
            id = int(id)

            return id

        def update_not_received_revenues(id: int):

            update_not_received_query = """UPDATE receitas SET recebido = "S" WHERE id = {};""".format(id)
            query_executor.update_table_unique_register(update_not_received_query, "Receita atualizada com sucesso!", "Erro ao atualizar receita:")

        def show_not_received_values():

            col4, col5, col6 = st.columns(3)

            revenue_values = query_executor.complex_compund_query(not_received_revenue_query, 6, "not_received")

            if len(revenue_values[0]) >= 1:

                with col4:
                    st.subheader(body=":computer: Valores")

                    with st.expander(label="Dados", expanded=True):

                        description, value, date, time, category, account = (revenue_values)

                        loan_data_df = pd.DataFrame(
                            {
                                "Descrição": description,
                                "Valor": value,
                                "Data": date,
                                "Categoria": category,
                                "Conta": account,
                            }
                        )

                        loan_data_df["Valor"] = loan_data_df["Valor"].apply(
                            lambda x: f"R$ {x:.2f}".replace(".", ",")
                        )
                        loan_data_df["Data"] = pd.to_datetime(loan_data_df["Data"]).dt.strftime("%d/%m/%Y")

                        st.dataframe(loan_data_df, hide_index=True, use_container_width=True)

                        description_list = []

                        for i in range(0, len(description)):

                            index_description = {}
                            str_value = str(value[i])
                            str_date = str(date[i])
                            str_date = datetime.strptime(str_date, "%Y-%m-%d")
                            query_str_date = str_date.strftime("%Y-%m-%d")
                            final_str_account = str(account[i])

                            index_description.update(
                                {
                                    "descrição": description[i],
                                    "valor": str_value,
                                    "data": query_str_date,
                                    "horario": time[i],
                                    "categoria": category[i],
                                    "conta": final_str_account,
                                }
                            )

                            formatted_data = str(index_description["data"])
                            formatted_data = datetime.strptime(formatted_data, "%Y-%m-%d")
                            formatted_data = formatted_data.strftime("%d/%m/%Y")


                            formatted_description = str(index_description["descrição"]) + " - " + "R$ {}".format(str(index_description["valor"]).replace(".", ",")) + " - " + formatted_data + " - " + str(index_description["horario"]) + " - " + str(index_description["categoria"]) + " - " + str(index_description["conta"])

                            description_list.append(formatted_description)

                        selected_revenue = st.selectbox(label="Selecione a receita", options=description_list)

                        confirm_selection = st.checkbox(label="Confirmar seleção")

                    update_button = st.button(label=":floppy_disk: Receber valor")

                    if confirm_selection and update_button:

                        final_description = str(selected_revenue["descrição"])
                        final_value = float(selected_revenue["valor"])
                        final_date = str(selected_revenue["data"])
                        final_category = str(selected_revenue["categoria"])
                        final_account = str(selected_revenue["conta"])

                        with col5:
                            st.success(body="Sucesso!")

                        with col6:
                            
                            st.subheader(body="Comprovante")

                            with st.spinner(text="Aguarde..."):
                                sleep(2)

                            final_id = get_not_received_revenue_id(
                                description=selected_revenue["descrição"],
                                value=selected_revenue["valor"],
                                date=selected_revenue["data"],
                                time=selected_revenue["horario"],
                                category=selected_revenue["categoria"],
                                account=selected_revenue["conta"],
                            )
                            
                            update_not_received_revenues(id=final_id)

                            receipt_executor.generate_receipt(table="receitas",id=final_id,description=final_description,value=final_value,date=final_date,category=final_category,account=final_account)

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Registro", "Registrou uma receita no valor de R$ {} associada a conta {}.".format(value, account))
                            query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

            elif len(revenue_values[0]) == 0:

                with col5:
                    st.info("Você não possui valores a receber.")

        self.main_menu = show_not_received_values
