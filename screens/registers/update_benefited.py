from data.cache.session_state import logged_user
from functions.login import Login
from dictionary.vars import today
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from functions.get_actual_time import GetActualTime
from time import sleep
import streamlit as st


class Benefited:
    """
    Classe que representa o cadastro e atualização dos dados dos beneficiários.
    """

    def update_benefited(self):
        """
        Atualiza os dados do beneficiado.
        """

        col1, col2, col3 = st.columns(3)

        with col2:
            st.warning(body="Em desenvolvimento.")

    def new_benefited(self):
        """
        Cadastra um novo beneficiado.
        """
        user_name, user_document = Login().get_user_doc_name()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(body=":computer: Entrada de Dados")

            with st.expander(label="Dados do credor", expanded=True):
                benefited_name = st.text_input(
                    label=":lower_left_ballpoint_pen: Nome", max_chars=100)
                benefited_document = st.text_input(
                    label=":lower_left_ballpoint_pen: Documento")
                benefited_phone = st.text_input(
                    label=":telephone_receiver: Telefone/Celular", max_chars=11)
                confirm_benefited_data = st.checkbox(
                    label="Confirmar dados")

            register_new_creditor = st.button(
                label=":floppy_disk: Cadastrar beneficiado")

            if confirm_benefited_data and register_new_creditor:
                with col2:
                    st.subheader(
                        body=":white_check_mark: Validação de Dados")

                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)
                    with st.expander(label="Validação dos dados", expanded=True):
                        is_document_valid = Documents().validate_owner_document(
                            benefited_document)
                        if is_document_valid == True and benefited_name != '' and benefited_phone != '':
                            benefited_document = int(benefited_document)
                            st.success(body="Documento válido.")

                        if (benefited_name != user_name) and (benefited_document != int(user_document)):
                            insert_benefited_query = '''INSERT INTO beneficiados (`nome`, `documento`, `telefone`) VALUES (%s, %s, %s)'''
                            query_values = (
                                benefited_name, benefited_document, benefited_phone)

                            QueryExecutor().insert_query(
                                insert_benefited_query, query_values, "Beneficiado cadastrado com sucesso!", "Erro ao cadastrar beneficiado:")

                            actual_time = GetActualTime().get_actual_time()
                            log_query = '''INSERT INTO logs_atividades (data_log, horario_log, usuario_log, tipo_log, conteudo_log) VALUES (%s, %s, %s, %s, %s)'''
                            log_values = (today, actual_time, logged_user, "Cadastro",
                                          "O usuário cadastrou o beneficiado {}.".format(benefited_name))

                            QueryExecutor().insert_query(
                                log_query, log_values, "Log gravado com sucesso!", "Erro ao gravar log:")

                        if (benefited_name == user_name) or (benefited_document == int(user_document)):
                            if benefited_name == user_name:
                                st.error(
                                    body="Este beneficiado já foi cadastrado anteriormente.")
                            if benefited_document == int(user_document):
                                st.error(
                                    body="Este documento já está sendo utilizado por outro beneficiado.")

    def main_menu(self):
        """
        Exibe o menu.
        """
        col1, col2, col3 = st.columns(3)

        menu_options = ["Cadastrar beneficiado", "Atualizar beneficiado"]

        with col3:
            cl1, cl2 = st.columns(2)

        with cl2:
            selected_option = st.selectbox(
                label="Menu", options=menu_options)

        if selected_option == "Cadastrar beneficiado":
            self.new_benefited()
        elif selected_option == "Atualizar beneficiado":
            self.update_benefited()
