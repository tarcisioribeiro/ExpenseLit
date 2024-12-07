from data.cache.session_state import logged_user
from dictionary.user_stats import user_document, user_name, user_phone
from dictionary.vars import today
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from functions.get_actual_time import GetActualTime
from time import sleep
import streamlit as st


class Creditors:
    def __init__(self):

        query_executor = QueryExecutor()
        document = Documents()
        time = GetActualTime()
        
        col1, col2, col3 = st.columns(3)

        def update_creditor():
            with col2:
                st.warning(body="Em desenvolvimento.", icon="⚠️")            

        def new_creditor():
            with col1:
                with st.expander(label="Dados do credor", expanded=True):
                    creditor_name = st.text_input(label="Nome", max_chars=100)
                    creditor_document = st.text_input(label="Documento")
                    creditor_phone = st.text_input(label="Telefone/Celular", max_chars=11)
                    confirm_creditor_data = st.checkbox(label="Confirmar dados")

                register_new_creditor = st.button(label=":floppy_disk: Cadastrar credor")

                if confirm_creditor_data and register_new_creditor:
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(2)
                        with st.expander(label="Validação dos dados", expanded=True):
                            is_document_valid = document.validate_owner_document(creditor_document)
                            if is_document_valid == True and creditor_name != '' and creditor_phone != '':
                                creditor_document = int(creditor_document)
                                st.success(body="Documento válido.")

                                if (creditor_name != user_name) and (creditor_document != int(user_document)) and (creditor_phone != user_phone):

                                    insert_creditor_query = '''INSERT INTO credores (`nome`, `documento`, `telefone`) VALUES (%s, %s, %s)'''
                                    query_values = (creditor_name, creditor_document, creditor_phone)

                                    query_executor.insert_query(insert_creditor_query, query_values, "Credor cadastrado com sucesso!", "Erro ao cadastrar credor:")

                                    actual_time = time.get_actual_time()
                                    log_query = '''INSERT INTO logs_atividades (data_log, horario_log, usuario_log, tipo_log, conteudo_log) VALUES (%s, %s, %s, %s, %s)'''
                                    log_values = (today, actual_time, logged_user, "Cadastro", "O usuário cadastrou o credor {}.".format(creditor_name))

                                    query_executor.insert_query(log_query, log_values, "Log gravado com sucesso!", "Erro ao gravar log:")
                                
                                if (creditor_name == user_name) or (creditor_document == int(user_document)) or (creditor_phone == user_phone):
                                    if creditor_name == user_name:
                                      st.error(body="Este credor já foi cadastrado anteriormente.")
                                    if creditor_document == int(user_document):
                                        st.error(body="Este documento já está sendo utilizado por outro credor.")
                                    if creditor_phone == user_phone:
                                        st.error(body="Este número de telefone já está sendo utilizado.")

        def main_menu():
            menu_options = ["Cadastrar credor", "Atualizar credor"]

            with col3:
                cl1, cl2 = st.columns(2)

            with cl2:
                selected_option = st.selectbox(label="Menu", options=menu_options)

            if selected_option == "Cadastrar credor":
                new_creditor()
            elif selected_option == "Atualizar credor":
                update_creditor()

        self.main_menu = main_menu