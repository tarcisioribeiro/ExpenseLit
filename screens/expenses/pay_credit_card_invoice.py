from dictionary.sql import owner_cards_query, card_invoices_query
from dictionary.vars import today, TO_REMOVE_LIST, actual_year
from functions.login import Login
from functions.credit_card import Credit_Card
from functions.get_actual_time import GetActualTime
from functions.query_executor import QueryExecutor
from functions.variable import Variable
from screens.reports.receipts import Receipts
from time import sleep
import pandas as pd
import streamlit as st


class CreditCardInvoice:
    """
    Classe que representa as faturas de cartão.
    """
    def get_credit_card_expenses_data(
        self,
        selected_card: str,
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
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        selected_card_linked_account_query = """
        SELECT
            DISTINCT(cc.conta_associada)
        FROM
            contas
        INNER JOIN
            cartao_credito AS cc
            ON contas.proprietario_conta = cc.proprietario_cartao
            AND contas.documento_proprietario_conta = cc.documento_titular
        WHERE
            cc.nome_cartao = %s
            AND contas.proprietario_conta = %s
            AND contas.documento_proprietario_conta = %s;
        """
        selected_card_linked_account = (
            QueryExecutor().simple_consult_query(
                selected_card_linked_account_query,
                params=(
                    selected_card,
                    user_name,
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
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )
        logged_user, logged_user_password = Login().get_user_data(
            return_option="user_login_password"
        )

        (
            month_year,
            month_name,
            month_abbreviation,
            selected_card_linked_account
        ) = self.get_credit_card_expenses_data(selected_card, selected_month)

        month_expenses = Credit_Card().month_expenses(
            selected_card,
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
                month_year, month_name
            )
            (
                descricao_list,
                valor_list,
                data_list,
                categoria_list,
                parcela_list
            ) = (
                Credit_Card().get_complete_card_month_expenses(
                    selected_card,
                    month_year,
                    month_name
                )
            )

            credit_card_month_expenses_list_df = pd.DataFrame({
                "Descrição": descricao_list,
                "Valor": valor_list,
                "Data": data_list,
                "Categoria": categoria_list,
                "Parcela": parcela_list, })
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
            expense_query = """
            INSERT INTO
                despesas (
                    descricao,
                    valor,
                    data,
                    horario,
                    categoria,
                    conta,
                    proprietario_despesa,
                    documento_proprietario_despesa,
                    pago
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            values = (
                description,
                month_expenses,
                today,
                actual_horary,
                "Fatura Cartão",
                selected_card_linked_account,
                user_name,
                user_document,
                "S"
            )

            update_invoice_query = '''
            UPDATE
                fechamentos_cartao
            SET fechado = 'S'
            WHERE nome_cartao = '{}'
                AND mes = '{}'
                AND ano = '{}'
                AND documento_titular = {};
            '''.format(
                selected_card,
                selected_month,
                actual_year,
                user_document
            )

            if confirm_values_checkbox and pay_button:
                QueryExecutor().update_table_registers(
                    "despesas_cartao_credito",
                    "despesa_cartao",
                    id_list
                )
                QueryExecutor().insert_query(
                    expense_query,
                    values,
                    "Fatura paga com sucesso!",
                    "Erro ao pagar fatura:"
                )
                QueryExecutor().update_table_unique_register(
                    update_invoice_query,
                    "Fatura fechada com sucesso!",
                    "Falha ao fechar fatura:"
                )

                str_value = Variable().treat_complex_string(month_expenses)

                log_query = '''
                INSERT INTO
                    financas.logs_atividades (
                        usuario_log,
                        tipo_log,
                        conteudo_log
                    )
                VALUES ( %s, %s, %s);
                '''
                log_values = (
                    logged_user,
                    "Registro",
                    """
                    Registrou uma despesa no valor de R$ {}
                    associada a conta {}.""".format(
                        str_value,
                        selected_card
                    )
                )
                QueryExecutor().insert_query(
                    log_query,
                    log_values,
                    "Log gravado.",
                    "Erro ao gravar log:"
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
                            id_list[0],
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
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )
        logged_user, logged_user_password = Login().get_user_data(
            return_option="user_login_password"
        )

        col1, col2, col3 = st.columns(3)

        user_cards = QueryExecutor().complex_consult_query(
            query=owner_cards_query,
            params=(user_name, user_document)
        )
        user_cards = QueryExecutor().treat_numerous_simple_result(
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
                params=(selected_card, user_name, user_document)
            )
            card_invoices_data = QueryExecutor().treat_numerous_simple_result(
                card_invoices_data, TO_REMOVE_LIST
            )

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
