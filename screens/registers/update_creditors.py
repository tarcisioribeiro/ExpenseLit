from functions.login import Login
from dictionary.vars import today
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from functions.get_actual_time import GetActualTime
from time import sleep
import streamlit as st


class Creditors:
    """
    Classe que representa o cadastro e atualização dos dados dos credores.
    """

    def update_creditor(self):
        """
        Atualiza os dados do credor.
        """

        col1, col2, col3 = st.columns(3)

        with col2:
            st.warning(body="Em desenvolvimento.")

    def new_creditor(self):
        """
        Realiza o cadastro de um novo credor.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(body=":computer: Entrada de Dados")

            with st.expander(label="Dados do credor", expanded=True):
                creditor_name = st.text_input(
                    label=":lower_left_ballpoint_pen: Nome", max_chars=100)
                creditor_document = st.text_input(
                    label=":lower_left_ballpoint_pen: Documento")
                creditor_phone = st.text_input(
                    label=":telephone_receiver: Telefone/Celular", max_chars=11)
                confirm_creditor_data = st.checkbox(
                    label="Confirmar dados")

            register_new_creditor = st.button(
                label=":floppy_disk: Cadastrar credor")

            if confirm_creditor_data and register_new_creditor:
                with col2:
                    st.subheader(
                        body=":white_check_mark: Validação de Dados")
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)
                    with st.expander(label="Aviso", expanded=True):

                        is_document_valid = Documents().validate_owner_document(
                            creditor_document)

                        if is_document_valid == True and creditor_name != '' and creditor_phone != '':
                            creditor_document = int(creditor_document)
                            st.success(body="Documento válido.")

                            if (creditor_name != user_name) and (creditor_document != int(user_document)):

                                insert_creditor_query = '''INSERT INTO credores (`nome`, `documento`, `telefone`) VALUES (%s, %s, %s)'''
                                query_values = (
                                    creditor_name, creditor_document, creditor_phone)

                                QueryExecutor().insert_query(
                                    insert_creditor_query, query_values, "Credor cadastrado com sucesso!", "Erro ao cadastrar credor:")

                                actual_time = GetActualTime().get_actual_time()
                                log_query = '''INSERT INTO logs_atividades (data_log, horario_log, usuario_log, tipo_log, conteudo_log) VALUES (%s, %s, %s, %s, %s)'''
                                log_values = (today, actual_time, logged_user, "Cadastro",
                                              "O usuário cadastrou o credor {}.".format(creditor_name))

                                QueryExecutor().insert_query(
                                    log_query, log_values, "Log gravado com sucesso!", "Erro ao gravar log:")

                            if (creditor_name == user_name) or (creditor_document == int(user_document)):
                                if creditor_name == user_name:
                                    st.error(
                                        body="Este credor já foi cadastrado anteriormente.")
                                if creditor_document == int(user_document):
                                    st.error(
                                        body="Este documento já está sendo utilizado por outro credor.")

                        elif is_document_valid == False:
                            st.error(body="O documento {} informado não é válido.".format(
                                creditor_document))

    def main_menu(self):
        """
        Menu principal.
        """
        col1, col2, col3 = st.columns(3)
        with col3:
            cl1, cl2 = st.columns(2)
        menu_options = ["Cadastrar credor", "Atualizar credor"]

        with cl2:
            selected_option = st.selectbox(
                label="Menu", options=menu_options)

        if selected_option == "Cadastrar credor":
            self.new_creditor()
        elif selected_option == "Atualizar credor":
            self.update_creditor()
