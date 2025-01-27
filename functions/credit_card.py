from data.cache.session_state import logged_user, logged_user_password
from dictionary.db_config import db_config
from dictionary.vars import (
    actual_year,
    to_remove_list,
    string_actual_month
)
from dictionary.user_stats import user_document
from functions.query_executor import QueryExecutor
import mysql.connector
import re
import streamlit as st


class Credit_Card:
    """
    Classe com métodos que representam as operações de um cartão de crédito.
    """

    def get_card_month(self, selected_card: str):
        """
        Obtém o mês de fatura do cartão no qual a data atual se encontra.

        Parameters
        ----------
        selected_card: str = O cartão selecionado pelo usuário.

        Returns
        -------
        actual_month: str = O nome do mês de fatura do cartão no qual a data atual se encontra.
        """

        month_query = '''SELECT 
                                mes
                            FROM
                                fechamentos_cartao
                            WHERE
                                CURDATE() BETWEEN data_comeco_fatura AND data_fim_fatura
                                    AND nome_cartao = '{}'
                                    AND documento_titular = {};'''.format(selected_card, user_document)
        actual_month = QueryExecutor().simple_consult_query(month_query)
        actual_month = QueryExecutor().treat_simple_result(
            actual_month, to_remove_list)

        return actual_month

    def get_credit_card_not_payed_expenses(self, selected_card: str):
        """
        Consulta as despesas de cartão que ainda não foram pagas.

        Parameters
        ----------
        selected_card: str = O cartão selecionado pelo usuário.
        """

        actual_month = self.get_card_month(selected_card)

        credit_card_not_payed_expenses_query: str = """
            SELECT 
                COALESCE(SUM(despesas_cartao_credito.valor), 0)
            FROM
                despesas_cartao_credito
                    INNER JOIN
                fechamentos_cartao ON despesas_cartao_credito.numero_cartao = fechamentos_cartao.numero_cartao
                    AND despesas_cartao_credito.doc_proprietario_cartao = fechamentos_cartao.documento_titular
                    INNER JOIN
                usuarios ON despesas_cartao_credito.proprietario_despesa_cartao = usuarios.nome
                    AND despesas_cartao_credito.doc_proprietario_cartao = usuarios.cpf
            WHERE
                despesas_cartao_credito.cartao = '{}'
                    AND despesas_cartao_credito.data <= fechamentos_cartao.data_comeco_fatura
                    # AND despesas_cartao_credito.data <= fechamentos_cartao.data_fim_fatura
                    AND despesas_cartao_credito.pago = 'N'
                    AND fechamentos_cartao.ano <= '{}'
                    AND fechamentos_cartao.mes = '{}'
                    AND usuarios.login = '{}'
                    AND usuarios.senha = '{}'
            ;""".format(
            selected_card,
            actual_year,
            actual_month,
            logged_user,
            logged_user_password,
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(credit_card_not_payed_expenses_query)
            result = cursor.fetchone()
            cursor.close()
            if result and result[0] is not None:
                return float(result[0])
            return 0.0
        except mysql.connector.Error as err:
            st.error(
                f"Erro ao consultar valor de despesas do cartão não pagas: {
                    err}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    def get_credit_card_month_expenses(self, selected_card: str, year: int, selected_month: str):
        """
        Consulta as despesas de cartão no mês e cartão selecionados.

        Parameters
        ----------

        selected_card: str = O cartão selecionado pelo usuário.\n
        year: int = O ano passado como parâmetro.\n
        selected_month: str = O mês selecionado pelo usuário.

        Returns
        -------
        float: O valor total das despesas do cartão no mês.
        """

        credit_card_month_expenses_query: str = """
            SELECT 
                COALESCE(SUM(despesas_cartao_credito.valor), 0)
            FROM
                despesas_cartao_credito
                    INNER JOIN
                fechamentos_cartao ON despesas_cartao_credito.numero_cartao = fechamentos_cartao.numero_cartao
                    AND despesas_cartao_credito.doc_proprietario_cartao = fechamentos_cartao.documento_titular
                    INNER JOIN
                usuarios ON despesas_cartao_credito.proprietario_despesa_cartao = usuarios.nome
                    AND despesas_cartao_credito.doc_proprietario_cartao = usuarios.cpf
            WHERE
                despesas_cartao_credito.cartao = '{}'
                    AND despesas_cartao_credito.data >= fechamentos_cartao.data_comeco_fatura
                    AND despesas_cartao_credito.data <= fechamentos_cartao.data_fim_fatura
                    AND despesas_cartao_credito.pago = 'N'
                    AND fechamentos_cartao.ano = '{}'
                    AND fechamentos_cartao.mes = '{}'
                    AND usuarios.login = '{}'
                    AND usuarios.senha = '{}'
            ;""".format(
            selected_card,
            year,
            selected_month,
            logged_user,
            logged_user_password,
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(credit_card_month_expenses_query)
            result = cursor.fetchone()
            cursor.close()
            if result and result[0] is not None:
                return float(result[0])
            return 0.0
        except mysql.connector.Error as err:
            st.error(
                f"Erro ao consultar valor total de despesas do cartão no mês: {
                    err}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    def get_complete_card_month_expenses(self, selected_card: str, year: int, selected_month: str):
        """
        Consulta os detalhes das despesas de cartão no mês selecionado pelo usuário.

        Parameters
        ----------
        selected_card: str = O cartão selecionado pelo usuário.\n
        year: int = O ano passado como parâmetro.\n
        selected_month: str = O mês selecionado pelo usuário.

        Returns
        -------
        descricao_list: list = A lista com a descrição das despesas.\n
        valor_list: list = A lista com o valor das despesas.\n
        data_list: list = A lista com a data das despesas.\n
        categoria_list: list = A lista com a categoria das despesas.\n
        parcela_list: list = A lista com a parcela das despesas.
        """

        actual_month = self.get_card_month(selected_card)

        credit_card_month_expenses_complete_query: str = """
        SELECT 
            despesas_cartao_credito.descricao AS 'Descrição',
            despesas_cartao_credito.valor AS 'Valor',
            despesas_cartao_credito.data AS 'Data',
            despesas_cartao_credito.categoria AS 'Categoria',
            CONCAT(despesas_cartao_credito.parcela, 'ª') AS 'Parcela'
        FROM
            despesas_cartao_credito
                INNER JOIN
            fechamentos_cartao ON despesas_cartao_credito.numero_cartao = fechamentos_cartao.numero_cartao
                AND despesas_cartao_credito.doc_proprietario_cartao = fechamentos_cartao.documento_titular
                INNER JOIN
            usuarios ON despesas_cartao_credito.proprietario_despesa_cartao = usuarios.nome
                AND despesas_cartao_credito.doc_proprietario_cartao = usuarios.cpf
        WHERE
            despesas_cartao_credito.cartao = '{}'
                AND despesas_cartao_credito.data >= fechamentos_cartao.data_comeco_fatura
                AND despesas_cartao_credito.data <= fechamentos_cartao.data_fim_fatura
                AND despesas_cartao_credito.pago = 'N'
                AND fechamentos_cartao.ano = '{}'
                AND fechamentos_cartao.mes = '{}'
                AND usuarios.login = '{}'
                AND usuarios.senha = '{}';
                """.format(
            selected_card,
            year,
            selected_month,
            logged_user,
            logged_user_password,
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(credit_card_month_expenses_complete_query)

            descricao_list = []
            valor_list = []
            data_list = []
            categoria_list = []
            parcela_list = []

            for row in cursor.fetchall():
                descricao_list.append(row[0])
                valor_list.append(row[1])
                data_list.append(row[2])
                categoria_list.append(row[3])
                parcela_list.append(row[4])

            cursor.close()

            return (
                descricao_list,
                valor_list,
                data_list,
                categoria_list,
                parcela_list,
            )

        except mysql.connector.Error as err:
            st.error(
                f"Erro ao consultar detalhamento das despesas do cartão no mês: {
                    err}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    def get_card_id_month_expenses(self, selected_card: str, year: int, selected_month: str):
        """
        Consulta o id das despesas de cartão no mês selecionado.

        Parameters
        ----------
        selected_card: str = O cartão selecionado pelo usuário.\n
        year: int = O ano passado como parâmetro.\n
        selected_month: str = O mês da fatura selecionada.

        Returns
        -------
        converted_id_list: list = A lista com os ID's de despesas de cartão no mês.
        """

        credit_card_id_expenses_query = """
        SELECT 
            despesas_cartao_credito.id_despesa_cartao
        FROM
            despesas_cartao_credito
                INNER JOIN
            fechamentos_cartao ON despesas_cartao_credito.numero_cartao = fechamentos_cartao.numero_cartao
                AND despesas_cartao_credito.doc_proprietario_cartao = fechamentos_cartao.documento_titular
                INNER JOIN
            usuarios ON despesas_cartao_credito.proprietario_despesa_cartao = usuarios.nome
                AND despesas_cartao_credito.doc_proprietario_cartao = usuarios.cpf
        WHERE
            despesas_cartao_credito.cartao = '{}'
                AND despesas_cartao_credito.data >= fechamentos_cartao.data_comeco_fatura
                AND despesas_cartao_credito.data <= fechamentos_cartao.data_fim_fatura
                AND fechamentos_cartao.ano = '{}'
                AND fechamentos_cartao.mes = '{}'
                AND usuarios.login = '{}'
                AND usuarios.senha = '{}'
                AND pago = 'N';
                """.format(
            selected_card,
            year,
            selected_month,
            logged_user,
            logged_user_password,
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(credit_card_id_expenses_query)
            id_list = cursor.fetchall()
            cursor.close()

            converted_id_list = []

            for row in id_list:
                id_ = str(row[0])
                id_ = re.sub(r"['()Decimal,]", "", id_)
                float_id = int(id_)
                converted_id_list.append(float_id)

            return converted_id_list

        except mysql.connector.Error as err:
            st.error(
                f"Erro ao consultar id's das despesas do cartão no mês: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def get_credit_card_next_expenses(self, selected_card: str):
        """
        Consulta o valor das próximas despesas do cartão.

        Parameters
        ----------
        selected_card: str = O cartão selecionado pelo usuário.

        Returns
        -------
        float: O valor total das despesas futuras.
        """

        actual_month = self.get_card_month(selected_card)

        credit_card_next_expenses_query: str = """
        SELECT 
            COALESCE(SUM(despesas_cartao_credito.valor), 0)
        FROM
            despesas_cartao_credito
                INNER JOIN
            fechamentos_cartao ON despesas_cartao_credito.numero_cartao = fechamentos_cartao.numero_cartao
                AND despesas_cartao_credito.doc_proprietario_cartao = fechamentos_cartao.documento_titular
                INNER JOIN
            usuarios ON despesas_cartao_credito.proprietario_despesa_cartao = usuarios.nome
                AND despesas_cartao_credito.doc_proprietario_cartao = usuarios.cpf
        WHERE
            despesas_cartao_credito.cartao = '{}'
                AND despesas_cartao_credito.pago = 'N'
                AND despesas_cartao_credito.data > fechamentos_cartao.data_fim_fatura
                AND fechamentos_cartao.ano = '{}'
                AND fechamentos_cartao.mes = '{}'
                AND usuarios.login = '{}'
                AND usuarios.senha = '{}';
                """.format(
            selected_card,
            actual_year,
            actual_month,
            logged_user,
            logged_user_password,
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(credit_card_next_expenses_query)
            result = cursor.fetchone()
            cursor.close()
            if result and result[0] is not None:
                return float(result[0])
            return 0.0
        except mysql.connector.Error as err:
            st.error(
                f"Erro ao consultar valor total das despesas futuras do cartão: {
                    err}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    def get_credit_card_limit(self, selected_card: str):
        """
        Consulta o limite do cartão.

        Parameters
        ----------
        selected_card: O cartão selecionado pelo usuário.

        Returns
        -------
        float: O limite de crédito do cartão.
        """
        credit_card_limit_query: str = """
        SELECT 
            COALESCE(SUM(cartao_credito.limite_credito), 0)
        FROM
            cartao_credito
                INNER JOIN
            usuarios ON cartao_credito.documento_titular = usuarios.cpf
                AND cartao_credito.proprietario_cartao = usuarios.nome
        WHERE
            cartao_credito.nome_cartao = '{}'
                AND usuarios.login = '{}'
                AND usuarios.senha = '{}';""".format(
            selected_card, logged_user, logged_user_password
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(credit_card_limit_query)
            result = cursor.fetchone()
            cursor.close()
            if result and result[0] is not None:
                return float(result[0])
            return 0.0
        except mysql.connector.Error as err:
            st.error(f"Erro ao consultar limite do cartão: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def get_credit_card_key(self, card: str):
        """
        Consulta os dados do cartão selecionado.

        Parameters
        ----------
        card: O cartão selecionado pelo usuário.

        Returns
        -------
        card_number: str = O número do cartão.\n
        card_owner: str = O nome do proprietário do cartão.\n
        card_owner_document: int = O documento do proprietário do cartão.\n
        card_security_code: str = O código de segurança do cartão.
        """
        card_key_query = """
        SELECT 
            cartao_credito.numero_cartao,
            cartao_credito.proprietario_cartao,
            cartao_credito.documento_titular,
            cartao_credito.codigo_seguranca
        FROM
            cartao_credito
                INNER JOIN
            usuarios ON cartao_credito.proprietario_cartao = usuarios.nome
                AND cartao_credito.documento_titular = usuarios.cpf
        WHERE
            cartao_credito.nome_cartao = '{}'
                AND usuarios.login = '{}'
                AND usuarios.senha = '{}';""".format(
            card, logged_user, logged_user_password
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(card_key_query)
            result = cursor.fetchall()
            cursor.close()

            if result is not None and len(result) > 0 and result[0] is not None:

                str_card_key_list = str(result[0])

                str_card_key_list = str_card_key_list.replace(")", "")
                str_card_key_list = str_card_key_list.replace("(", "")
                str_card_key_list = str_card_key_list.replace("'", "")
                str_card_key_list = str_card_key_list.split(", ")

                card_number = str_card_key_list[0]
                card_owner = str_card_key_list[1]
                card_owner_document = int(str_card_key_list[2])
                card_security_code = str_card_key_list[3]

                return (
                    card_number,
                    card_owner,
                    card_owner_document,
                    card_security_code,
                )

            else:
                return ["9999999999999999", "Sem proprietário", 99999999999, 000]

        except mysql.connector.Error as err:
            st.error(f"Erro ao consultar chave do cartão: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def get_credit_card_remaining_limit(self, selected_card: str):
        card_total_limit = self.get_credit_card_limit(selected_card)
        not_payed_expenses = self.get_credit_card_not_payed_expenses(
            selected_card)
        month_card_expenses = self.get_credit_card_month_expenses(
            selected_card, actual_year, string_actual_month)
        future_card_expenses = self.get_credit_card_next_expenses(
            selected_card)
        total_card_expenses = month_card_expenses + \
            future_card_expenses + not_payed_expenses
        remaining_limit = card_total_limit - total_card_expenses
        return remaining_limit
