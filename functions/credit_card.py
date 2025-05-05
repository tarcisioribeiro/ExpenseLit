from dictionary.db_config import db_config
from dictionary.vars import (
    actual_year,
    TO_REMOVE_LIST,
    string_actual_month
)
from functions.query_executor import QueryExecutor
from functions.login import Login
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
        selected_card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        actual_month : str
            O nome do mês de fatura do cartão no qual a data atual se encontra.
        """

        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        month_query = '''
        SELECT
            mes
        FROM
        fechamentos_cartao
        WHERE
            CURDATE()
            BETWEEN
                data_comeco_fatura
            AND
                data_fim_fatura
        AND nome_cartao = '{}'
        AND documento_titular = {};'''.format(selected_card, user_document)
        actual_month = QueryExecutor().simple_consult_brute_query(month_query)
        actual_month = QueryExecutor().treat_simple_result(
            actual_month,
            TO_REMOVE_LIST
        )

        return actual_month

    def not_payed_expenses(self, selected_card: str):
        """
        Consulta as despesas de cartão que ainda não foram pagas.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        actual_month = self.get_card_month(selected_card)

        credit_card_not_payed_expenses_query: str = """
            SELECT
                COALESCE(SUM(dcc.valor), 0)
            FROM
                despesas_cartao_credito AS dcc
            INNER JOIN
                fechamentos_cartao AS fc
                ON dcc.numero_cartao = fc.numero_cartao
                AND dcc.doc_proprietario_cartao = fc.documento_titular
            INNER JOIN
                usuarios ON dcc.proprietario_despesa_cartao = usuarios.nome
                    AND dcc.doc_proprietario_cartao = usuarios.documento
            WHERE
                dcc.cartao = '{}'
                AND dcc.data <= fc.data_comeco_fatura
                AND dcc.pago = 'N'
                AND fc.ano <= '{}'
                AND fc.mes = '{}'
                AND usuarios.nome = '{}'
                AND usuarios.documento = '{}';
            """.format(
                selected_card,
                actual_year,
                actual_month,
                user_name,
                user_document
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
                f"""
                Erro ao consultar valor de despesas do cartão não pagas: {err}
                """
            )
        finally:
            if connection.is_connected():
                connection.close()

    def month_expenses(
            self,
            selected_card: str,
            year: int,
            selected_month:
            str
    ):
        """
        Consulta as despesas de cartão no mês e cartão selecionados.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        year : int
            O ano passado como parâmetro.
        selected_month : str
            O mês selecionado pelo usuário.

        Returns
        -------
        float
            O valor total das despesas do cartão no mês.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        credit_card_month_expenses_query: str = """
            SELECT
                COALESCE(SUM(dcc.valor), 0)
            FROM
                despesas_cartao_credito AS dcc
            INNER JOIN
                fechamentos_cartao AS fc
                ON dcc.numero_cartao = fc.numero_cartao
                AND dcc.doc_proprietario_cartao = fc.documento_titular
            INNER JOIN
                usuarios
                ON dcc.proprietario_despesa_cartao = usuarios.nome
                AND dcc.doc_proprietario_cartao = usuarios.documento
            WHERE
                dcc.cartao = '{}'
                AND dcc.data >= fc.data_comeco_fatura
                AND dcc.data <= fc.data_fim_fatura
                AND dcc.pago = 'N'
                AND fc.ano = '{}'
                AND fc.mes LIKE '{}'
                AND usuarios.nome = '{}'
                AND usuarios.documento = '{}';""".format(
                    selected_card,
                    year,
                    selected_month,
                    user_name,
                    user_document
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
                f"""
                Erro ao consultar valor de despesas do cartão no mês: {err}
                """
            )
        finally:
            if connection.is_connected():
                connection.close()

    def get_complete_card_month_expenses(
            self,
            selected_card: str,
            year: int,
            selected_month: str
    ):
        """
        Consulta os detalhes das despesas de cartão no mês selecionado.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        year : int
            O ano passado como parâmetro.
        selected_month : str
            O mês selecionado pelo usuário.

        Returns
        -------
        descricao_list : list
            A lista com a descrição das despesas.
        valor_list : list
            A lista com o valor das despesas.
        data_list : list
            A lista com a data das despesas.
        categoria_list : list
            A lista com a categoria das despesas.
        parcela_list : list
            A lista com a parcela das despesas.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        credit_card_month_expenses_complete_query: str = """
        SELECT
            dcc.descricao AS 'Descrição',
            dcc.valor AS 'Valor',
            dcc.data AS 'Data',
            dcc.categoria AS 'Categoria',
            CONCAT(dcc.parcela, 'ª') AS 'Parcela'
        FROM
            despesas_cartao_credito AS dcc
        INNER JOIN
            fechamentos_cartao AS fc
                ON dcc.numero_cartao = fcc.numero_cartao
                AND dcc.doc_proprietario_cartao = fc.documento_titular
        INNER JOIN
            usuarios ON dcc.proprietario_despesa_cartao = usuarios.nome
                AND dcc.doc_proprietario_cartao = usuarios.documento
        WHERE
            dcc.cartao = '{}'
                AND dcc.data >= fc.data_comeco_fatura
                AND dcc.data <= fc.data_fim_fatura
                AND dcc.pago = 'N'
                AND fc.ano = '{}'
                AND fc.mes = '{}'
                AND usuarios.nome = '{}'
                AND usuarios.documento = '{}';
        """.format(
            selected_card,
            year,
            selected_month,
            user_name,
            user_document
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
                f"""
                Erro ao consultar detalhamento no mês: {err}"""
            )
        finally:
            if connection.is_connected():
                connection.close()

    def get_card_id_month_expenses(
        self,
        selected_card: str,
        year: int,
        selected_month: str
    ):
        """
        Consulta o id das despesas de cartão no mês selecionado.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        year : int
            O ano passado como parâmetro.
        selected_month : str
            O mês da fatura selecionada.

        Returns
        -------
        converted_id_list : list
            A lista com os ID's de despesas de cartão no mês.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        credit_card_id_expenses_query = """
        SELECT
            dcc.id_despesa_cartao
        FROM
            despesas_cartao_credito AS dcc
        INNER JOIN
            fechamentos_cartao AS fc
                ON dcc.numero_cartao = fc.numero_cartao
                AND dcc.doc_proprietario_cartao = fc.documento_titular
        INNER JOIN
            usuarios ON dcc.proprietario_despesa_cartao = usuarios.nome
                AND dcc.doc_proprietario_cartao = usuarios.documento
        WHERE
            dcc.cartao = '{}'
                AND dcc.data >= fc.data_comeco_fatura
                AND dcc.data <= fc.data_fim_fatura
                AND fc.ano = '{}'
                AND fc.mes = '{}'
                AND usuarios.nome = '{}'
                AND usuarios.documento = '{}'
                AND pago = 'N';
        """.format(
            selected_card,
            year,
            selected_month,
            user_name,
            user_document
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

    def future_expenses(self, selected_card: str):
        """
        Consulta o valor das próximas despesas do cartão.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        float
            O valor total das despesas futuras.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        actual_month = self.get_card_month(selected_card)

        credit_card_next_expenses_query: str = """
        SELECT
            COALESCE(SUM(dcc.valor), 0)
        FROM
            despesas_cartao_credito AS dcc
        INNER JOIN
            fechamentos_cartao AS fc
            ON dcc.numero_cartao = fc.numero_cartao
                AND dcc.doc_proprietario_cartao = fc.documento_titular
        INNER JOIN
            usuarios ON dcc.proprietario_despesa_cartao = usuarios.nome
                AND dcc.doc_proprietario_cartao = usuarios.documento
        WHERE
            dcc.cartao = '{}'
                AND dcc.pago = 'N'
                AND dcc.data > fc.data_fim_fatura
                AND fc.ano = '{}'
                AND fc.mes = '{}'
                AND usuarios.nome = '{}'
                AND usuarios.documento = '{}';
        """.format(
            selected_card,
            actual_year,
            actual_month,
            user_name,
            user_document
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
                f"""
                Erro ao consultar valor das despesas futuras: {err}
                """
            )
        finally:
            if connection.is_connected():
                connection.close()

    def card_limit(self, selected_card: str):
        """
        Consulta o limite do cartão.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        float
            O limite de crédito do cartão.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

        credit_card_limit_query: str = """
        SELECT
            COALESCE(SUM(cartao_credito.limite_credito), 0)
        FROM
            cartao_credito
                INNER JOIN
            usuarios ON cartao_credito.documento_titular = usuarios.documento
                AND cartao_credito.proprietario_cartao = usuarios.nome
        WHERE
            cartao_credito.nome_cartao = '{}'
        AND usuarios.nome = '{}'
        AND usuarios.documento = '{}';""".format(
            selected_card,
            user_name,
            user_document
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
        card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        card_number : str
            O número do cartão.
        card_owner : str
            O nome do proprietário do cartão.
        card_owner_document : int
            O documento do proprietário do cartão.
        card_security_code : str
            O código de segurança do cartão.
        """
        user_name, user_document = Login().get_user_data(
            return_option="user_doc_name"
        )

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
                AND cartao_credito.documento_titular = usuarios.documento
        WHERE
            cartao_credito.nome_cartao = '{}'
                AND usuarios.nome = '{}'
                AND usuarios.documento = '{}';
        """.format(
            card,
            user_name,
            user_document
        )

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(card_key_query)
            result = cursor.fetchall()
            cursor.close()

            if (
                result is not None
                ) and (
                len(result) > 0
                ) and (
                result[0] is not None
            ):

                str_card_key_list = str(result[0])

                str_card_key_list = str_card_key_list.replace(")", "")
                str_card_key_list = str_card_key_list.replace("(", "")
                str_card_key_list = str_card_key_list.replace("'", "")
                str_card_key_list = str_card_key_list.split(", ")

                card_number = str_card_key_list[0]
                card_owner = str_card_key_list[1]
                card_owner_document = str_card_key_list[2]
                card_security_code = str_card_key_list[3]

                return (
                    card_number,
                    card_owner,
                    card_owner_document,
                    card_security_code,
                )

        except mysql.connector.Error as err:
            st.error(f"Erro ao consultar chave do cartão: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def card_remaining_limit(self, selected_card: str):
        """
        Calcula o limite restante do cartão de crédito.

        Parameters
        ----------
        selected_card : str
            O cartão de crédito selecionado.

        Returns
        -------
        remaining_limit : float
            0 valor do limite restante do cartão.
        """
        card_total_limit = self.card_limit(selected_card)
        not_payed_expenses = self.not_payed_expenses(selected_card)
        month_card_expenses = self.month_expenses(
            selected_card,
            actual_year,
            string_actual_month
        )
        future_card_expenses = self.future_expenses(selected_card)
        total_card_expenses = month_card_expenses + \
            future_card_expenses + not_payed_expenses
        remaining_limit = card_total_limit - total_card_expenses
        return remaining_limit
