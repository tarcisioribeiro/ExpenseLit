from dictionary.sql.credit_card_queries import (
    owner_cards_query,
    card_invoices_query,
    credit_card_id_query
)
from dictionary.sql.credit_card_expenses_queries import (
    update_invoice_query
)
from dictionary.sql.account_queries import (
    selected_card_linked_account_query
)
from dictionary.sql.expenses_queries import (
    insert_expense_query
)
from dictionary.vars import actual_year, TO_REMOVE_LIST, today
from functions.credit_card import Credit_Card
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep
import pandas as pd
import streamlit as st


user_id, user_document = Login().get_user_data()


class CreditCardInvoice:
    """
    Classe que representa as faturas de cartão.
    """
    def get_credit_card_expenses_data(
        self,
        selected_card: int,
        selected_month: str,
    ):
        """
        Realiza a consulta dos dados das despesas do cartão no mês.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado.
        selected_month: str
            O mês selecionado.

        Returns
        -------
        month_year : str
            O ano do mês selecionado.
        month_name : str
            O mês selecionado.
        month_abbreviation : str
            A abreviação do mês.
        selected_card_linked_account : str
            A conta vinculada ao cartão.
        """

        selected_card_linked_account = (
            QueryExecutor().simple_consult_query(
                selected_card_linked_account_query,
                params=(
                    selected_card,
                    user_id,
                    user_document
                )
            )
        )
        selected_card_linked_account = QueryExecutor().treat_simple_result(
            selected_card_linked_account,
            TO_REMOVE_LIST
        )

        month_data = selected_month.split()
        month_data.pop(1)
        month_data[1] = int(month_data[1])

        month_name = month_data[0]
        month_year = month_data[1]

        months_abbreviation_dictionary = {
            "Janeiro": "Jan",
            "Fevereiro": "Fev",
            "Março": "Mar",
            "Abril": "Abr",
            "Maio": "Mai",
            "Junho": "Jun",
            "Julho": "Jul",
            "Agosto": "Ago",
            "Setembro": "Set",
            "Outubro": "Out",
            "Novembro": "Nov",
            "Dezembro": "Dez"
        }
        month_abbreviation = months_abbreviation_dictionary[month_name]

        return (
            month_year,
            month_name,
            month_abbreviation,
            selected_card_linked_account
        )

    def show_expenses(
            self,
            selected_card: str,
            selected_month: str,
            column_disposition:
            any
    ):
        """
        Exibe as faturas de cartão que ainda não foram pagas.

        Parameters
        ----------
        selected_card : str
            O cartão de crédito selecionado pelo usuário.
        selected_month : str
            O mês da fatura selecionado pelo usuário.
        """
        selected_card_id = QueryExecutor().simple_consult_query(
            credit_card_id_query,
            (user_id, user_document, selected_card)
        )
        selected_card_id = QueryExecutor().treat_simple_result(
            selected_card_id,
            TO_REMOVE_LIST
        )
        selected_card_id = int(selected_card_id)

        (
            month_year,
            month_name,
            month_abbreviation,
            selected_card_linked_account
        ) = self.get_credit_card_expenses_data(
            selected_card_id,
            selected_month
        )

        month_expenses = Credit_Card().month_expenses(
            selected_card_id,
            month_year,
            month_name
        )

        str_month_expenses = Variable().treat_complex_string(month_expenses)

        if month_expenses == 0:
            with st.expander(label="Informação", expanded=True):
                st.info(
                    body="""
                    Você não tem valores a pagar neste cartão no mês de {}.
                    """.format(selected_month)
                )

        elif month_expenses > 0:
            id_list = Credit_Card().get_card_id_month_expenses(
                selected_card,
                month_year,
                month_name
            )
            (
                description_list,
                value_list,
                date_list,
                category_list,
                installment_list
            ) = (
                Credit_Card().get_complete_card_month_expenses(
                    selected_card,
                    month_year,
                    month_name
                )
            )

            credit_card_month_expenses_list_df = pd.DataFrame({
                "Descrição": description_list,
                "Valor": value_list,
                "Data": date_list,
                "Categoria": category_list,
                "Parcela": installment_list, })
            credit_card_month_expenses_list_df["Valor"] = (
                credit_card_month_expenses_list_df["Valor"].apply(
                    lambda x: f"R$ {x:.2f}".replace(".", ",")
                )
            )
            credit_card_month_expenses_list_df["Data"] = pd.to_datetime(
                credit_card_month_expenses_list_df["Data"]
            ).dt.strftime("%d/%m/%Y")

            st.subheader(
                body=":credit_card: Fatura de {}".format(selected_month)
            )

            with st.expander(label="Valores", expanded=True):
                st.info(
                    body="""
                    Valor total da fatura: :heavy_dollar_sign:{}
                    """.format(str_month_expenses)
                )
                st.data_editor(
                    credit_card_month_expenses_list_df,
                    hide_index=True,
                    use_container_width=True
                )
                confirm_values_checkbox = st.checkbox(
                    label="Confirmar valores"
                )

            description = "Fatura {}/{}".format(month_abbreviation, month_year)
            actual_horary = GetActualTime().get_actual_time()

            pay_button = st.button(label=":pencil: Pagar Fatura")

            values = (
                description,
                month_expenses,
                today,
                actual_horary,
                "Fatura Cartão",
                selected_card_linked_account,
                user_id,
                user_document,
                "S"
            )

            update_invoice_query.format(
                selected_card,
                selected_month,
                actual_year,
                user_document
            )

            if confirm_values_checkbox and pay_button:
                QueryExecutor().update_table_registers(
                    "despesas_cartao_credito",
                    id_list
                )
                QueryExecutor().insert_query(
                    insert_expense_query,
                    values,
                    "Fatura paga com sucesso!",
                    "Erro ao pagar fatura:"
                )
                QueryExecutor().update_unique_register(
                    update_invoice_query,
                    (
                        selected_card,
                        user_id,
                        user_document,
                        month_name,
                        month_year,
                        user_id,
                        user_document
                    ),
                    "Fatura fechada com sucesso!",
                    "Falha ao fechar fatura:"
                )

                str_value = Variable().treat_complex_string(month_expenses)

                log_values = (
                    user_id,
                    "Registro",
                    """
                    Registrou uma despesa no valor de R$ {}
                    associada a conta {}.""".format(
                        str_value,
                        selected_card
                    )
                )
                QueryExecutor().register_log_query(
                    log_values,
                )

                with column_disposition:
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)
                    st.subheader(
                        body=":pencil: Comprovante de Pagamento"
                    )
                    with st.expander(label="Arquivo", expanded=True):
                        Receipts().generate_receipt(
                            "despesas",
                            int(id_list[0]),
                            description="Fatura Cartão de {}".format(
                                selected_month
                            ),
                            value=month_expenses,
                            date=today,
                            category="Fatura Cartão",
                            account=selected_card_linked_account
                        )

    def main_menu(self):
        """
        Exibe as faturas de cartão que ainda não foram pagas.
        """

        col1, col2, col3 = st.columns(3)

        user_cards = QueryExecutor().complex_consult_query(
            query=owner_cards_query,
            params=(user_id, user_document)
        )
        user_cards = QueryExecutor().treat_simple_results(
            user_cards, TO_REMOVE_LIST
        )

        if len(user_cards) == 0:
            with col2:
                st.info(body="Você ainda não possui cartões cadastrados.")

        elif len(user_cards) >= 1:
            with col3:
                cl1, cl2 = st.columns(2)
                with cl2:
                    selected_card = st.selectbox(
                        label="Selecione o cartão",
                        options=user_cards
                    )

            card_invoices_data = QueryExecutor().complex_consult_query(
                query=card_invoices_query,
                params=(
                    selected_card,
                    user_id,
                    user_document,
                    user_id,
                    user_document
                    )
            )
            card_invoices_data = QueryExecutor().treat_simple_results(
                card_invoices_data, TO_REMOVE_LIST
            )
            if len(card_invoices_data) >= 1:

                with cl2:
                    selected_month = st.selectbox(
                        label="Selecione o mês", options=card_invoices_data
                    )

                with col1:
                    self.show_expenses(
                        selected_card,
                        selected_month,
                        column_disposition=col2
                    )

            elif len(card_invoices_data) == 0:
                with col2:
                    st.info(body=f"""
                            Não há faturas em aberto no cartão {selected_card}.
                            """)
