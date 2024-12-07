from data.cache.session_state import logged_user
from dictionary.sql import check_user_query, check_if_user_document_exists_query, check_if_user_login_exists_query
from dictionary.vars import to_remove_list
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from time import sleep
import streamlit as st


class CreateUser:

    def __init__(self):

        query_executor = QueryExecutor()
        document = Documents()

        def check_if_user_exists(login: str, document: str):
            
            formatted_check_if_user_document_exists_query = check_if_user_document_exists_query.format(document)
            formatted_check_if_user_login_exists_query = check_if_user_login_exists_query.format(login)

            check_if_user_document_exists = query_executor.simple_consult_query(formatted_check_if_user_document_exists_query)
            check_if_user_document_exists = query_executor.treat_simple_result(check_if_user_document_exists, to_remove_list)
            check_if_user_document_exists = int(check_if_user_document_exists)

            check_if_user_login_exists = query_executor.simple_consult_query(formatted_check_if_user_login_exists_query)
            check_if_user_login_exists = query_executor.treat_simple_result(check_if_user_login_exists, to_remove_list)
            check_if_user_login_exists = int(check_if_user_login_exists)

            if check_if_user_document_exists == 0 and check_if_user_login_exists == 0:
                return True
            else:
                if check_if_user_login_exists >= 1 and check_if_user_document_exists == 0:
                    st.error(body="O login {} já está em uso.".format(login))
                elif check_if_user_document_exists >= 1 and check_if_user_login_exists == 0:
                    st.error(body="O documento {} já está em uso.".format(document))
                elif check_if_user_login_exists >= 1 and check_if_user_login_exists >= 1:
                    st.error(body="O documento {} e o login {} já estão em uso.".format(document, login))
                return False


        def main_menu():

            check_user_quantity = query_executor.simple_consult_query(check_user_query)
            check_user_quantity = query_executor.treat_simple_result(
                check_user_quantity, to_remove_list
            )
            check_user_quantity = int(check_user_quantity)

            sex_options = {
                "Masculino": "M",
                "Feminino": "F"
                }

            if check_user_quantity == 0:
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.subheader(body=":floppy_disk: Cadastro de usuário")
                st.divider()

            col4, col5, col6 = st.columns(3)

            if check_user_quantity == 0:

                with col6:
                    cl1, cl2 = st.columns(2)
                    with cl2:
                        st.warning(body=":warning: Nenhum usuário cadastrado. Cadastre o primeiro usuário.")

            with col5:
                with st.expander(label="Dados do usuário", expanded=True):

                    user_login = st.text_input(label="Login de usuário",max_chars=25,help="O nome do usuário deve ter no máximo 25 caracteres.",)
                    user_password = st.text_input(label="Senha de usuário",max_chars=100,help="A senha deve conter no máximo 100 caracteres.",type="password")
                    user_name = st.text_input(label="Nome completo do usuário",max_chars=100,help="Informe aqui seu nome completo.",)
                    user_document = st.text_input(label="CPF do usuário")
                    user_phone = st.text_input(label="Telefone/Celular")
                    user_sex = st.selectbox(label="Sexo do usuário", options=sex_options.keys())
                    confirm_values = st.checkbox(label="Confirmar dados")

                insert_new_user_button = st.button(label=":floppy_disk: Cadastrar novo usuário")

                if insert_new_user_button and confirm_values:
                    with col4:
                        with st.spinner(text="Aguarde..."):
                            sleep(2)
                    user_sex = sex_options[user_sex]

                    with col6:
                        cl1, cl2 = st.columns(2)
                        with cl2:
                            is_document_valid = document.validate_owner_document(user_document)

                    if user_login != "" and user_password != "" and user_name != "" and is_document_valid == True and user_phone != "" and user_sex != "":
                        with cl2:
                            st.success("O documento {} é válido.".format(user_document))
                            sleep(3)

                        if check_user_quantity == 0:
                            insert_new_user_query = """INSERT INTO usuarios (login, senha, nome, cpf, telefone, sexo) VALUES (%s, %s, %s, %s, %s, %s)"""
                            new_user_values = (user_login,user_password,user_name,user_document,user_phone,user_sex)
                            query_executor.insert_query(insert_new_user_query,new_user_values,"Novo usuário cadastrado com sucesso!","Erro ao cadastrar novo usuário:")

                            insert_new_creditor_query = """INSERT INTO credores (nome, documento, telefone) VALUES (%s, %s, %s)"""
                            new_creditor_values = (user_name,user_document,user_phone)
                            query_executor.insert_query(insert_new_creditor_query,new_creditor_values,"Novo credor cadastrado com sucesso!","Erro ao cadastrar novo credor:")

                            insert_new_benefited_query = """INSERT INTO beneficiados (nome, documento, telefone) VALUES (%s, %s, %s)"""
                            new_benefited_values = (user_name,user_document,user_phone)
                            query_executor.insert_query(insert_new_benefited_query,new_benefited_values,"Novo beneficiado cadastrado com sucesso!","Erro ao cadastrar novo beneficiado:")

                            log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                            log_values = (user_login, "Registro", "O usuário foi cadastrado no sistema.")
                            query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                            with col4:
                                with st.spinner(text="Recarregando..."):
                                    sleep(2.5)
                                    st.rerun()

                        elif check_user_quantity >= 1:

                            with col6:
                                cl1, cl2 = st.columns(2)
                                with cl2:
                                    is_data_valid = check_if_user_exists(user_login, user_document)

                                    if is_data_valid == True:
                                        insert_new_user_query = """INSERT INTO usuarios (login, senha, nome, cpf, sexo) VALUES (%s, %s, %s, %s, %s)"""
                                        new_user_values = (user_login,user_password,user_name,user_document,user_sex)
                                        query_executor.insert_query(insert_new_user_query,new_user_values,"Novo usuário cadastrado com sucesso!","Erro ao cadastrar novo usuário:")

                                        insert_new_creditor_query = """INSERT INTO credores (nome, documento) VALUES (%s, %s)"""
                                        new_creditor_values = (user_name,user_document)
                                        query_executor.insert_query(insert_new_creditor_query,new_creditor_values,"Novo credor cadastrado com sucesso!","Erro ao cadastrar novo credor:")

                                        insert_new_benefited_query = """INSERT INTO beneficiados (nome, documento) VALUES (%s, %s)"""
                                        new_benefited_values = (user_name,user_document)
                                        query_executor.insert_query(insert_new_benefited_query,new_benefited_values,"Novo beneficiado cadastrado com sucesso!","Erro ao cadastrar novo beneficiado:")

                                        log_query = '''INSERT INTO financas.logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES ( %s, %s, %s);'''
                                        log_values = (logged_user, "Registro", "Cadastrou o usuário {} associado ao documento {} no sistema.".format(user_name, user_document))
                                        query_executor.insert_query(log_query, log_values, "Log gravado.", "Erro ao gravar log:")

                                        sleep(2.5)
                                    elif is_data_valid >= False:
                                        pass

                    elif user_login != "" and user_password != "" and user_name != "" and is_document_valid == False and user_sex != "":
                        with cl2:
                            st.error("O documento {} é inválido.".format(user_document),icon="🚨")

                elif confirm_values == False:
                    st.warning(body=":warning: Revise os dados e confirme-os antes de prosseguir.")

        self.main_menu = main_menu


if __name__ == "__main__":
    create_user = CreateUser()
    create_user.main_menu()
