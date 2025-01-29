from dictionary.db_config import db_config
from dictionary.vars import operational_system
import mysql.connector
import streamlit as st


class QueryExecutor:
    """
    Classe com métodos para inserção, atualização e tratamento de dados obtidos do banco de dados.
    """

    def insert_query(self, query: str, values: tuple, success_message: str, error_message: str):
        """
        Realiza a inserção da consulta no banco de dados.

        Parameters
        ----------
        query : str
            A consulta a ser inserida.
        values : tuple
            A tupla com os valores a serem inseridos.
        success_message : str
            A mensagem a ser exibida caso a consulta seja inserida com sucesso.
        error_message : str
            A mensagem a ser exibida caso a consulta apresente erros ao ser inserida.
        """
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            st.toast(":white_check_mark: {}".format(success_message))
        except mysql.connector.Error as error:
            st.toast(":warning: {} {}".format(error_message, error))
            st.error(error)
        finally:
            if connection.is_connected():
                connection.close()
                st.toast(body="Inserção finalizada.")

    def simple_consult_query(self, query: str, params: tuple):
        """
        Realiza uma consulta simples no banco de dados, de acordo com os parametros informados.

        Parameters
        ----------
        query : str
            A consulta a ser inserida.
        params : tuple
            A tupla com os valores a serem consultados.
        """
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query, params)
            simple_value = cursor.fetchone()
            cursor.close()
            if simple_value is not None:
                return simple_value
            else:
                return 0
        except mysql.connector.Error as error:
            st.toast(":warning: Erro ao consultar dado: {}".format(error))
            st.error(error)
        finally:
            if connection.is_connected():
                connection.close()

    def simple_consult_brute_query(self, query: str):
        """
        Realiza uma consulta simples no banco de dados.

        Parameters
        ----------
        query : str
            A consulta a ser inserida.
        """
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor() 
            cursor.execute(query)
            simple_value = cursor.fetchone()
            cursor.close()
            if simple_value is not None:
                return simple_value
            else:
                return 0
        except mysql.connector.Error as error:
            if operational_system == "posix":
                st.toast(":warning: Erro ao consultar dado: {}".format(error))
                st.error(error)
            elif operational_system == "nt":
                print("Erro ao consultar dado: {}".format(error))
        finally:
            if connection.is_connected():
                connection.close()

    def complex_compund_query(self, query: str, list_quantity: int, params: tuple):
        """
        Executa uma consulta composta no banco de dados com base nos parâmetros fornecidos.

        Parameters
        ----------
        query : str
            A consulta SQL a ser executada.
        list_quantity : int
            O número de listas que deverão ser criadas para armazenar os resultados.
        params : tuple
            Uma tupla contendo os valores que serão utilizados como parâmetros na consulta.

        Returns
        -------
        list
            Uma lista contendo múltiplas listas, cada uma correspondendo aos valores retornados pela consulta.
        """
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query, params)

            lists = [[] for _ in range(list_quantity)]

            for row in cursor.fetchall():
                for i in range(list_quantity):
                    lists[i].append(row[i])

            return lists

        except mysql.connector.Error as err:
            st.error("Erro ao consultar dados compostos: {}".format(err))
            return None

        finally:
            if connection.is_connected():
                connection.close()

    def complex_consult_query(self, query: str, params: tuple):
        """
        Realiza uma consulta complexa no banco de dados, de acordo com os parametros informados.

        Parameters
        ----------
        query : str
            A consulta a ser inserida.
        params : tuple
            A tupla com os valores a serem consultados.

        Returns
        -------
        complex_value : list
            A lista com os valores da consulta.
        """
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query, params)
            complex_value = cursor.fetchall()
            cursor.close()
            if complex_value is not None:
                return complex_value
            else:
                return [0]
        except mysql.connector.Error as error:
            st.toast(":warning: Erro ao consultar dados: {}".format(error))
            st.error(error)
        finally:
            if connection.is_connected():
                connection.close()

    def complex_consult_brute_query(self, query: str):
        """
        Realiza uma consulta complexa no banco de dados.

        Parameters
        ----------
        query : str
            A consulta a ser inserida.

        Returns
        -------
        complex_value : list
            A lista com os valores da consulta.
        """
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query)
            complex_value = cursor.fetchall()
            cursor.close()
            if complex_value is not None:
                return complex_value
            else:
                return [0]
        except mysql.connector.Error as error:
            st.toast(":warning: Erro ao consultar dados: {}".format(error))
            st.error(error)
        finally:
            if connection.is_connected():
                connection.close()

    def treat_simple_result(self, value_to_treat: str, values_to_remove: list):
        """
        Realiza o tratamento de uma cadeia de caracteres, de acordo com os parametros informados.

        Parameters
        ----------
        value_to_treat : str
            O valor a ser tratado.
        values_to_remove : list
            Os valores a serem removidos.

        Returns
        -------
        final_result : str
            O valor tratado.
        """
        final_result = str(value_to_treat)

        for i in range(0, len(values_to_remove)):
            final_result = final_result.replace(
                "{}".format(values_to_remove[i]), "")

        return final_result

    def treat_numerous_simple_result(self, values_to_treat: list, values_to_remove: list):
        """
        Realiza o tratamento de varias cadeias de caracteres, de acordo com os parametros informados.

        Parameters
        ----------
        value_to_treat : list
            Os valores a serem tratados.
        values_to_remove : list
            Os valores a serem removidos.

        Returns
        -------
        final_list : list
            Os valores tratados.
        """
        aux_str = ""
        aux_list = []

        for i in range(0, len(values_to_treat)):
            aux_str = str(values_to_treat[i])
            aux_list.append(aux_str)

        final_str = ""
        final_list = []

        for i in range(0, len(aux_list)):
            final_str = str(aux_list[i])
            for i in range(0, len(values_to_remove)):
                final_str = final_str.replace(
                    "{}".format(values_to_remove[i]), "")
            final_list.append(final_str)

        return final_list

    def treat_complex_result(self, values_to_treat, values_to_remove: list):
        """
        Realiza o tratamento de uma cadeia de caracteres, de acordo com os parametros informados.

        Parameters
        ----------
        value_to_treat : str
            O valor a ser tratado.
        values_to_remove : list
            Os valores a serem removidos.

        Returns
        -------
        final_result : str
            O valor tratado.
        """
        aux_str = ""
        aux_list = []

        final_str = ""
        final_list = []

        for i in range(0, len(values_to_treat)):
            aux_str = str(values_to_treat[i])
            aux_list = aux_str.split(", ")
            for i in range(0, len(aux_list)):
                final_str = str(aux_list[i])
                for i in range(0, len(values_to_remove)):
                    final_str = final_str.replace(
                        "{}".format(values_to_remove[i]), "")
                final_list.append(final_str)

        return final_list

    def check_if_value_exists(self, query):
        """
        Verifica se o valor da consulta existe no banco de dados.

        Parameters
        ----------
        query : str
            A consulta a ser verificada.

        Returns
        -------
        bool
            Retorna se o dado consultado existe ou não no banco de dados.
        """
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchone() is not None

    def update_table_registers(self, table: str, table_field: str, id_list: list):
        """
        Realiza a atualização de registros no banco de dados, de acordo com os parametros informados.

        Parameters
        ----------
        table : str
            A tabela que será atualizada.
        table_field: str
            O campo da tabela que será atualizado.
        id_list : list
            Os id's de identificação dos registros que serão atualizados.
        """
        for i in range(0, len(id_list)):

            update_id_query = """UPDATE {} SET pago = 'S' WHERE id_{} = {}""".format(
                table, table_field, id_list[i])

            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute(update_id_query)
                connection.commit()
                cursor.close()

            except mysql.connector.Error as err:
                st.toast(f"Erro ao pagar despesas do cartão: {err}")
            finally:
                if connection.is_connected():
                    connection.close()

    def update_table_unique_register(self, query: str, success_message: str, error_message: str):
        """
        Realiza a atualização de um registro no banco de dados.

        Parameters
        ----------
        query : str
            A consulta de atualização.
        success_message : str
            A mensagem que será exibida caso a atualização seja concluída.
        error_message : str
            A mensagem que será exibida caso ocorram erros durante a atualização.
        """
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            cursor.close()

            st.toast(":white_check_mark: {}".format(success_message))
        except mysql.connector.Error as error:
            st.toast(":warning: {} {}".format(error_message, error))
        finally:
            if connection.is_connected():
                connection.close()
