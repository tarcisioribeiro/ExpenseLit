from datetime import datetime
from functions.credit_card import Credit_Card
from functions.get_balance import GetBalance
from functions.query_executor import QueryExecutor
from dictionary.sql import (
    fund_expense_query,
    fund_revenue_query,
    ticket_expense_query,
    ticket_revenue_query,
    loan_expense_query,
    debts_expense_query,
    most_categories_expenses_query,
    most_credit_card_expenses_query,
    most_categories_revenues_query,
    owner_active_cards_query
)
from dictionary.user_stats import user_name, user_sex
from dictionary.vars import to_remove_list, string_actual_month
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


class Home:

    def __init__(self):

        query_executor = QueryExecutor()

        def treat_complex_string(str_passed):

            list_to_treat = list(str_passed)
            point_position = list_to_treat.index(".")
            list_treated = list_to_treat[: point_position + 3]

            final_str = ""

            for i in range(0, len(list_treated)):
                final_str += list_treated[i]

            aux_list = list_treated[-2:]
            aux_str = ""
            if "." in aux_list:
                aux_str += aux_list[1] + "0"
            else:
                aux_str += aux_list[0] + aux_list[1]

            return final_str

        def mount_card_graph(selected_card: str):

            credit_card = Credit_Card()

            not_payed_expenses = credit_card.not_payed_card_expenses(selected_card="{}".format(selected_card))
            month_expenses = credit_card.month_expenses(selected_card, string_actual_month)
            future_expenses = credit_card.future_expenses(selected_card="{}".format(selected_card))
            card_limit = credit_card.card_limit(selected_card=selected_card)
            remaining_limit = credit_card.card_remaining_limit(selected_card)

            st.info(body="Cartão {}".format(selected_card))
            credit_card_data_df = pd.DataFrame(
                {
                    "Categoria": ["Faturas não pagas", "Mês Atual", "Futuro", "Limite Restante"],
                    "Valor": [
                        not_payed_expenses,
                        month_expenses,
                        future_expenses,
                        remaining_limit,
                    ],
                    "Porcentagem": [
                        (not_payed_expenses / card_limit) * 100 if card_limit != 0 else 0,
                        (month_expenses / card_limit) * 100 if card_limit != 0 else 0,
                        (future_expenses / card_limit) * 100 if card_limit != 0 else 0,
                        (remaining_limit / card_limit) * 100 if card_limit != 0 else 0,
                    ],
                }
            )
            credit_card_data_df["Valor"] = credit_card_data_df["Valor"].apply(lambda x: f"R$ {x:.2f}")
            credit_card_data_df["Porcentagem"] = credit_card_data_df["Porcentagem"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(credit_card_data_df, hide_index=True, use_container_width=True)

        def show_balance():

            call_balance = GetBalance()
            balance = call_balance.balance()
            accounts_list, accounts_balance, future_accounts_balance = call_balance.accounts_balance()
            last_revenues, last_expenses, max_revenue, max_expense = call_balance.list_values()

            str_balance = str(balance)
            final_str_balance = treat_complex_string(str_balance)

            ticket_revenue_ammount = query_executor.simple_consult_query(ticket_revenue_query)
            ticket_revenue_ammount = query_executor.treat_simple_result(ticket_revenue_ammount, to_remove_list)
            ticket_revenue_ammount = float(ticket_revenue_ammount)

            ticket_expense_ammount = query_executor.simple_consult_query(ticket_expense_query)
            ticket_expense_ammount = query_executor.treat_simple_result(ticket_expense_ammount, to_remove_list)
            ticket_expense_ammount = float(ticket_expense_ammount)

            ticket_ammount = ticket_revenue_ammount - ticket_expense_ammount
            str_ticket_ammount = str(ticket_ammount)
            final_str_ticket_ammount = treat_complex_string(str_ticket_ammount)

            fund_revenue_ammount = query_executor.simple_consult_query(fund_revenue_query)
            fund_revenue_ammount = query_executor.treat_simple_result(fund_revenue_ammount, to_remove_list)
            fund_revenue_ammount = float(fund_revenue_ammount)

            fund_expense_ammount = query_executor.simple_consult_query(fund_expense_query)
            fund_expense_ammount = query_executor.treat_simple_result(fund_expense_ammount, to_remove_list)
            fund_expense_ammount = float(fund_expense_ammount)

            fund_ammount = fund_revenue_ammount - fund_expense_ammount
            str_fund_ammount = str(fund_ammount)
            final_str_fund_ammount = treat_complex_string(str_fund_ammount)

            loan_ammount = query_executor.simple_consult_query(loan_expense_query)
            loan_ammount = query_executor.treat_simple_result(loan_ammount, to_remove_list)
            str_loan_ammount = str(loan_ammount)
            final_str_loan_ammount = treat_complex_string(str_loan_ammount)

            debts_ammount = query_executor.simple_consult_query(debts_expense_query)
            debts_ammount = query_executor.treat_simple_result(debts_ammount, to_remove_list)
            str_debts_ammount = str(debts_ammount)
            final_str_debts_ammount = treat_complex_string(str_debts_ammount)

            col1, col2, col3 = st.columns(3)

            with col2:
                
                col21, col22, col23 = st.columns(3)
                
                str_user_name = str(user_name)
                str_user_name = str_user_name.split(" ")

                with col22:

                    if user_sex == "F":
                        st.subheader(body="Bem vind{}, {}!".format("a", str_user_name[0]))
                    elif user_sex == "M":
                        st.subheader(body="Bem vind{}, {}!".format("o", str_user_name[0]))

            with col3:
                col31, col32, col33 = st.columns(3)

                with col32:
                    app_actual_date = datetime.now()
                    app_actual_date = app_actual_date.date()
                    st.info(body=":spiral_calendar_pad: {}".format(app_actual_date.strftime("%d/%m/%Y")))
                with col33:
                    app_actual_horary = datetime.now().strftime("%H:%M:%S")
                    st.info(body=":mantelpiece_clock: {}".format(app_actual_horary))

            st.divider()

            col4, col5, col6 = st.columns(3)

            with col4:
                st.subheader(body=":dollar: Saldos e Valores")

                with st.expander(label="Valores principais", expanded=True):
                    st.text(body="O seu saldo total é:", help="Valor considerando saldo em contas correntes.")
                    st.info(body=":heavy_dollar_sign: {}".format(final_str_balance))
                    st.text(body="Saldo de Vale Disponível:", help="Valor considerando saldo de vales alimentação e refeição.")
                    st.info(body=":heavy_dollar_sign: {}".format(final_str_ticket_ammount))
                    st.text(body="Fundo de garantia:", help="Valor considerando saldos de fundo de garantia.")
                    st.info(body=":heavy_dollar_sign: {}".format(final_str_fund_ammount))
                    st.text(body="Empréstimos não recebidos:", help="Valores de empréstimos realizados que ainda não recebidos.")
                    st.info(body=":heavy_dollar_sign: {}".format(final_str_loan_ammount))
                    st.text(body="Valores a pagar:", help="Dívidas e empréstimos contraídos que ainda não foram pagos.")
                    st.info(body=":heavy_dollar_sign: {}".format(final_str_debts_ammount))

                with st.expander(label="Contas", expanded=True):
                    if balance > 0 and len(accounts_balance) > 0:
                        balance_data_df = pd.DataFrame(
                            {
                                "Conta": accounts_list,
                                "Valor": accounts_balance,
                                "Valor Futuro": future_accounts_balance,
                            }
                        )

                        balance_data_df["Valor"] = balance_data_df["Valor"].apply(lambda x: f"R$ {x:.2f}")
                        balance_data_df["Valor Futuro"] = balance_data_df["Valor Futuro"].apply(lambda x: f"R$ {x:.2f}")
                        st.data_editor(balance_data_df, hide_index=True, use_container_width=True)

                    else:
                        st.info("Você ainda não possui contas.")

                with st.expander(label="Cartão de crédito", expanded=True):
                    cards_result = query_executor.complex_consult_query(owner_active_cards_query)
                    cards_result = query_executor.treat_numerous_simple_result(cards_result, to_remove_list)

                    if len(cards_result) == 0:
                        st.info(body="Você ainda não possui cartões.")

                    elif len(cards_result) >= 1 and cards_result[0] != "":
                        for i in range(0, len(cards_result)):
                            mount_card_graph(cards_result[i])

            with col5:
                st.subheader(body=":scroll: Registros")
                with st.expander(label=":scroll: Últimos registros", expanded=True):
                    st.info(body=":arrow_up_small: Últimas receitas")

                    if len(last_revenues) > 0:
                        revenue_df = pd.DataFrame(
                            last_revenues,
                            columns=[
                                "Descrição",
                                "Valor",
                                "Data",
                                "Categoria",
                                "Conta",
                            ],
                        )

                        revenue_df["Valor"] = revenue_df["Valor"].apply(lambda x: f"R$ {x:.2f}")
                        revenue_df["Data"] = pd.to_datetime(revenue_df["Data"]).dt.strftime("%d/%m/%Y")

                        st.dataframe(revenue_df, hide_index=True, use_container_width=True)
                    else:
                        st.warning(body="Você ainda não possui receitas registradas.")

                    st.info(body=":arrow_down_small: Últimas despesas")

                    if len(last_expenses) > 0:
                        expense_df = pd.DataFrame(
                            last_expenses,
                            columns=[
                                "Descrição",
                                "Valor",
                                "Data",
                                "Categoria",
                                "Conta",
                            ],
                        )
                        expense_df["Valor"] = expense_df["Valor"].apply(lambda x: f"R$ {x:.2f}")
                        expense_df["Data"] = pd.to_datetime(expense_df["Data"]).dt.strftime("%d/%m/%Y")
                        st.dataframe(expense_df, hide_index=True, use_container_width=True)
                    else:
                        st.warning(body="Você ainda não possui despesas registradas.")

                with st.expander(label=":scroll: Maiores registros", expanded=True):
                    st.info(body=":arrow_up_small: Maiores receitas")

                    if len(max_revenue) > 0:
                        max_revenue_df = pd.DataFrame(
                            max_revenue,
                            columns=[
                                "Descrição",
                                "Valor",
                                "Data",
                                "Categoria",
                                "Conta",
                            ],
                        )

                        max_revenue_df["Valor"] = max_revenue_df["Valor"].apply(lambda x: f"R$ {x:.2f}")
                        max_revenue_df["Data"] = pd.to_datetime(max_revenue_df["Data"]).dt.strftime("%d/%m/%Y")
                        st.dataframe(max_revenue_df, hide_index=True, use_container_width=True)

                    else:
                        st.warning(body="Você ainda não possui receitas registradas.")

                    st.info(body=":arrow_down_small: Maiores Despesas")

                    if len(max_expense) > 0:
                        max_expense_df = pd.DataFrame(
                            max_expense,
                            columns=[
                                "Descrição",
                                "Valor",
                                "Data",
                                "Categoria",
                                "Conta",
                            ],
                        )
                        max_expense_df["Valor"] = max_expense_df["Valor"].apply(lambda x: f"R$ {x:.2f}")
                        max_expense_df["Data"] = pd.to_datetime(max_expense_df["Data"]).dt.strftime("%d/%m/%Y")
                        st.dataframe(max_expense_df, hide_index=True, use_container_width=True)
                    else:
                        st.warning(body="Você ainda não possui despesas registradas.")

            with col6:
                st.subheader(body=":bar_chart: Gráficos")

                with st.expander(label=":bar_chart: Contas Correntes", expanded=True):
                    accounts_expense_graph = query_executor.complex_consult_query(most_categories_expenses_query)

                    if len(accounts_expense_graph) > 0:
                        account_df = pd.DataFrame(accounts_expense_graph, columns=["Valor", "Categoria"])
                        fig, ax = plt.subplots()
                        wedges, texts, autotexts = ax.pie(account_df["Valor"], labels=None, autopct="", startangle=90)
                        ax.axis("equal")
                        legend_labels = ["{} - {:.1f}%".format(category, (value / account_df["Valor"].sum()) * 100)
                            for category, value in zip(
                                account_df["Categoria"], account_df["Valor"]
                            )
                        ]
                        ax.legend(
                            wedges,
                            legend_labels,
                            title="Legenda",
                            loc="center left",
                            bbox_to_anchor=(1, 0.5),
                        )
                        ax.set_title("Despesas por Categoria - Contas Correntes")
                        st.pyplot(fig)
                    else:
                        st.warning(body="Você ainda não possui despesas registradas.")

                with st.expander(label=":bar_chart: Cartão de Crédito", expanded=True):
                    credit_card_expense_graph = query_executor.complex_consult_query(most_credit_card_expenses_query)

                    if len(credit_card_expense_graph) > 0:
                        credit_card_df = pd.DataFrame(credit_card_expense_graph, columns=["Valor", "Categoria"])
                        fig, ax = plt.subplots()
                        wedges, texts, autotexts = ax.pie(
                            credit_card_df["Valor"],
                            labels=None,
                            autopct="",
                            startangle=90,
                        )
                        ax.axis("equal")
                        legend_labels = [
                            "{} - {:.1f}%".format(category, (value / credit_card_df["Valor"].sum()) * 100)
                            for category, value in zip(
                                credit_card_df["Categoria"], credit_card_df["Valor"]
                            )
                        ]
                        ax.legend(
                            wedges,
                            legend_labels,
                            title="Legenda",
                            loc="center left",
                            bbox_to_anchor=(1, 0.5),
                        )
                        ax.set_title("Despesas por Categoria - Cartão de Crédito")

                        st.pyplot(fig)

                    else:
                        st.warning(body="Você ainda não possui despesas de cartão registradas.")

                with st.expander(label=":bar_chart: Contas Correntes", expanded=True):
                    accounts_revenue_graph = query_executor.complex_consult_query(most_categories_revenues_query)

                    if len(accounts_revenue_graph) > 0:
                        account_df = pd.DataFrame(accounts_revenue_graph, columns=["Valor", "Categoria"])
                        fig, ax = plt.subplots()
                        wedges, texts, autotexts = ax.pie(account_df["Valor"], labels=None, autopct="", startangle=90)
                        ax.axis("equal")
                        legend_labels = ["{} - {:.1f}%".format(category, (value / account_df["Valor"].sum()) * 100)
                            for category, value in zip(
                                account_df["Categoria"], account_df["Valor"]
                            )
                        ]
                        ax.legend(
                            wedges,
                            legend_labels,
                            title="Legenda",
                            loc="center left",
                            bbox_to_anchor=(1, 0.5),
                        )
                        ax.set_title("Receitas por Categoria")
                        st.pyplot(fig)

                    else:
                        st.warning(body="Você ainda não possui receitas registradas.")

        self.show_balance = show_balance