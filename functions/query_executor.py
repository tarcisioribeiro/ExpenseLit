from dictionary.db_config import db_config
import mysql.connector
import streamlit as st


class QueryExecutor:

    def __init__(self) -> None:

        def insert_query(query, values, success_message: str, error_message: str):

            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                st.toast(":white_check_mark: {}".format(success_message))
            except mysql.connector.Error as error:
                if error.errno == 1062:
                    st.error("Já existe um registro no banco de dados com estas informações.")
                elif error.errno == 1054:
                    st.error("Há algum erro na consulta que está sendo realizada: {}".format(query))
                else:
                    st.toast(":warning: {} {}".format(error_message, error))
                    st.error(error)
                
            finally:
                if connection.is_connected():
                    connection.close()
                    st.toast(body="Inserção finalizada.")

        def simple_consult_query(query: str):

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

        def complex_compund_query(query: str, list_quantity: int, list_prefix_name: str):
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute(query)

                lists = [[] for _ in range(list_quantity)]

                for i in range(list_quantity):
                    globals()[f'{list_prefix_name}{i + 1}'] = lists[i]

                for row in cursor.fetchall():
                    for i in range(list_quantity):
                        globals()[f'{list_prefix_name}{i + 1}'].append(row[i])

                return lists

            except mysql.connector.Error as err:
                st.error("Erro ao consultar dados compostos: {}".format(err))

            finally:
                if connection.is_connected():
                    connection.close()

        def complex_consult_query(query: str):

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

        def treat_simple_result(value_to_treat, values_to_remove: list):

            final_result = str(value_to_treat)
            
            for i in range(0, len(values_to_remove)):
                final_result = final_result.replace("{}".format(values_to_remove[i]), "")

            return final_result

        def treat_numerous_simple_result(values_to_treat, values_to_remove: list):

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

        def treat_complex_result(values_to_treat, values_to_remove: list):

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

        def check_if_value_exists(query):
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(query)
            return cursor.fetchone() is not None

        def update_table_registers(table: str, table_field: str, id_list: list):

            for i in range(0, len(id_list)):

                update_id_query = """UPDATE {} SET pago = 'S' WHERE id_{} = {}""".format(table, table_field, id_list[i])

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

        def update_table_unique_register(query: str, success_message: str, error_message: str):

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

        self.insert_query = insert_query
        self.simple_consult_query = simple_consult_query
        self.complex_compund_query = complex_compund_query
        self.complex_consult_query = complex_consult_query
        self.treat_simple_result = treat_simple_result
        self.treat_numerous_simple_result = treat_numerous_simple_result
        self.treat_complex_result = treat_complex_result
        self.check_if_value_exists = check_if_value_exists
        self.update_table_registers = update_table_registers
        self.update_table_unique_register = update_table_unique_register