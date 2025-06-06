from datetime import datetime
from dictionary.sql.account_queries import user_current_accounts_query
from dictionary.sql.expenses_queries import expenses_statement_query
from dictionary.sql.revenues_queries import revenues_statement_query
from dictionary.sql.user_queries import user_real_name_query
from dictionary.style import system_font
from dictionary.vars import ABSOLUTE_APP_PATH, TO_REMOVE_LIST, today
from fpdf import FPDF
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.query_executor import QueryExecutor
from time import sleep
import pandas as pd
import streamlit as st


user_id, user_document = Login().get_user_data()


class AccountStatement:
    """
    Classe que representa os extratos bancários das contas do usuário.
    """

    def consult_statement(
        self,
        statement_query_option: str,
        accounts: list,
        initial_data: str,
        final_data: str
    ):
        """
        Realiza a consulta do extrato bancário.

        Parameters
        ----------
        statement_query_option : str
            A opção de extrato selecionada pelo usuário.
        accounts : list
            Lista com as contas a serem consultadas.
        initial_data: str
            A data inicial da consulta.
        final_data: str
            A data final da consulta.

        Returns
        -------
        value_list : list
            A lista com os valores do extrato.
        data_df_list : list
            A lista com os gráficos estruturados.
        """

        value_list = []
        data_df_list = []

        placeholders = ", ".join(["%s"] * len(accounts))

        revenues_query = revenues_statement_query.replace(
            "IN %s", f"IN ({placeholders})"
        )
        expenses_query = expenses_statement_query.replace(
            "IN %s", f"IN ({placeholders})"
        )

        if statement_query_option == "Receitas e Despesas":
            empty_list = QueryExecutor().complex_compund_query(
                revenues_query,
                6,
                params=(
                    initial_data,
                    final_data,
                    *accounts,
                    user_id,
                    user_document
                )
            )
            description, value, date, time, category, account = (empty_list)

            if (
                len(description) == 0
                ) and (
                    len(value) == 0
                ) and (
                    len(date) == 0
                ) and (
                    len(time) == 0
                ) and (
                    len(category) == 0
                ) and (
                    len(account) == 0
            ):
                with st.expander(
                    label="Relatório de Receitas",
                    expanded=True
                ):
                    st.info(body="Nao há registros neste período.")

            elif (
                len(description) > 0
                ) and (
                    len(value) > 0
                ) and (
                    len(date) > 0
                ) and (
                    len(time) > 0
                ) and (
                    len(category) > 0
                ) and (
                    len(account) > 0
            ):
                aux_str = ""

                for i in range(0, len(time)):
                    aux_str = str(time[i])
                    time[i] = aux_str

                with st.expander(label="Relatório de Receitas", expanded=True):

                    data_df = pd.DataFrame(
                        {
                            "Descrição": description,
                            "Valor": value,
                            "Data": date,
                            "Horário": time,
                            "Categoria": category,
                            "Conta": account,
                        }
                    )

                    data_df["Valor"] = data_df["Valor"].apply(
                        lambda x: f"R$ {x:.2f}".replace(".", ",")
                    )
                    data_df["Data"] = pd.to_datetime(
                        data_df["Data"]
                    ).dt.strftime("%d/%m/%Y")
                    st.dataframe(
                        data_df,
                        hide_index=True,
                        use_container_width=True
                    )

                value_list.append(value)
                data_df_list.append(data_df)

            empty_list = QueryExecutor().complex_compund_query(
                expenses_query,
                6,
                params=(
                    initial_data,
                    final_data,
                    *accounts,
                    user_id,
                    user_document
                )
            )
            description, value, date, time, category, account = (empty_list)

            if (
                len(description) == 0
                ) and (
                    len(value) == 0
                ) and (
                    len(date) == 0
                ) and (
                    len(time) == 0
                ) and (
                    len(category) == 0
                ) and (
                    len(account) == 0
            ):
                with st.expander(
                    label="Relatório de Despesas",
                    expanded=True
                ):
                    st.info(body="Nao há registros neste período.")

            elif (
                len(description) > 0
                ) and (
                    len(value) > 0
                ) and (
                    len(date) > 0
                ) and (
                    len(time) > 0
                ) and (
                    len(category) > 0
                ) and (
                    len(account) > 0
            ):
                aux_str = ""

                for i in range(0, len(time)):
                    aux_str = str(time[i])
                    time[i] = aux_str

                with st.expander(label="Relatório de Despesas", expanded=True):

                    data_df = pd.DataFrame(
                        {
                            "Descrição": description,
                            "Valor": value,
                            "Data": date,
                            "Horário": time,
                            "Categoria": category,
                            "Conta": account,
                        }
                    )

                    data_df["Valor"] = data_df["Valor"].apply(
                        lambda x: f"R$ {x:.2f}".replace(".", ",")
                    )
                    data_df["Data"] = pd.to_datetime(
                        data_df["Data"]
                    ).dt.strftime("%d/%m/%Y")
                    st.dataframe(
                        data_df,
                        hide_index=True,
                        use_container_width=True
                    )

                value_list.append(value)
                data_df_list.append(data_df)

        if statement_query_option == "Receitas":
            empty_list = QueryExecutor().complex_compund_query(
                revenues_query,
                6,
                params=(
                    initial_data,
                    final_data,
                    *accounts,
                    user_id,
                    user_document
                )
            )
            description, value, date, time, category, account = (empty_list)

            if (
                len(description) == 0
                ) and (
                    len(value) == 0
                ) and (
                    len(date) == 0
                ) and (
                    len(time) == 0
                ) and (
                    len(category) == 0
                ) and (
                    len(account) == 0
            ):
                with st.expander(label="Relatório de Receitas", expanded=True):
                    st.info(body="Nao há registros neste período.")

            elif (
                len(description) > 0
                ) and (
                    len(value) > 0
                ) and (
                    len(date) > 0
                ) and (
                    len(time) > 0
                ) and (
                    len(category) > 0
                ) and (
                    len(account) > 0
            ):
                aux_str = ""

                for i in range(0, len(time)):
                    aux_str = str(time[i])
                    time[i] = aux_str

                with st.expander(label="Relatório de Receitas", expanded=True):

                    data_df = pd.DataFrame(
                        {
                            "Descrição": description,
                            "Valor": value,
                            "Data": date,
                            "Horário": time,
                            "Categoria": category,
                            "Conta": account,
                        }
                    )

                    data_df["Valor"] = data_df["Valor"].apply(
                        lambda x: f"R$ {x:.2f}".replace(".", ",")
                    )
                    data_df["Data"] = pd.to_datetime(
                        data_df["Data"]
                    ).dt.strftime("%d/%m/%Y")
                    st.dataframe(
                        data_df,
                        hide_index=True,
                        use_container_width=True
                    )

                value_list.append(value)
                data_df_list.append(data_df)

        if statement_query_option == "Despesas":
            empty_list = QueryExecutor().complex_compund_query(
                expenses_query,
                6,
                params=(
                    initial_data,
                    final_data,
                    *accounts,
                    user_id,
                    user_document
                )
            )
            description, value, date, time, category, account = (empty_list)

            if (
                len(description) == 0
                ) and (
                len(value) == 0
                ) and (
                    len(date) == 0
                ) and (
                    len(time) == 0
                ) and (
                    len(category) == 0
                ) and (
                    len(account) == 0
            ):
                with st.expander(label="Relatório de Despesas", expanded=True):
                    st.info(body="Nao há registros neste período.")

            elif (
                len(description) > 0
                ) and (
                    len(value) > 0
                ) and (
                    len(date) > 0
                ) and (
                    len(time) > 0
                ) and (
                    len(category) > 0
                ) and (
                    len(account) > 0
            ):
                aux_str = ""

                for i in range(0, len(time)):
                    aux_str = str(time[i])
                    time[i] = aux_str

                with st.expander(label="Relatório de Despesas", expanded=True):

                    data_df = pd.DataFrame(
                        {
                            "Descrição": description,
                            "Valor": value,
                            "Data": date,
                            "Horário": time,
                            "Categoria": category,
                            "Conta": account,
                        }
                    )

                    data_df["Valor"] = data_df["Valor"].apply(
                        lambda x: f"R$ {x:.2f}".replace(".", ",")
                    )
                    data_df["Data"] = pd.to_datetime(
                        data_df["Data"]
                    ).dt.strftime("%d/%m/%Y")
                    st.dataframe(
                        data_df,
                        hide_index=True,
                        use_container_width=True
                    )

                value_list.append(value)
                data_df_list.append(data_df)

        return value_list, data_df_list

    def generate_pdf(
            self,
            df: list,
            statement_type: str,
            initial_data: str,
            final_data: str,
            accounts: list
    ):
        """
        Gera o PDF do extrato bancário.

        Parameters
        ----------
        df : list
            A lista com os gráficos.
        statement_type : str
            O tipo de extrato bancário.
        initial_data : str
            A data inicial do extrato.
        final_data : str
            A data final do extrato.
        accounts : list
            Lista com as contas consultadas.

        Returns
        -------
        pdf: O PDF gerado pela função.
        """

        user_name = QueryExecutor().simple_consult_query(
            user_real_name_query,
            (user_id, user_document)
        )
        user_name = QueryExecutor().treat_simple_result(
            user_name,
            TO_REMOVE_LIST
        )

        unformatted_today = datetime.strptime(today, '%Y-%m-%d')
        formatted_today = unformatted_today.strftime('%d/%m/%Y')

        time = GetActualTime().get_actual_time()

        accounts_str = ""
        for item in range(0, len(accounts)):
            if item < (len(accounts) - 1):
                accounts_str = accounts_str + accounts[item] + ", "
            if item == len(accounts) - 1:
                accounts_str = accounts_str + accounts[item] + "."

        pdf = FPDF(orientation='L', unit="mm", format="A4")
        pdf.add_page()
        pdf.add_font(
            "SystemFont",
            "",
            "{}{}".format(ABSOLUTE_APP_PATH, system_font),
            uni=True
        )

        pdf.set_font("SystemFont", size=16)
        pdf.cell(
            0,
            10,
            "Relatório de {}".format(statement_type),
            ln=True,
            align="C"
        )
        pdf.ln(10)

        pdf.set_font("SystemFont", size=12)
        pdf.cell(
            0,
            5,
            "Período de consulta: {} à {}".format(
                initial_data,
                final_data
            ),
            ln=True
        )
        pdf.set_font("SystemFont", size=12)
        pdf.cell(
            0,
            10,
            "Contas consultadas: {}".format(accounts_str),
            ln=True
        )
        pdf.ln(5)

        statement_types = ["Receitas", "Despesas"]

        for i in range(0, len(df)):

            pdf.set_font("SystemFont", size=14)
            pdf.cell(0, 10, "{}".format(statement_types[i]), ln=True)
            pdf.ln(5)

            col_width = (pdf.w / len(df[i].columns)) * 0.85

            pdf.set_font("SystemFont", size=10)

            for col in df[i].columns:
                pdf.cell(col_width, 5, col, border=1, align="C")
            pdf.ln()
            pdf.set_font("SystemFont", size=10)
            for _, row in df[i].iterrows():
                for cell in row:
                    pdf.cell(col_width, 10, str(cell), border=1, align="C")
                pdf.ln()
            pdf.ln(10)

        pdf.cell(
            0,
            10,
            "Horário da consulta: {}, às {}.".format(formatted_today, time),
            align="R",
            ln=True
        )
        pdf.cell(
            0,
            10,
            "Nome do usuário: {}.".format(user_name),
            align="R",
            ln=True
        )
        pdf.ln(5)

        document_folder = ABSOLUTE_APP_PATH + "/data/account_statements/"
        document_type = "extrato_bancario"
        time = GetActualTime().get_actual_time()
        time = time.replace(":", "_")
        initial_data = initial_data.replace("/", "")
        final_data = final_data.replace("/", "")

        pdf_file_name = """{}{}_{}_{}_a_{}_{}.pdf""".format(
            document_folder,
            document_type,
            statement_type.replace(
                " ", "_"
            ).lower(),
            initial_data,
            final_data,
            time
        )

        pdf.output(pdf_file_name)

        return pdf_file_name

    def main_menu(self):
        """
        Menu principal.
        """

        user_current_accounts = QueryExecutor().complex_consult_query(
            query=user_current_accounts_query,
            params=(user_id, user_document)
        )
        user_current_accounts = QueryExecutor().treat_simple_results(
            user_current_accounts,
            TO_REMOVE_LIST
        )

        col4, col5, col6 = st.columns(3)

        if len(user_current_accounts) > 0:

            with col4:
                st.subheader(body=":computer: Entrada de Dados")
                with st.expander(label="Dados", expanded=True):
                    statement_option = st.selectbox(
                        label="Tipos de extrato",
                        options=[
                            "Selecione uma opção",
                            "Receitas",
                            "Despesas",
                            "Receitas e Despesas"
                        ]
                    )
                    selected_accounts = st.multiselect(
                        label="Contas",
                        options=user_current_accounts,
                        placeholder="Escolha a(s) conta(s)"
                    )
                    initial_data = st.date_input(label="Data de início")
                    final_data = st.date_input(label="Data de fim")
                    confirm_choice = st.checkbox(label="Confirmar dados")

                consult_tables = st.button(label=":chart: Gerar Relatórios")

            if confirm_choice and consult_tables:
                medium_value = 0

                with col5:
                    with st.spinner(text="Aguarde..."):
                        sleep(1.25)

                    st.subheader(body=":bar_chart: Resultados")

                    if (
                        statement_option != "Selecione uma opção"
                    ) and (
                        len(selected_accounts) > 0
                    ) and (
                        initial_data <= final_data
                    ):
                        value_list, dataframes = self.consult_statement(
                            statement_option,
                            selected_accounts,
                            initial_data,
                            final_data
                        )

                        with col6:
                            with st.spinner(text="Aguarde..."):
                                sleep(1.25)
                            st.subheader(
                                body=":information_source: Informações"
                            )

                            total_value = 0
                            counter = 0

                            for i in range(0, len(value_list)):
                                for j in range(0, len(value_list[i])):
                                    total_value += value_list[i][j]
                                    counter += 1
                                medium_value = round(
                                    (
                                        total_value / len(value_list[i])
                                    ), 2
                                )

                            medium_value = str(medium_value)
                            medium_value = medium_value.replace(".", ",")
                            total_value = str(total_value)
                            total_value = total_value.replace(".", ",")

                            with st.expander(label="Dados", expanded=True):
                                if statement_option in (
                                    'Receitas',
                                    'Despesas'
                                ):
                                    st.info(
                                        body="""
                                        Quantidade de {}: {}.
                                        """.format(
                                            statement_option.lower(),
                                            counter
                                        )
                                    )
                                    st.info(
                                        body="""
                                        Valor total das {}: R$ {}.
                                        """.format(
                                            statement_option.lower(),
                                            total_value
                                        )
                                    )
                                    st.info(
                                        body="""
                                        Valor médio das {}: R$ {}.
                                        """.format(
                                            statement_option.lower(),
                                            medium_value
                                        )
                                    )

                            formatted_initial_data = initial_data.strftime(
                                "%d/%m/%Y"
                            )
                            formatted_final_data = final_data.strftime(
                                "%d/%m/%Y"
                            )

                            log_values = (
                                user_id,
                                "Consulta",
                                """
                                Consultou o relatório de {}
                                entre o período de {} a {}.
                                """.format(
                                    statement_option,
                                    formatted_initial_data,
                                    formatted_final_data
                                )
                            )
                            QueryExecutor().register_log_query(
                                log_values,
                            )

                            pdf = self.generate_pdf(
                                dataframes,
                                statement_option,
                                formatted_initial_data,
                                formatted_final_data,
                                selected_accounts
                            )

                            with open(pdf, "rb") as file:
                                pdf_bytes = file.read()

                            st.download_button(
                                label=":floppy_disk: Baixar PDF",
                                data=pdf_bytes,
                                file_name=pdf,
                                mime="application/pdf",
                            )

                    elif (
                        len(
                            selected_accounts) == 0
                        ) or (
                            initial_data > final_data
                        ) or (
                            statement_option == "Selecione uma opção"
                    ):
                        with st.expander(label="Avisos", expanded=True):
                            if statement_option == "Selecione uma opção":
                                st.error(body="Selecione um tipo de extrato.")
                            if len(selected_accounts) == 0:
                                st.error(body="Nenhuma conta selecionada.")
                            if initial_data > final_data:
                                st.error(
                                    body="""
                                    A data inicial deve ser menor que a final.
                                    """
                                )

        elif len(user_current_accounts) == 0:
            with col5:
                st.warning(body="Você ainda não possui contas cadastradas.")
