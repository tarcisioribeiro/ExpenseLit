from functions.query_executor import QueryExecutor
from functions.create_user import CreateUser
from functions.login import Login
from dictionary.vars import to_remove_list
from dictionary.sql import check_user_query
import os
import streamlit as st
import mysql.connector

if os.name == "posix":

    st.set_page_config(page_title='ExpenseLit - Controle Financeiro', page_icon=':moneybag:',layout="wide", initial_sidebar_state="auto", menu_items=None)

    hide_streamlit_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}
                        </style>
                        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    actual_path = os.getcwd()

    software_env_path = '{}/.env'.format(actual_path)
    session_state_path = '{}/data/cache/session_state.py'.format(actual_path)

    if not os.path.isfile(software_env_path):
        from time import sleep
        import streamlit as st

        col1, col2, col3 = st.columns(3)

        with col1:
            st.header(body=":dollar: ExpenseLit - Controle Financeiro")

        with col2:
            st.error(body="Não foi configurado o ambiente de conexão. Informe os dados de conexão do banco de dados.")

        st.divider()

        col4, col5, col6 = st.columns(3)

        with col5:
            with st.expander(label="Dados da conexão", expanded=True):
                db_port = 3306
                db_hostname = "localhost"
                db_user = "root"
                db_password = st.text_input(label="Senha do banco de dados", type="password")
                confirm_database_informations = st.checkbox(label="Confirmar Dados")

            record_database_informations = st.button(label=":floppy_disk: Gravar informações")

            if confirm_database_informations and record_database_informations:
                with st.spinner(text="Aguarde..."):
                    sleep(2.5)

                if db_hostname != "" and db_user != "" and db_password != "":
                    try:
                        connection = mysql.connector.connect(host=db_hostname, database='financas', user=db_user, password=db_password, port=db_port)
                        if connection.is_connected():
                            with col6:
                                cl1, cl2 = st.columns(2)
                                with cl2:
                                    st.success(body="Conexão bem-sucedida ao banco de dados!")
                            with open(software_env_path, 'w') as env_archive:
                                env_archive.write("DB_PORT={}".format(db_port))
                                env_archive.write("\nDB_HOSTNAME={}".format(db_hostname))
                                env_archive.write("\nDB_USER={}".format(db_user))
                                env_archive.write("\nDB_NAME=financas")
                                env_archive.write("\nDB_PASSWORD={}".format(db_password))
                            with col6:
                                cl1, cl2 = st.columns(2)
                                with cl2:
                                    st.success(body="Dados gravados com sucesso!")
                                    sleep(5)
                                    import subprocess
                                    command = "sudo systemctl restart expenselit.service"
                                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                                    print("Saída:", result.stdout)
                                    print("Erro:", result.stderr)

                    except mysql.connector.Error as error:
                        with col6:
                            cl1, cl2 = st.columns(2)
                            with cl2:
                                if error.errno == 1049:
                                    st.error(body="Erro ao conectar ao MySQL: O banco de dados financas não existe. Faça a importação do arquivo de backup/implantação.")
                                elif error.errno == 1045:
                                    st.error(body="Conexão não realizada. Revise os dados de conexão e tente novamente.")
                                else:
                                    st.error(body="Erro ao conectar ao MySQL: {} .".format(error))

                elif db_hostname == "" or db_user == "" or db_password == "":
                    with col6:
                        cl1, cl2 = st.columns(2)
                        with cl2:
                            if db_hostname == "":
                                st.error(body="O endereço do banco de dados não foi informado.")
                            if db_user == "":
                                st.error(body="O usuário do banco de dados não foi informado.")
                            if db_password == "":
                                st.error(body="A senha do banco de dados não foi informada.")

            elif confirm_database_informations == False and record_database_informations:
                with col6:
                    cl1, cl2 = st.columns(2)
                with cl2:
                    st.warning(body="Confirme e revise os dados antes de prosseguir.")

    if not os.path.isfile(session_state_path):
        with open(session_state_path, 'w') as session_state_archive:
            session_state_archive.write("logged_user = ''")
            session_state_archive.write("\nlogged_user_password = ''")

    if os.path.isfile(software_env_path):
        try:
            from dictionary.db_config import db_config
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                def main():
                    query_executor = QueryExecutor()
                    user_quantity = query_executor.simple_consult_brute_query(check_user_query)
                    user_quantity = query_executor.treat_simple_result(user_quantity, to_remove_list)
                    user_quantity = int(user_quantity)

                    if user_quantity == 0:
                        CreateUser().main_menu()

                    elif user_quantity > 0:
                        if 'is_logged_in' not in st.session_state:
                            st.session_state.is_logged_in = False

                        if st.session_state.is_logged_in:
                            from screens.app import App
                            App().main_menu()
                        else:
                            try:
                                call_user = Login()
                                call_user.get_login()
                            except KeyError:
                                st.warning(body=":warning: Alguns erros no Login.")

                if __name__ == "__main__":
                    main()

        except mysql.connector.Error as error:
            col1, col2, col3 = st.columns(3)

            with col2:
                if error.errno == 1049:
                    st.error(body="Erro ao conectar ao MySQL: O banco de dados {} não existe. Faça a importação do arquivo de backup/implantação.".format(db_config["database"]))
                else:
                    st.error(body="Erro ao conectar ao MySQL: {} .".format(error))

        except TypeError as type_error:
            st.info(type_error)

elif os.name == 'nt':
    import flet as ft
    from functions.query_executor import QueryExecutor


    sample_sql_query = "SELECT COUNT(id_usuario) FROM usuarios;"
    returned_value = QueryExecutor().simple_consult_brute_query(query=sample_sql_query)


    def main(page: ft.Page):
        page.title = "Flet counter example"
        text_tuple = ft.Text(returned_value)
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.add(text_tuple)

        txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

        def minus_click(e):
            txt_number.value = str(int(txt_number.value) - 1)
            page.update()

        def plus_click(e):
            txt_number.value = str(int(txt_number.value) + 1)
            page.update()

        page.add(
            ft.Row(
                [
                    ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                    txt_number,
                    ft.IconButton(ft.Icons.ADD, on_click=plus_click),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    ft.app(main)
