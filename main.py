try:

    import os
    import streamlit as st
    import mysql.connector

    st.set_page_config(page_title='Controle Financeiro', page_icon=':moneybag:', layout="wide", initial_sidebar_state="auto", menu_items=None)

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

        with col2:
            st.error(body="Não foi configurado o ambiente de conexão. Informe os dados de conexão.")
        
        st.divider()

        col4, col5, col6 = st.columns(3)

        with col5:
            with st.expander(label="Dados da conexão", expanded=True):
                db_port = st.number_input(label="Porta do banco de dados", step=1, value=3306)
                db_hostname = st.text_input(label="Host do banco de dados", placeholder="localhost")
                db_user = st.text_input(label="Usuário do banco de dados", placeholder="root")
                db_password = st.text_input(label="Senha do banco de dados", type="password")
                confirm_database_informations = st.checkbox(label="Confirmar Dados")

            record_database_informations = st.button(label=":floppy_disk: Gravar informações")

            if confirm_database_informations and record_database_informations:

                with st.spinner(text="Aguarde..."):
                    sleep(3)
                
                try:
                    connection = mysql.connector.connect(
                        host=db_hostname,
                        database='financas',
                        user=db_user,
                        password=db_password,
                        port=db_port 
                    )
                    
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
                                command = "sudo systemctl restart fcscript.service"
                                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                                print("Saída:", result.stdout)
                                print("Erro:", result.stderr)

                except mysql.connector.Error as error:
                    with col6:
                        cl1, cl2 = st.columns(2)
                        with cl2:
                            if error.errno == 1049:
                                st.error(body="Erro ao conectar ao MySQL: O banco de dados financas não existe. Faça a importação do arquivo de backup/implantação.", icon="🚨")
                            elif error.errno == 1045:
                                st.error(body="Conexão não realizada. Revise os dados de conexão e tente novamente.", icon="🚨")
                            else:
                                st.error(body="Erro ao conectar ao MySQL: {} .".format(error), icon="🚨")


    if not os.path.isfile(session_state_path):

        with open(session_state_path, 'w') as session_state_archive:
            session_state_archive.write("logged_user = ''")
            session_state_archive.write("\nlogged_user_password = ''")

    from dictionary.sql import check_user_query
    from dictionary.vars import to_remove_list
    from functions.login import User
    from functions.create_user import CreateUser
    from functions.query_executor import QueryExecutor

    if os.path.isfile(software_env_path):

        try:
            from dictionary.db_config import db_config

            connection = mysql.connector.connect(**db_config)
            
            if connection.is_connected():

                def main():

                    query_executor = QueryExecutor()
                    user_quantity = query_executor.simple_consult_query(check_user_query)
                    user_quantity = query_executor.treat_simple_result(user_quantity, to_remove_list)
                    user_quantity = int(user_quantity)

                    if user_quantity == 0:
                        create_user = CreateUser()
                        create_user.main_menu()

                    elif user_quantity > 0:
                        if 'is_logged_in' not in st.session_state:
                            st.session_state.is_logged_in = False

                        if st.session_state.is_logged_in:
                            from screens.app import App
                            app = App()
                            app.HomePage()
                        else:
                            try:
                                call_user = User()
                                call_user.get_login()
                            except KeyError:
                                st.warning(body=":warning: Alguns erros no Login.")

                if __name__ == "__main__":
                    main()
                

        except mysql.connector.Error as error:

            col1, col2, col3 = st.columns(3)

            with col2:
                if error.errno == 1049:
                    st.error(body="Erro ao conectar ao MySQL: O banco de dados {} não existe. Faça a importação do arquivo de backup/implantação.".format(db_config["database"]), icon="🚨")
                else:
                    st.error(body="Erro ao conectar ao MySQL: {} .".format(error), icon="🚨")

        except TypeError as type_error:
            pass

except KeyError:
    import streamlit as st
    st.rerun()
