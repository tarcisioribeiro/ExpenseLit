import pandas as pd
import streamlit as st
from dictionary.style import system_font
from datetime import datetime
from dictionary.vars import (
    operational_system,
    today,
    actual_horary,
    TO_REMOVE_LIST,
    ABSOLUTE_APP_PATH,
    TRANSFER_IMAGE,
    SAVE_FOLDER
)
from dictionary.sql import user_current_accounts_query, account_image_query
from functions.query_executor import QueryExecutor
from functions.login import Login
from functions.variable import Variable
from PIL import Image, ImageDraw, ImageFont
from time import sleep


class Receipts:
    """
    Classe responsável pela geração e consulta de comprovantes.
    """

    def validate_query(self, table: str,
                       date: str, account: str, value: float):
        """
        Realiza a validação da consulta passada como consulta.

        Parameters
        ----------
        table : str
            A tabela da consulta.
        date : str
            A data da consulta.
        account : str
            A conta da consulta.
        value : float
            O valor da consulta.

        Returns
        -------
        ids_string : Any
            A string com os id's que correspondem a consulta,
            caso a mesma seja válida.
        boolean
            Se a consulta é válida.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        if table == "despesas":
            id_query = """
            SELECT
                despesas.id_despesa
            FROM
                despesas
                INNER JOIN usuarios ON
                    despesas.proprietario_despesa = usuarios.nome
                AND
                despesas.documento_proprietario_despesa = usuarios.documento
            WHERE
                despesas.data = '{}'
            AND despesas.conta = '{}'
            AND despesas.valor = {}
            AND usuarios.nome = '{}'
            AND usuarios.documento = {};""".format(
                date.strftime("%Y-%m-%d"),
                account, value, user_name, user_document)

        if table == "receitas":
            id_query = """
            SELECT
                receitas.id_receita
            FROM
                receitas
                INNER JOIN usuarios ON
                    receitas.proprietario_receita = usuarios.nome
                AND
                receitas.documento_proprietario_receita = usuarios.documento
            WHERE
                receitas.data = '{}'
            AND receitas.conta = '{}'
            AND receitas.valor = {}
            AND usuarios.nome = '{}'
            AND usuarios.documento = {};""".format(
                date.strftime("%Y-%m-%d"),
                account, value, user_name, user_document)

        if table == "despesas_cartao_credito":
            id_query = """
            SELECT
                dpscc.id_despesa_cartao
            FROM
            despesas_cartao_credito AS dpscc
                INNER JOIN
            usuarios AS users ON
            despesas_cartao_credito.proprietario_despesa_cartao = users.nome
            AND
            dpscc.doc_proprietario_cartao = users.documento
            WHERE
                dpscc.data = '{}'
            AND dpscc.cartao = '{}'
            AND dpscc.valor = {}
            AND users.nome = '{}'
            AND users.documento = {};""".format(
                date.strftime("%Y-%m-%d"),
                account, value, user_name, user_document)

        if table == "emprestimos":
            id_query = """
            SELECT
                emprestimos.id_emprestimo
            FROM
                emprestimos
                    INNER JOIN
                usuarios ON emprestimos.credor = usuarios.nome
                    AND emprestimos.documento_credor = usuarios.documento
            WHERE
                emprestimos.data = '{}'
            AND emprestimos.conta = '{}'
            AND emprestimos.valor = {}
            AND usuarios.nome = '{}'
            AND usuarios.documento = {};""".format(
                date.strftime("%Y-%m-%d"),
                account, value, user_name, user_document)

        id = QueryExecutor().complex_consult_brute_query(id_query)
        id = QueryExecutor().treat_numerous_simple_result(id, TO_REMOVE_LIST)

        if len(id) >= 1:
            return id, True

        elif len(id) == 0:
            return 0, False

    def execute_query(self, table: str, id_list: list):
        """
        Realiza a consulta informada.

        Parameters
        ----------
        table : str
            A tabela da consulta.
        id_list : list
            A lista com os ids da consulta.
        """
        placeholders = ", ".join(["%s"] * len(id_list))

        if table == "despesas_cartao_credito":
            values_query = """
            SELECT
                descricao, valor, data, horario, categoria, cartao
            FROM
                despesas_cartao_credito WHERE id_despesa_cartao IN %s;"""
            values_query = values_query.replace(
                "IN %s", f"IN ({placeholders})"
            )

        elif table == "receitas":
            values_query = """
            SELECT
                descricao, valor, data, horario, categoria, conta
            FROM
                receitas WHERE id_receita IN %s;"""
            values_query = values_query.replace(
                "IN %s", f"IN ({placeholders})"
            )

        elif table == "despesas":
            values_query = """
            SELECT
                descricao, valor, data, horario, categoria, conta
            FROM
                despesas WHERE id_despesa IN %s;"""
            values_query = values_query.replace(
                "IN %s", f"IN ({placeholders})"
            )

        consult_values = QueryExecutor().complex_compund_query(
            values_query, 6, params=(*id_list,)
        )

        return consult_values

    def treat_receipt_values(self, receipt_list: list):
        """
        Realiza o tratamento dos valores do comprovante.

        Parameters
        ----------
        receipt_list : list
            A lista com os valores do comprovante.

        Returns
        -------
        description_list : list
            A lista com a descrição do comprovante.
        value_list : list
            A lista com o valor do comprovante.
        date_list : list
            A lista com as datas do comprovante.
        time_list : list
            A lista com os horários do comprovante.
        category_list : list
            A lista com as categorias do comprovante.
        account_list : list
            A lista com as contas do comprovante.
        """

        len_lists_receipt = 0
        for i in range(0, len(receipt_list)):
            len_lists_receipt += len(receipt_list[i])

        if len(receipt_list) >= 5 and len_lists_receipt >= 5:

            description = receipt_list[0]
            description_list = []

            for i in range(0, len(description)):
                aux_description = QueryExecutor().treat_simple_result(
                    description[i], TO_REMOVE_LIST)
                description_list.append(aux_description)

            value = receipt_list[1]
            value_list = []

            for i in range(0, len(value)):
                aux_value = QueryExecutor().treat_simple_result(
                    value[i], TO_REMOVE_LIST)
                aux_value = float(aux_value)
                value_list.append(aux_value)

            date = receipt_list[2]
            date_list = []

            for i in range(0, len(date)):
                aux_date = QueryExecutor().treat_simple_result(
                    date[i], TO_REMOVE_LIST)
                aux_date = aux_date.replace(" ", "-")
                date_list.append(aux_date)

            time = receipt_list[3]
            time_list = []

            for i in range(0, len(time)):
                aux_time = QueryExecutor().treat_simple_result(
                    time[i], TO_REMOVE_LIST)
                aux_time = str(aux_time)
                time_list.append(aux_time)

            category = receipt_list[4]
            category_list = []

            for i in range(0, len(category)):
                aux_category = QueryExecutor().treat_simple_result(
                    category[i], TO_REMOVE_LIST)
                category_list.append(aux_category)

            account = receipt_list[5]
            account_list = []

            for i in range(0, len(account)):
                aux_account = QueryExecutor().treat_simple_result(
                    account[i], TO_REMOVE_LIST)
                account_list.append(aux_account)

            return (
                description_list,
                value_list,
                date_list,
                time_list,
                category_list,
                account_list
            )

    def generate_transfer_receipt(self, id: int, description: str,
                                  value: float, date: str, category: str,
                                  origin_account: str, destiny_account: str):
        """
        Gera o comprovante de transferência.

        Parameters
        ----------
        id : int
            O ID do registro do comprovante.
        description : str
            A descrição da transferência.
        value : float
            O valor da transferência.
        date : str
            A data da transferência.
        category : str
            A categoria da transferência.
        origin_account : str
            A conta de origem da transferência.
        destiny_account : str
            A conta de destino da transferência.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )
        origin_account_image = QueryExecutor().simple_consult_query(
            query=account_image_query,
            params=(origin_account, user_name, user_document)
        )
        origin_account_image = QueryExecutor().treat_simple_result(
            origin_account_image, TO_REMOVE_LIST
        )
        origin_account_image_path = SAVE_FOLDER + origin_account_image
        origin_pasted_image = Image.open(origin_account_image_path)

        destiny_account_image = QueryExecutor().simple_consult_query(
            query=account_image_query,
            params=(destiny_account, user_name, user_document)
        )
        destiny_account_image = QueryExecutor().treat_simple_result(
            destiny_account_image, TO_REMOVE_LIST)
        destiny_account_image_path = SAVE_FOLDER + destiny_account_image
        destiny_pasted_image = Image.open(destiny_account_image_path)

        loaded_TRANSFER_IMAGE = Image.open(TRANSFER_IMAGE)

        float_value = round(value, 2)

        str_value = Variable().treat_complex_string(float_value)

        reference_number = ""
        if id <= 9:
            reference_number = """REF: 000{}""".format(id)
        if id >= 10 and id <= 99:
            reference_number = """REF: 00{}""".format(id)
        if id >= 100 and id <= 999:
            reference_number = """REF: 0{}""".format(id)

        width, height = 900, 450
        dpi = 300
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        font_size = 20

        if operational_system == "nt":
            font = ImageFont.truetype("cour.ttf", font_size)
        elif operational_system == "posix":
            font = ImageFont.truetype("{}{}".format(
                ABSOLUTE_APP_PATH, system_font), font_size,
            )

        border_color = "black"
        border_width = 4
        border_box = [
            (border_width, border_width),
            (width - border_width, height - border_width),]
        draw.rectangle(border_box, outline=border_color, width=border_width)

        header_font_size = 20

        if operational_system == "nt":
            header_font = ImageFont.truetype("cour.ttf", header_font_size)
        elif operational_system == "posix":
            header_font = ImageFont.truetype("{}{}".format(
                ABSOLUTE_APP_PATH, system_font), font_size,)

        header_text = "Comprovante de Transferência"
        bbox = draw.textbbox((0, 0), header_text, font=header_font)
        header_text_width = bbox[2] - bbox[0]
        header_text_height = bbox[3] - bbox[1]
        print(header_text_height)

        header_position = ((width - header_text_width) / 2, 10)
        draw.text(header_position, header_text, fill="black", font=header_font)

        draw.line([(20, 40), (width - 20, 40)], fill="black", width=2)
        draw.text((20, 60), f"Descrição: {description}",
                  fill="black", font=font)
        draw.text((20, 90), f"Valor: R$ {str_value}",
                  fill="black", font=font)
        draw.text((20, 120), f"Data: {date.strftime('%d/%m/%Y')}",
                  fill="black", font=font)
        draw.text((20, 150), f"Categoria: {category}",
                  fill="black", font=font)
        draw.text((20, 180), f"Conta de Origem: {origin_account}",
                  fill="black", font=font)
        draw.text((20, 210), f"Conta de Destino: {destiny_account}",
                  fill="black", font=font)
        draw.line([(20, 240), (width - 20, 240)], fill="black", width=2)
        draw.line([(width - 400, height - 60),
                  (width - 20, height - 60)], fill="black", width=2)
        draw.text((520, 400), f"{user_name}", fill="black", font=font)
        draw.text((20, height - 40), reference_number, fill="black", font=font)

        image.paste(origin_pasted_image, (20, 250))
        image.paste(loaded_TRANSFER_IMAGE, (170, 250))
        image.paste(destiny_pasted_image, (320, 250))

        archive_path = "{}/data/transfers/Comprovante_transferencia_{}_{}.png"
        archive_path = archive_path.format(
            ABSOLUTE_APP_PATH, today, actual_horary
        )

        image.save(archive_path, dpi=(dpi, dpi))
        st.image(archive_path, use_container_width=True)

        with open(archive_path, "rb") as file:
            download_button = st.download_button(
                label=":floppy_disk: Baixar imagem",
                data=file,
                file_name=archive_path
            )
            print(download_button)

    def generate_receipt(
            self,
            table: str,
            id: int,
            description: str,
            value: float,
            date,
            category: str,
            account: str
    ):
        """
        Gera o comprovante de despesa/receita.

        Parameters
        ----------
        id : int
            O ID do registro do comprovante.
        description : str
            A descrição da despesa/receita.
        value : float
            O valor da despesa/receita.
        date : str
            A data da despesa/receita.
        category : str
            A categoria da despesa/receita.
        account : str
            A conta da despesa/receita.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        account_image = QueryExecutor().simple_consult_query(
            query=account_image_query,
            params=(account, user_name, user_document))
        account_image = QueryExecutor().treat_simple_result(
            account_image,
            TO_REMOVE_LIST
        )
        account_image_path = SAVE_FOLDER + account_image

        table_dictionary = {
            "receitas": "Receita",
            "emprestimos": "Empréstimo",
            "despesas": "Despesa",
            "despesas_cartao_credito": "Despesa de Cartão"
        }

        table = table_dictionary[table]
        value = round(value, 2)
        value = Variable().treat_complex_string(value)

        reference_number = ""
        if id <= 9:
            reference_number = """REF: 000{}""".format(id)
        if id >= 10 and id <= 99:
            reference_number = """REF: 00{}""".format(id)
        if id >= 100 and id <= 999:
            reference_number = """REF: 0{}""".format(id)

        table = table.capitalize()
        description = description.replace("'", "")
        category = category.capitalize()
        category = category.replace("'", "")
        account = account.replace("'", "")

        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.strftime("%d/%m/%Y")

        width, height = 800, 400
        dpi = 300
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        font_size = 20

        if operational_system == "nt":
            font = ImageFont.truetype("cour.ttf", font_size)
        elif operational_system == "posix":
            font = ImageFont.truetype("{}{}".format(
                ABSOLUTE_APP_PATH, system_font), font_size)

        border_color = "black"
        border_width = 4
        border_box = [(border_width, border_width),
                      (width - border_width, height - border_width)]
        draw.rectangle(border_box, outline=border_color, width=border_width)

        header_font_size = 20
        print(header_font_size)

        if operational_system == "nt":
            header_font = ImageFont.truetype("cour.ttf", font_size)
        elif operational_system == "posix":
            header_font = ImageFont.truetype("{}{}".format(
                ABSOLUTE_APP_PATH, system_font), font_size,)

        header_text = "Comprovante de {}".format(table)
        bbox = draw.textbbox((0, 0), header_text, font=header_font)
        header_text_width = bbox[2] - bbox[0]
        header_text_height = bbox[3] - bbox[1]
        print(header_text_height)

        header_position = ((width - header_text_width) / 2, 10)
        draw.text(header_position, header_text, fill="black", font=header_font)

        draw.line([(20, 40), (width - 20, 40)], fill="black", width=2)
        draw.text(
            (20, 60),
            f"Descrição: {description}",
            fill="black",
            font=font
        )
        draw.text((20, 90), f"Valor: R$ {value}", fill="black", font=font)
        draw.text((20, 120), f"Data: {date}", fill="black", font=font)
        draw.text((20, 150), f"Categoria: {category}", fill="black", font=font)
        draw.text((20, 180), f"Conta: {account}", fill="black", font=font)
        draw.line([(20, 210), (width - 20, 210)], fill="black", width=2)
        draw.line([(width - 400, height - 60),
                  (width - 20, height - 60)], fill="black", width=2)
        draw.text((400, 360), f"{user_name}", fill="black", font=font)
        draw.text((20, height - 40), reference_number, fill="black", font=font)

        pasted_image = Image.open(account_image_path)

        image.paste(pasted_image, (20, 220))

        archive_path = "{}/data/reports/Relatorio_{}_{}.png".format(
            ABSOLUTE_APP_PATH,
            today,
            actual_horary
        )
        image.save(archive_path, dpi=(dpi, dpi))
        st.image(archive_path, use_container_width=True)

        with open(archive_path, "rb") as file:
            download_button = st.download_button(
                label=":floppy_disk: Baixar imagem",
                data=file,
                file_name="Relatorio_{}_{}.png".format(today, actual_horary),)

            print(download_button)

    def main_menu(self):
        """
        Coleta os dados da consulta do comprovante.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )
        logged_user, logged_user_password = Login().get_user_data(
            return_option="user_login_password")

        col4, col5, col6 = st.columns(3)

        user_current_accounts = QueryExecutor().complex_consult_query(
            query=user_current_accounts_query,
            params=(user_name, user_document)
        )
        user_current_accounts = QueryExecutor().treat_numerous_simple_result(
            user_current_accounts, TO_REMOVE_LIST)

        if len(user_current_accounts) > 0:

            with col4:

                receipt_options = {
                    "Despesa": "despesas",
                    "Despesa de Cartão": "despesas_cartao_credito",
                    "Receita": "receitas",
                    "Empréstimo": "emprestimos"
                }

                st.subheader(body=":computer: Entrada de Dados")

                with st.expander(label="Filtros", expanded=True):
                    report_type = st.selectbox(
                        label="Relatório", options=receipt_options.keys())
                    date = st.date_input(label="Data")
                    account = st.selectbox(
                        label="Conta", options=user_current_accounts)
                    value = st.number_input(
                        label="Valor",
                        placeholder="Informe o valor",
                        min_value=0.01,
                        step=0.01
                    )
                    confirm_data = st.checkbox(label="Confirmar dados")

                if confirm_data:

                    table = receipt_options[report_type]

                    with col5:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(body=":page_facing_up: Resultados")

                        query_data, is_query_valid = self.validate_query(
                            table, date, account, value)

                        if is_query_valid:

                            with st.expander(label=":bar_chart: Resultados",
                                             expanded=True):

                                ids_string = ""
                                for i in range(0, len(query_data)):
                                    if i == (len(query_data) - 1):
                                        ids_string += "ID " + \
                                            str(query_data[i])
                                    else:
                                        ids_string += "ID " + \
                                            str(query_data[i]) + ", "

                                st.info(
                                    "Registro(s) encontrado(s): {}.".format(
                                        ids_string)
                                )

                                query = self.execute_query(table, query_data)
                                description, value, date, time, category, account = self.treat_receipt_values(query)

                                str_value_list = []

                                for i in range(0, len(value)):
                                    aux_value = Variable(
                                    ).treat_complex_string(value[i])
                                    aux_value = 'R$ ' + aux_value
                                    str_value_list.append(aux_value)

                                formatted_date_list = []

                                for i in range(0, len(date)):
                                    aux_date = date[i]
                                    aux_date = datetime.strptime(
                                        aux_date, '%Y-%m-%d')
                                    aux_date = aux_date.strftime('%d/%m/%Y')
                                    formatted_date_list.append(aux_date)

                                formatted_time_list = []

                                for i in range(0, len(time)):
                                    aux_time = time[i]
                                    formatted_time_list.append(aux_time)

                                str_ids_list = query_data

                                ids_list = []
                                for i in range(0, len(str_ids_list)):
                                    aux_int = int(str_ids_list[i])
                                    ids_list.append(aux_int)

                                data_df = pd.DataFrame(
                                    {
                                        "ID": ids_list,
                                        "Descrição": description,
                                        "Valor": str_value_list,
                                        "Data": formatted_date_list,
                                        "Horário": formatted_time_list,
                                        "Categoria": category,
                                        "Conta": account
                                    })

                                st.dataframe(data_df, hide_index=True,
                                             use_container_width=True)
                                select_id_register = st.selectbox(
                                    label="Selecione o ID do registro",
                                    options=ids_list
                                )
                                id_list_index = ids_list.index(
                                    select_id_register)

                                confirm_register_selection = st.checkbox(
                                    label="Confirmar seleção")

                            receipt_button = st.button(
                                label=":pencil: Gerar Comprovante")

                            if (confirm_register_selection and receipt_button):
                                with col6:
                                    with st.spinner(text="Aguarde..."):
                                        sleep(2.5)
                                    st.subheader(body=":pencil: Comprovante")
                                    self.generate_receipt(
                                        table,
                                        select_id_register,
                                        description[id_list_index],
                                        value[id_list_index],
                                        date[id_list_index],
                                        category[id_list_index],
                                        account[id_list_index]
                                    )

                                log_query = '''
                                    INSERT INTO
                                        financas.logs_atividades
                                        (usuario_log, tipo_log, conteudo_log)
                                    VALUES ( %s, %s, %s);
                                    '''
                                log_values = (
                                    logged_user,
                                    "Consulta",
                                    """Consultou comprovante de {} na data {},
                                        associado a conta {}.""".format(
                                        report_type,
                                        date,
                                        account
                                    )
                                )
                                QueryExecutor().insert_query(
                                    log_query,
                                    log_values,
                                    "Log gravado.",
                                    "Erro ao gravar log:"
                                )

                        elif is_query_valid is False:
                            with st.expander(
                                label="Resultados",
                                expanded=True
                            ):
                                st.info("Nenhum resultado Encontrado.")

        elif len(user_current_accounts) == 0:
            with col5:
                st.warning(body="Você ainda não possui contas cadastradas.")
