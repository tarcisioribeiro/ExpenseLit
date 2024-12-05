from dictionary.vars import db_config
import mysql.connector
import streamlit as st


class QueryExecutor:
    """
    Classe responsável pela execução de consultas e tratamento dos resultados.

    Attributes
    ----------
    insert_query(query, values, success_message, error_message)
        Realiza a inserção de uma query no banco de dados com base nos dados informados, retornando uma mensagem de sucesso ou erro ao fim do processo.
    """

    def insert_query(
        self, query: str, values: tuple, success_message: str, error_message: str
    ):
        """
        Realiza a inserção de uma query no banco de dados com base nos dados informados, retornando uma mensagem de sucesso ou erro ao fim do processo.

        Parameters
        ----------
        query: str
            Query a ser inserida no banco de dados.
        values: tuple
            Tupla com os valores a serem inseridos.
        successs_message: str
            Mensagem de sucesso a ser exibida caso o processo seja concluído.
        error_message: str
            Mensagem de erro a ser exibida caso o processo tenha fala.
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

    def simple_consult_query(self, query: str):
        """
        Realiza a consulta de um valor único no banco de dados.

        Parameters
        ----------
        query: str
            Consulta a ser realiza no banco de dados.
        Returns
        -------
        simple_value: str
            O valor a ser retornado.
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
            st.toast(":warning: Erro ao consultar dado: {}".format(error))
            st.error(error)
        finally:
            if connection.is_connected():
                connection.close()

    def complex_compund_query(
        self, query: str, list_quantity: int, list_prefix_name: str
    ):
        """
        """

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query)

            lists = [[] for _ in range(list_quantity)]

            for i in range(list_quantity):
                globals()[f"{list_prefix_name}{i + 1}"] = lists[i]

            for row in cursor.fetchall():
                for i in range(list_quantity):
                    globals()[f"{list_prefix_name}{i + 1}"].append(row[i])

            return lists

        except mysql.connector.Error as err:
            st.error("Erro ao consultar dados compostos: {}".format(err))

        finally:
            if connection.is_connected():
                connection.close()

    def complex_consult_query(self, query: str):

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

    def treat_simple_result(self, value_to_treat: list, values_to_remove: list):

        final_result = str(value_to_treat)

        for i in range(0, len(values_to_remove)):
            final_result = final_result.replace("{}".format(values_to_remove[i]), "")

        return final_result

    def treat_numerous_simple_result(
        self, values_to_treat: list, values_to_remove: list
    ):

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
                final_str = final_str.replace("{}".format(values_to_remove[i]), "")
            final_list.append(final_str)

        return final_list

    def treat_complex_result(self, values_to_treat: list, values_to_remove: list):

        aux_str = ""
        aux_list = []

        for i in range(0, len(values_to_treat)):
            aux_str = str(values_to_treat[i])
            aux_str = aux_str.split(", ")
            aux_list.append(aux_str)

        final_str = ""
        final_list = []

        for i in range(0, len(aux_list)):
            aux_str = str(aux_list[i])
            aux_list = aux_str.split(", ")
            for i in range(0, len(aux_list)):
                final_str = str(aux_list[i])
                for i in range(0, len(values_to_remove)):
                    final_str = final_str.replace("{}".format(values_to_remove[i]), "")
                final_list.append(final_str)

        return final_list

    def check_if_value_exists(self, query: str):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchone() is not None

    def update_table_registers(self, table: str, table_field: str, id_list: list):

        for i in range(0, len(id_list)):

            update_id_query = """UPDATE {} SET pago = 'S' WHERE id_{} = {}""".format(
                table, table_field, id_list[i]
            )

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

    def update_table_unique_register(
        self, query: str, success_message: str, error_message: str
    ):

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
