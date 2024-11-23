from data.cache.session_state import logged_user, logged_user_password
from dictionary.vars import db_config, actual_year, to_remove_list, string_actual_month
from dictionary.user_stats import user_document
from functions.query_executor import QueryExecutor
import mysql.connector
import re
import streamlit as st


class Credit_Card:
    """
    Representa um cartão de crédito e suas funções.

    Attributes
    ----------
    get_card_month: str
        Realiza a busca do mês atual do cartão.
    not_payed_expenses: float
        Realiza a busca das despesas não pagas do cartão.
    month_expenses: float
        Realiza a busca das despesas do cartão no mês.
    month_complete_expenses: list
        Faz uma busca detalhada das despesas do cartão no mês.
    get_card_id_month_expenses: list
        Realiza a busca dos id's das despesas do mês, realiza o tratamento dos valores e retorna uma lista.
    future_expenses: float
        Realiza a busca do valor das próximas despesas do cartão.
    card_limit: float
        Realiza a consulta do limite de crédito do cartão.
    credit_card_key: list
        Realiza a busca dos dados do cartão de cŕedito.
    card_remaining_limit: float
        Realiza o cálculo do valor restante do limite disponível para o cartão.
    """

    query_executor = QueryExecutor()

    def get_card_month(self, selected_card: str):
        """
        Realiza a busca do mês atual do cartão.

        Parameters
        ----------
        selected_card: str
            Utiliza o cartão passado para a busca.

        Returns
        -------
        actual_month: str
            O mês atual do cartão.
        """

        query_executor = QueryExecutor()

        month_query = """SELECT 
                                    mes
                                FROM
                                    fechamentos_cartao
                                WHERE
                                    CURDATE() BETWEEN data_comeco_fatura AND data_fim_fatura
                                        AND nome_cartao = '{}'
                                        AND documento_titular = {};""".format(
            selected_card, user_document
        )
        actual_month = query_executor.simple_consult_query(month_query)
        actual_month = query_executor.treat_simple_result(actual_month, to_remove_list)

        return actual_month

    def not_payed_expenses(self, selected_card: str):
        """
        Realiza a busca das despesas não pagas do cartão.

        Parameters
        ----------
        selected_card: str
            Utiliza o cartão passado para realizar a busca.

        Returns
        -------
        result: float
            O valor total das despesas não pagas no cartão.
        """

        actual_month = self.get_card_month(selected_card)

        credit_card_not_payed_expenses_query: str = (
            """
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
            st.error(f"Erro ao consultar valor de despesas do cartão não pagas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def month_expenses(self, selected_card: str, selected_month: str):
        """
        Realiza a busca das despesas do cartão no mês.

        Parameters
        ----------

        selected_card: str
            Utiliza o cartão selecionado como parâmetro da busca.
        selected_month: str
            Utiliza o mês selecionado como parâmetro da busca.

        Returns
        -------
        result: float
            O valor total das despesas do cartão no mês.
        """

        actual_month = self.get_card_month(selected_card)

        credit_card_month_expenses_query: str = (
            """
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
                actual_year,
                selected_month,
                logged_user,
                logged_user_password,
            )
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
                f"Erro ao consultar valor total de despesas do cartão no mês: {err}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    def month_complete_expenses(self, selected_card: str, selected_month: str):
        """
        Faz uma busca detalhada das despesas do cartão no mês.

        Parameters
        ----------
        selected_card: str
          Utiliza o cartão selecionado como parâmetro da busca.
        selected_month: str
          Utiliza o mês selecionado como parâmetro da busca.

        Returns
        -------
        list
            A lista com a descrição, valor, data, categoria e a parcela da despesa.
        """

        actual_month = self.get_card_month(selected_card)

        credit_card_month_expenses_complete_query: str = (
            """
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
                actual_year,
                selected_month,
                logged_user,
                logged_user_password,
            )
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
                f"Erro ao consultar detalhamento das despesas do cartão no mês: {err}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    def get_card_id_month_expenses(self, selected_card: str, selected_month: str):
        """
        Realiza a busca dos id's das despesas do mês, realiza o tratamento dos valores e retorna uma lista.

        Parameters
        ----------
        selected_card: str
            Utiliza o cartão selecionado como parâmetro da busca.
        selected_month: str
            Utiliza o mês selecionado como parâmetro da busca.

        Returns
        -------
        converted_id_list: list
            Retorna a lista dos id's tratados pela função.
        """

        actual_month = self.get_card_month(selected_card)

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
            actual_year,
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
            st.error(f"Erro ao consultar id's das despesas do cartão no mês: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def future_expenses(self, selected_card: str):
        """
        Realiza a busca do valor das próximas despesas do cartão.

        Parameters
        ----------
        selected_card: str
            Utiliza o cartão selecionado como parâmetro da busca.

        Returns
        -------
        result: float
            O valor total das despesas futuras.
        """

        actual_month = self.get_card_month(selected_card)

        credit_card_next_expenses_query: str = (
            """
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
                f"Erro ao consultar valor total das despesas futuras do cartão: {err}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    def card_limit(self, selected_card: str):
        """
        Realiza a consulta do limite de crédito do cartão.

        Parameters
        ----------
        selected_card: str
            Utiliza o cartão selecionado como parâmetro da busca.

        Returns
        -------
        result: float
            O valor do limite do cartão.
        """

        credit_card_limit_query: str = (
            """
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

    def credit_card_key(self, card: str):
        """
        Realiza a busca dos dados do cartão de cŕedito.

        Parameters
        ----------

        card: str
            Utiliza o cartão selecionado como parâmetro da busca.

        Returns
        -------

        card_list: list
            A lista com os dados do cartão.
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
                card_security_code = int(str_card_key_list[3])

                card_list = []

                card_list.append(card_number, card_owner, card_owner_document, card_security_code)

                return card_list

            else:
                return ["9999999999999999", "Sem proprietário", 99999999999, 000]

        except mysql.connector.Error as err:
            st.error(f"Erro ao consultar chave do cartão: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def card_remaining_limit(self, selected_card: str):
        """
        Realiza o cálculo do valor restante do limite disponível para o cartão.

        Parameters
        ----------
        selected_card: str
            Utiliza o cartão selecionado como parâmetro do cálculo.

        Returns
        -------
        remaining_limit: float
            O valor do limite restante.
        """

        card_total_limit = self.get_credit_card_limit(selected_card)
        not_payed_expenses = self.get_credit_card_not_payed_expenses(selected_card)
        month_card_expenses = self.get_credit_card_month_expenses(
            selected_card, string_actual_month
        )
        future_card_expenses = self.get_credit_card_next_expenses(selected_card)
        total_card_expenses = (
            month_card_expenses + future_card_expenses + not_payed_expenses
        )
        remaining_limit = card_total_limit - total_card_expenses
        return remaining_limit