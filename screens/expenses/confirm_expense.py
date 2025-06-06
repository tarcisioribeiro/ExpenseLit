from datetime import datetime
from dictionary.vars import DECIMAL_VALUES, TO_REMOVE_LIST, today
from dictionary.sql.expenses_queries import (
    get_id_query,
    not_payed_expense_query,
    update_not_payed_query
)
from functions.query_executor import QueryExecutor
from functions.login import Login
from screens.reports.receipts import Receipts
from time import sleep
import pandas as pd
import streamlit as st


user_id, user_document = Login().get_user_data()


class ConfirmExpense:
    """
    Classe que representa a confirmação de despesas ainda não pagas.
    """

    def get_not_payed_expense_id(
        self,
        description: str,
        value: float,
        date: str,
        time: str,
        category: str,
        account: str
    ):
        """
        Realiza a consulta do id da despesa que ainda não foi paga.

        Parameters
        ----------
        description : str
            A descrição da despesa.
        value : float
            O valor da despesa.
        date : str
            A data da despesa.
        time : str
            O horário da despesa.
        category : str
            A categoria da despesa.
        account : str
            A conta na qual a despesa foi registrada.

        Returns
        -------
        id : int
            O ID da despesa não paga.
        """

        id = QueryExecutor().simple_consult_query(
            get_id_query,
            (
                description,
                value,
                date,
                time,
                category,
                account
            )
        )
        id = QueryExecutor().treat_simple_result(id, TO_REMOVE_LIST)
        id = int(id)

        return id

    def update_not_payed_expenses(self, id: int, new_date: str):
        """
        Atualiza a despesa não paga para constar como paga.

        Parameters
        ----------
        new_date : str
            A nova data da despesa.
        """

        QueryExecutor().update_unique_register(
            update_not_payed_query,
            (new_date, id),
            "Despesa atualizada com sucesso!",
            "Erro ao atualizar receita:"
        )

    def main_menu(self):
        """
        Exibe as despesas ainda não pagas.
        """

        col4, col5, col6 = st.columns(3)

        expense_values = QueryExecutor().complex_compund_query(
            query=not_payed_expense_query,
            list_quantity=7,
            params=(user_id, user_document)
        )

        if len(expense_values[0]) >= 1:

            with col4:
                st.subheader(body=":computer: Valores")

                with st.expander(label="Dados", expanded=True):

                    (
                        expense_id,
                        description,
                        value,
                        date,
                        time,
                        category,
                        account
                    ) = (expense_values)

                    time_list = []

                    for i in range(0, len(time)):
                        aux_time = QueryExecutor().treat_simple_result(
                            time[i],
                            TO_REMOVE_LIST
                        )
                        time_list.append(aux_time)

                    loan_data_df = pd.DataFrame(
                        {
                            "ID": expense_id,
                            "Descrição": description,
                            "Valor": value,
                            "Data": date,
                            "Horário": time_list,
                            "Categoria": category,
                            "Conta": account
                        }
                    )
                    loan_data_df["Valor"] = loan_data_df["Valor"].apply(
                        lambda x: f"R$ {x:.2f}".replace(".", ",")
                    )
                    loan_data_df["Data"] = pd.to_datetime(
                        loan_data_df["Data"]).dt.strftime(
                            "%d/%m/%Y"
                        )

                    st.dataframe(
                        loan_data_df,
                        hide_index=True,
                        use_container_width=True
                    )

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
                                "conta": final_str_account
                            }
                        )

                        formatted_data = str(index_description["data"])
                        formatted_data = datetime.strptime(
                            formatted_data,
                            "%Y-%m-%d"
                        )
                        formatted_data = formatted_data.strftime("%d/%m/%Y")

                        formatted_description = str(
                            index_description["descrição"]
                        ) + " - " + "R$ {}".format(
                            str(index_description["valor"]
                                ).replace(".", ",")) + (
                                    " - " + formatted_data
                                ) + " - " + str(
                            index_description["horario"]
                        ) + " - " + str(
                            index_description["categoria"]
                        ) + " - " + str(index_description["conta"])
                        description_list.append(formatted_description)

                    selected_revenue = st.selectbox(
                        label="Selecione a despesa",
                        options=description_list
                    )
                    print(selected_revenue)

                    confirm_selection = st.checkbox(label="Confirmar seleção")

                update_button = st.button(
                    label=":floppy_disk: Confirmar pagamento"
                )

                if confirm_selection and update_button:
                    with col5:
                        with st.spinner(text="Aguarde..."):
                            sleep(1.25)

                        st.subheader(
                            body=":white_check_mark: Validação de Dados"
                        )

                        final_description = str(index_description["descrição"])
                        final_value = float(index_description["valor"])
                        final_date = str(index_description["data"])
                        final_category = str(index_description["categoria"])
                        final_account = str(index_description["conta"])

                        str_final_value = str(final_value)
                        str_final_value = str_final_value.replace(".", ",")
                        last_two_digits = str_final_value[-2:]
                        if last_two_digits in DECIMAL_VALUES:
                            str_final_value = str_final_value + "0"

                        with st.subheader(
                            body="""
                            :white_check_mark: Validação de Dados
                            """
                        ):
                            with st.expander(label="Dados", expanded=True):
                                st.info(body="Descrição: {}".format(
                                    final_description
                                    )
                                )
                                st.info(
                                    body="""
                                    Valor: :heavy_dollar_sign: {}
                                    """.format(str_final_value))
                                st.info(
                                    body="Categoria: {}".format(
                                        final_category
                                    )
                                )
                                st.info(body="Conta: {}".format(final_account))

                    with col6:
                        st.subheader(body=":pencil: Comprovante")
                        with st.spinner(text="Aguarde..."):
                            sleep(1.25)

                        final_id = self.get_not_payed_expense_id(
                            description=index_description["descrição"],
                            value=index_description["valor"],
                            date=index_description["data"],
                            time=index_description["horario"],
                            category=index_description["categoria"],
                            account=index_description["conta"]
                        )

                        self.update_not_payed_expenses(
                            id=final_id,
                            new_date=today
                        )

                        Receipts().generate_receipt(
                            table="despesas",
                            id=final_id,
                            description=final_description,
                            value=final_value,
                            date=final_date,
                            category=final_category,
                            account=final_account
                        )

                        str_value = str(value)
                        str_value = str_value.replace(".", ",")
                        last_two_digits = str_value[-2:]
                        if last_two_digits in DECIMAL_VALUES:
                            str_value = str_value + "0"

                        log_values = (
                            user_id,
                            "Registro",
                            """
                            Registrou uma despesa no valor de R$ {}
                            associada a conta {}.
                            """.format(str_value, account))
                        QueryExecutor().register_log_query(
                            log_values,
                        )

                elif update_button and confirm_selection is False:
                    with col5:
                        st.subheader(body="")
                        with st.spinner(text="Aguarde..."):
                            sleep(1.25)
                        with st.expander(label="Aviso", expanded=True):
                            st.warning(
                                body="Confirme os dados antes de prosseguir."
                            )

        elif len(expense_values[0]) == 0:

            with col5:
                st.info(
                    body="Você não possui valores futuros a pagar."
                )
