import pandas as pd
import streamlit as st
from data.cache.session_state import logged_user, logged_user_password
from datetime import datetime
from dictionary.vars import (
    accounts,
    accounts_images_paths,
    operational_system,
    today,
    actual_horary,
    to_remove_list,
    absolute_app_path,
    accounts_images,
    transfer_image
)
from functions.query_executor import QueryExecutor
from PIL import Image, ImageDraw, ImageFont
from time import sleep


class Receipts:
    def __init__(self):

        query_executor = QueryExecutor()

        def validate_query(table, date, account, value):
            if table == "despesas":
                id_query = """
                            SELECT 
                                despesas.id_despesa
                            FROM
                                despesas
                                INNER JOIN usuarios ON despesas.proprietario_despesa = usuarios.nome AND despesas.documento_proprietario_despesa = usuarios.cpf
                            WHERE
                                despesas.data = '{}'
                                    AND despesas.conta = '{}'
                                    AND despesas.valor = {}
                                    AND usuarios.login = '{}'
                                    AND usuarios.senha = '{}';""".format(
                    date.strftime("%Y-%m-%d"),
                    account,
                    value,
                    logged_user,
                    logged_user_password,
                )

            if table == "receitas":
                id_query = """
                            SELECT 
                                receitas.id_receita
                            FROM
                                receitas
                                INNER JOIN usuarios ON receitas.proprietario_receita = usuarios.nome AND receitas.documento_proprietario_receita = usuarios.cpf
                            WHERE
                                receitas.data = '{}'
                                    AND receitas.conta = '{}'
                                    AND receitas.valor = {}
                                    AND usuarios.login = '{}'
                                    AND usuarios.senha = '{}';""".format(
                    date.strftime("%Y-%m-%d"),
                    account,
                    value,
                    logged_user,
                    logged_user_password,
                )

            if table == "despesas_cartao_credito":
                id_query = """
                                SELECT 
                                    despesas_cartao_credito.id_despesa_cartao
                                FROM
                                    despesas_cartao_credito
                                        INNER JOIN
                                    usuarios ON despesas_cartao_credito.proprietario_despesa_cartao = usuarios.nome
                                        AND despesas_cartao_credito.doc_proprietario_cartao = usuarios.cpf
                                WHERE
                                    despesas_cartao_credito.data = '{}'
                                        AND despesas_cartao_credito.cartao = '{}'
                                        AND despesas_cartao_credito.valor = {}
                                        AND usuarios.login = '{}'
                                        AND usuarios.senha = '{}';""".format(
                    date.strftime("%Y-%m-%d"),
                    account,
                    value,
                    logged_user,
                    logged_user_password,
                )

            if table == "emprestimos":
                id_query = """
                                SELECT 
                                    emprestimos.id_emprestimo
                                FROM
                                    emprestimos
                                        INNER JOIN
                                    usuarios ON emprestimos.credor = usuarios.nome
                                        AND emprestimos.documento_credor = usuarios.cpf
                                WHERE
                                    emprestimos.data = '{}'
                                        AND emprestimos.conta = '{}'
                                        AND emprestimos.valor = {}
                                        AND usuarios.login = '{}'
                                        AND usuarios.senha = '{}';""".format(
                    date.strftime("%Y-%m-%d"),
                    account,
                    value,
                    logged_user,
                    logged_user_password,
                )

            data_exists = False

            id = query_executor.simple_consult_query(id_query)
            id = query_executor.treat_simple_result(id, to_remove_list)

            if id is not None:
                data_exists = True
            else:
                data_exists = False

            return id, data_exists

        def execute_query(table, id):

            if table == "despesas_cartao_credito":
                values_query = """SELECT id_despesa_cartao, descricao, valor, data, categoria, cartao FROM {} WHERE id_despesa_cartao = {};""".format(table, id)
            elif table == "receitas":
                values_query = """SELECT id_receita, descricao, valor, data, categoria, conta FROM {} WHERE id_receita = {};""".format(table, id)
            elif table == "despesas":
                values_query = """SELECT id_despesa, descricao, valor, data, categoria, conta FROM {} WHERE id_despesa = {};""".format(table, id)

            consult_values = query_executor.complex_compund_query(values_query, 6, "query_values")

            return consult_values

        def treat_receipt_values(receipt_list):

            len_lists_receipt = 0
            for i in range(0, len(receipt_list)):
                len_lists_receipt += len(receipt_list[i])

            if len(receipt_list) >= 5 and len_lists_receipt >= 5:

                id = receipt_list[0]
                id = query_executor.treat_simple_result(id, to_remove_list)
                id = int(id)

                description = receipt_list[1]
                description = query_executor.treat_simple_result(description, to_remove_list)

                value = receipt_list[2]
                value = query_executor.treat_simple_result(value, to_remove_list)
                value = float(value)

                date = receipt_list[3]
                date = query_executor.treat_simple_result(date, to_remove_list)
                date = date.replace(" ", "-")

                category = receipt_list[4]
                category = query_executor.treat_simple_result(category, to_remove_list)

                account = receipt_list[5]
                account = query_executor.treat_simple_result(account, to_remove_list)

                return id, description, value, date, category, account
            
            else:
                return 0, '', 0, '1999-12-31', '', '' 

        def generate_transfer_receipt(id, description, value, date, category, origin_account, destiny_account):
            reference_number = ""
            if id <= 9:
                reference_number = """REF: 000{}""".format(id)
            if id >= 10 and id <= 99:
                reference_number = """REF: 00{}""".format(id)
            if id >= 100 and id <= 999:
                reference_number = """REF: 0{}""".format(id)

            origin_pasted_image = ""
            if origin_account == "Ben Visa Vale":
                origin_pasted_image = accounts_images[0]
            elif origin_account == "Caixa":
                origin_pasted_image = accounts_images[1]
            elif origin_account == "Carteira":
                origin_pasted_image = accounts_images[2]
            elif origin_account == "Mercado Pago":
                origin_pasted_image = accounts_images[3]
            elif origin_account == "Nubank":
                origin_pasted_image = accounts_images[4]
            elif origin_account == "Picpay":
                origin_pasted_image = accounts_images[5]
            elif origin_account == "Sicoob":
                origin_pasted_image = accounts_images[6]

            destiny_pasted_image = ""
            if destiny_account == "Ben Visa Vale":
                destiny_pasted_image = accounts_images[0]
            elif destiny_account == "Caixa":
                destiny_pasted_image = accounts_images[1]
            elif destiny_account == "Carteira":
                destiny_pasted_image = accounts_images[2]
            elif destiny_account == "Mercado Pago":
                destiny_pasted_image = accounts_images[3]
            elif destiny_account == "Nubank":
                destiny_pasted_image = accounts_images[4]
            elif destiny_account == "Picpay":
                destiny_pasted_image = accounts_images[5]
            elif destiny_account == "Sicoob":
                destiny_pasted_image = accounts_images[6]

            width, height = 800, 400
            dpi = 300
            image = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(image)
            font_size = 16

            if operational_system == "nt":
                font = ImageFont.truetype("cour.ttf", font_size)
            elif operational_system == "posix":
                font = ImageFont.truetype(
                    "{}/library/fonts/Roboto_Regular.ttf".format(absolute_app_path),
                    font_size,
                )

            border_color = "black"
            border_width = 4
            border_box = [
                (border_width, border_width),
                (width - border_width, height - border_width),
            ]
            draw.rectangle(border_box, outline=border_color, width=border_width)

            description = description.upper()
            category = category.upper()
            origin_account = origin_account.upper()
            destiny_account = destiny_account.upper()

            header_font_size = 20

            if operational_system == "nt":
                header_font = ImageFont.truetype("cour.ttf", header_font_size)
            elif operational_system == "posix":
                header_font = ImageFont.truetype(
                    "{}/library/fonts/Roboto_Regular.ttf".format(absolute_app_path),
                    font_size,
                )

            header_text = "COMPROVANTE DE TRANSFERENCIA"
            header_text_width, header_text_height = draw.textsize(
                header_text, font=header_font
            )
            header_position = ((width - header_text_width) / 2, 10)
            draw.text(header_position, header_text, fill="black", font=header_font)

            draw.line([(20, 40), (width - 20, 40)], fill="black", width=2)
            draw.text((20, 60), f"DESCRIÇÃO: {description}", fill="black", font=font)
            draw.text((20, 90), f"VALOR: R$ {value:.2f}", fill="black", font=font)
            draw.text(
                (20, 120), f"DATA: {date.strftime('%d/%m/%Y')}", fill="black", font=font
            )
            draw.text((20, 150), f"CATEGORIA: {category}", fill="black", font=font)
            draw.text(
                (20, 180), f"CONTA DE ORIGEM: {origin_account}", fill="black", font=font
            )
            draw.text(
                (20, 210),
                f"CONTA DE DESTINO: {destiny_account}",
                fill="black",
                font=font,
            )
            draw.line([(20, 240), (width - 20, 240)], fill="black", width=2)
            draw.line(
                [(width - 240, height - 60), (width - 20, height - 60)],
                fill="black",
                width=2,
            )
            draw.text((680, height - 40), reference_number, fill="black", font=font)

            image.paste(origin_pasted_image, (20, 250))
            image.paste(transfer_image, (170, 250))
            image.paste(destiny_pasted_image, (320, 250))

            caminho_arquivo = "{}/data/receipts/transfers/Comprovante_de_transferencia_{}_{}.png".format(
               absolute_app_path, today, actual_horary
            )

            image.save(caminho_arquivo, dpi=(dpi, dpi))
            st.image(caminho_arquivo, use_container_width=True)

            with open(caminho_arquivo, "rb") as file:
                download_button = st.download_button(
                    label=":floppy_disk: Baixar imagem",
                    data=file,
                    file_name=caminho_arquivo,
                )

        def generate_receipt(table, id, description, value, date, category, account):
            if table == "receitas":
                table = "RECEITA"
            elif table == "emprestimos":
                table = "EMPRÉSTIMO"
            elif table == "despesas":
                table = "DESPESA"
            elif table == "despesas_cartao_credito":
                table = "DESPESA DE CARTÃO"

            reference_number = ""
            if id <= 9:
                reference_number = """REF: 000{}""".format(id)
            if id >= 10 and id <= 99:
                reference_number = """REF: 00{}""".format(id)
            if id >= 100 and id <= 999:
                reference_number = """REF: 0{}""".format(id)

            table = table.upper()
            description = description.upper()
            description = description.replace("'", "")
            category = category.upper()
            category = category.replace("'", "")
            account = account.upper()
            account = account.replace("'", "")

            date = datetime.strptime(date, "%Y-%m-%d")
            date = date.strftime("%d/%m/%Y")

            width, height = 800, 400
            dpi = 300
            image = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(image)
            font_size = 16

            if operational_system == "nt":
                font = ImageFont.truetype("cour.ttf", font_size)
            elif operational_system == "posix":
                font = ImageFont.truetype(
                    "{}/library/fonts/Roboto_Regular.ttf".format(absolute_app_path),
                    font_size,
                )

            border_color = "black"
            border_width = 4
            border_box = [
                (border_width, border_width),
                (width - border_width, height - border_width),
            ]
            draw.rectangle(border_box, outline=border_color, width=border_width)

            header_font_size = 20

            if operational_system == "nt":
                header_font = ImageFont.truetype("cour.ttf", font_size)
            elif operational_system == "posix":
                header_font = ImageFont.truetype(
                    "{}/library/fonts/Roboto_Regular.ttf".format(absolute_app_path),
                    font_size,
                )

            header_text = "COMPROVANTE DE {}".format(table)
            header_text_width, header_text_height = draw.textsize(
                header_text, font=header_font
            )
            header_position = ((width - header_text_width) / 2, 10)
            draw.text(header_position, header_text, fill="black", font=header_font)

            draw.line([(20, 40), (width - 20, 40)], fill="black", width=2)
            draw.text((20, 60), f"DESCRIÇÃO: {description}", fill="black", font=font)
            draw.text((20, 90), f"VALOR: R$ {value:.2f}", fill="black", font=font)
            draw.text((20, 120), f"DATA: {date}", fill="black", font=font)
            draw.text((20, 150), f"CATEGORIA: {category}", fill="black", font=font)
            draw.text((20, 180), f"CONTA: {account}", fill="black", font=font)
            draw.line([(20, 210), (width - 20, 210)], fill="black", width=2)
            draw.line(
                [(width - 240, height - 60), (width - 20, height - 60)],
                fill="black",
                width=2,
            )
            draw.text((20, height - 40), reference_number, fill="black", font=font)

            image_number = 0
            if account == "BEN VISA VALE":
                image_number = 0
            if account == "CARTEIRA":
                image_number = 1
            if account == "CAIXA":
                image_number = 2
            if account == "MERCADO PAGO":
                image_number = 3
            if account == "NUBANK":
                image_number = 4
            if account == "PICPAY":
                image_number = 5
            if account == "SICOOB":
                image_number = 6

            pasted_image = Image.open(accounts_images_paths[image_number])

            image.paste(pasted_image, (20, 220))

            caminho_arquivo = "{}/data/receipts/reports/Relatorio_{}_{}.png".format(
             absolute_app_path, today, actual_horary
            ) 
            image.save(caminho_arquivo, dpi=(dpi, dpi))
            st.image(caminho_arquivo, use_container_width=True)

            with open(caminho_arquivo, "rb") as file:
                download_button = st.download_button(
                    label=":floppy_disk: Baixar imagem",
                    data=file,
                    file_name="Relatorio_{}_{}.png".format(today, actual_horary),
                )

        def get_receipt_input():
            
            col4, col5, col6 = st.columns(3)

            with col4:
                st.subheader(body=":computer: Entrada de dados")

                with st.expander(label="Filtros", expanded=True):
                    report_type = st.selectbox(
                        label="Relatório",
                        options=[
                            "Despesa",
                            "Despesa de Cartão",
                            "Receita",
                            "Empréstimos",
                        ],
                    )

                    if report_type == "Despesa":
                        table = "despesas"
                    elif report_type == "Despesa de Cartão":
                        table = "despesas_cartao_credito"
                    elif report_type == "Receita":
                        table = "receitas"
                    elif report_type == "Empréstimos":
                        table = "emprestimos"

                    date = st.date_input(label="Data")
                    account = st.selectbox(label="Conta", options=accounts)
                    value = st.number_input(
                        label="Valor",
                        placeholder="Informe o valor",
                        min_value=0.01,
                        step=0.01,
                    )

                send_value_button = st.button(label=":white_check_mark: Enviar dados")

                if send_value_button:

                    with col5:
                        st.subheader(body=":page_facing_up: Resultados")

                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)

                        query_data, is_query_valid = validate_query(table, date, account, value)

                        if is_query_valid == True:

                            st.info("Registro encontrado: {}.".format(query_data))

                            with st.expander(label="Resultados", expanded=True):
                                query = execute_query(table, query_data)

                                (
                                    id,
                                    description,
                                    value,
                                    date,
                                    category,
                                    account,
                                ) = treat_receipt_values(query)

                                description = description.replace("'", "")
                                formatted_date = datetime.strptime(date, "%Y-%m-%d")
                                formatted_date = formatted_date.strftime("%d/%m/%Y")

                                formatted_value = str(value)
                                formatted_value = "R$ " + formatted_value.replace(".", ",")

                                if value % 1 == 0 or len(str(value)) == 3:
                                    formatted_value = formatted_value + "0"

                                category = category.replace("'", "")
                                account = account.replace("'", "")

                                credit_card_data_df = pd.DataFrame(
                                    {
                                        "Categoria": [
                                            "Descrição",
                                            "Valor",
                                            "Data",
                                            "Categoria",
                                            "Conta",
                                        ],
                                        "Valor": [
                                            description,
                                            formatted_value,
                                            formatted_date,
                                            category,
                                            account,
                                        ],
                                    }
                                )

                                st.dataframe(
                                    credit_card_data_df,
                                    hide_index=True,
                                    use_container_width=True,
                                )

                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)

                            with col6:
                                st.subheader(body=":pencil: Comprovante")
                                generate_receipt(
                                    table, id, description, value, date, category, account
                                )

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (logged_user, "Consulta", "Consultou um comprovante de {} na data {}, associado a conta {}.".format(report_type, date, account))
                            query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                        elif is_query_valid == False:
                            with st.expander(label="Resultados", expanded=True):
                                st.info("Nenhum resultado Encontrado.")

            with col6:
                st.write("")

        self.get_receipt_data = get_receipt_input
        self.generate_receipt = generate_receipt
        self.generate_transfer_receipt = generate_transfer_receipt