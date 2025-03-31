from functions.login import Login
from dictionary.vars import today, TO_REMOVE_LIST
from dictionary.sql import benefited_quantity_query, beneficiaries_query
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from functions.get_actual_time import GetActualTime
from time import sleep
import streamlit as st


class Benefited:
    """
    Classe que representa o cadastro e atualização dos dados dos beneficiários.
    """
    def is_benefited_new_values_valid(self, benefited_id: int, benefited_new_name: str, benefited_new_document: str, benefited_new_phone: str):
        """
        Realiza a verificação dos novos dados passados do beneficiado. Caso sejam válidos e não utilizados, é retornada a resposta positiva, caso contrário, é retornada uma resposta negativa.

        Parameters
        ----------
        benefited_new_name : str
            O novo nome pretendido para o beneficiado.
        benefited_new_document : str
            O novo documento pretendido para o beneficiado.
        benefited_new_phone : str
            O novo telefone pretendido para o beneficiado.

        Returns
        -------
        is_new_register_valid : boolean
            O retorno da verificação de validade dos novos dados do registro.
        """

        is_new_register_valid = True

        is_new_name_valid_query = "SELECT COUNT(id_beneficiado) FROM beneficiados WHERE nome = %s AND id_beneficiado <> %s;"
        is_new_name_valid = QueryExecutor().simple_consult_query(is_new_name_valid_query, params=(benefited_new_name, benefited_id))
        is_new_name_valid = QueryExecutor().treat_simple_result(is_new_name_valid, TO_REMOVE_LIST)

        is_document_valid = Documents().validate_owner_document(benefited_new_document)

        is_new_document_valid_query = "SELECT COUNT(id_beneficiado) FROM beneficiados WHERE documento = %s AND id_beneficiado <> %s;"
        is_new_document_valid = QueryExecutor().simple_consult_query(is_new_document_valid_query, params=(benefited_new_document, benefited_id))
        is_new_document_valid = QueryExecutor().treat_simple_result(is_new_document_valid, TO_REMOVE_LIST)

        if is_document_valid == False:
            is_new_register_valid = False
            st.error(body="Os novos dados não são válidos.")

        is_new_phone_valid_query = "SELECT COUNT(id_beneficiado) FROM beneficiados WHERE telefone = %s AND id_beneficiado <> %s;"
        is_new_phone_valid = QueryExecutor().simple_consult_query(is_new_phone_valid_query, params=(benefited_new_phone, benefited_id))
        is_new_phone_valid = QueryExecutor().treat_simple_result(is_new_phone_valid, TO_REMOVE_LIST)

        if is_new_name_valid == "1":
                st.error(body="O nome {} já está em uso.".format(benefited_new_name))
        if is_new_document_valid == "1":
            st.error(body="O documento {} já está em uso.".format(benefited_new_document))
        if is_new_phone_valid == "1":
            st.error(body="O telefone {} já está em uso.".format(benefited_new_phone))

        is_entire_data_valid_query = "SELECT COUNT(id_beneficiado) FROM beneficiados WHERE nome = %s AND documento = %s AND telefone = %s;"
        is_entire_data_valid = QueryExecutor().simple_consult_query(is_entire_data_valid_query, params=(benefited_new_name, benefited_new_document, benefited_new_phone))
        is_entire_data_valid = QueryExecutor().treat_simple_result(is_entire_data_valid, TO_REMOVE_LIST)

        if is_new_name_valid == "0" and is_new_document_valid == "0" and is_new_phone_valid == "0" and is_entire_data_valid == "0":
            is_new_register_valid = True
            st.success(body="Os novos dados são válidos.")
        elif is_new_name_valid == "1" or is_new_document_valid == "1" or is_new_phone_valid == "1":
            is_new_register_valid = False
            st.error(body="Os novos dados não são válidos.")

        return is_new_register_valid

    def update_benefited(self):
        """
        Atualiza os dados do beneficiado.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        benefited_quantity = QueryExecutor().simple_consult_query(query=benefited_quantity_query, params=(user_name, user_document))
        benefited_quantity = QueryExecutor().treat_simple_result(benefited_quantity, TO_REMOVE_LIST)
        benefited_quantity = int(benefited_quantity)

        if benefited_quantity == 0:
            col1, col2, col3 = st.columns(3)
            with col2:
                st.warning(body="Ainda não foram cadastrados beneficiados.")

        elif benefited_quantity >= 1:

            beneficiaries = QueryExecutor().complex_consult_query(query=beneficiaries_query, params=(user_name, user_document))
            beneficiaries = QueryExecutor().treat_numerous_simple_result(beneficiaries, TO_REMOVE_LIST)

            col1, col2, col3, col4 = st.columns(4)
            
            with col4:
                selected_beneficiary = st.selectbox(label="Beneficiado", options=beneficiaries)

            beneficiaries_complete_data_query = """SELECT beneficiados.id_beneficiado, beneficiados.nome, beneficiados.documento, beneficiados.telefone FROM beneficiados INNER JOIN usuarios ON beneficiados.nome <> usuarios.nome AND beneficiados.documento <> usuarios.documento WHERE usuarios.nome = %s AND usuarios.documento = %s AND beneficiados.nome = %s;"""
            beneficiaries_complete_data = QueryExecutor().complex_compund_query(query=beneficiaries_complete_data_query, list_quantity=4, params=(user_name, user_document, selected_beneficiary))
            beneficiaries_complete_data = QueryExecutor().treat_complex_result(beneficiaries_complete_data, TO_REMOVE_LIST)

            with col1:
                st.subheader(body=":floppy_disk: Registro")
                with st.expander(label="Dados atuais de {}".format(selected_beneficiary), expanded=True):
                    st.write("**Nome**")
                    st.info(beneficiaries_complete_data[1])
                    st.write("**Documento**")
                    st.info(beneficiaries_complete_data[2])
                    st.write("**Telefone**")
                    st.info(beneficiaries_complete_data[3])
                confirm_selection = st.checkbox(label="Confirmar seleção")

            if confirm_selection:

                with col2:

                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(label="Novos dados de {}".format(selected_beneficiary), expanded=True):
                        new_name = st.text_input(label="**Novo nome**", max_chars=100, help="Novo nome do beneficiado. Preferível que seja o nome completo.", placeholder=beneficiaries_complete_data[1])
                        new_document = st.text_input(label="**Novo documento**", help="Novo CPF/CNPJ do beneficiado, sem barras, pontos e hifens.", placeholder=beneficiaries_complete_data[2])
                        new_phone = st.text_input(label="**Novo telefone**", max_chars=11, help="Novo telefone do beneficiado, apenas números.", placeholder=beneficiaries_complete_data[3])

                    confirm_changes_button = st.button(label=":floppy_disk: Confirmar mudanças")

                    if confirm_changes_button:
                        if new_name == "":
                            new_name = beneficiaries_complete_data[1]
                        if new_document == "":
                            new_document = beneficiaries_complete_data[2]
                        if new_phone == "":
                            new_phone = beneficiaries_complete_data[3]

                        with col3:
                            with st.spinner(text="Aguarde..."):
                                sleep(1.5)
                            st.subheader(body=":white_check_mark: Validação de Dados")
                            with st.expander(label="Validação", expanded=True):
                                is_data_passed_valid = self.is_benefited_new_values_valid(int(beneficiaries_complete_data[0]), new_name, new_document, new_phone)

                            if is_data_passed_valid == True:
                                get_loans_ids_query = """SELECT id_emprestimo FROM emprestimos WHERE devedor = %s AND documento_devedor = %s;"""
                                loans_ids = QueryExecutor().complex_consult_query(query=get_loans_ids_query, params=(beneficiaries_complete_data[1], beneficiaries_complete_data[2]))
                                loans_ids = QueryExecutor().treat_complex_result(loans_ids, TO_REMOVE_LIST)

                                if len(loans_ids) >= 1:
                                    ids = []
                                    for i in range(0, len(loans_ids)):
                                        ids.append(int(loans_ids[i]))
                                    ids = tuple(ids)
                                    new_benefited_loans_data_query = """UPDATE emprestimos SET devedor = '{}', documento_devedor = {} WHERE devedor = '{}' AND documento_devedor = {} AND id_emprestimo IN{};""".format(
                                        new_name, new_document, beneficiaries_complete_data[1], beneficiaries_complete_data[2], ids)
                                    QueryExecutor().update_table_unique_register(new_benefited_loans_data_query, "Registros atualizados com sucesso!", "Erro ao atualizar registros:")

                                new_benefited_data_query = """UPDATE beneficiados SET nome = '{}', documento = {}, telefone = '{}' WHERE id_beneficiado = {};""".format(
                                    new_name, new_document, new_phone, int(beneficiaries_complete_data[0]))
                                QueryExecutor().update_table_unique_register(new_benefited_data_query, "Beneficiado atualizado com sucesso!", "Erro ao atualizar beneficiado:")

                                actual_time = GetActualTime().get_actual_time()
                                log_query = '''INSERT INTO logs_atividades (data_log, horario_log, usuario_log, tipo_log, conteudo_log) VALUES (%s, %s, %s, %s, %s)'''
                                log_values = (today, actual_time, logged_user, "Atualização", "O usuário atualizou o beneficiado {}.".format(beneficiaries_complete_data[1]))

                                QueryExecutor().insert_query(log_query, log_values, "Log gravado com sucesso!", "Erro ao gravar log:")
                                

    def new_benefited(self):
        """
        Cadastra um novo beneficiado.
        """
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(return_option="user_login_password")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(body=":computer: Entrada de Dados")

            with st.expander(label="Dados do credor", expanded=True):
                benefited_name = st.text_input(label=":lower_left_ballpoint_pen: Nome", max_chars=100, help="Nome do beneficiado. Preferível que seja o nome completo.")
                benefited_document = st.text_input(label=":lower_left_ballpoint_pen: Documento", help="CPF/CNPJ do beneficiado, sem barras, pontos e hifens.")
                benefited_phone = st.text_input(label=":telephone_receiver: Telefone/Celular", max_chars=11, help="Telefone do beneficiado, apenas números.")
                confirm_benefited_data = st.checkbox(label="Confirmar dados")

            register_new_creditor = st.button(
                label=":floppy_disk: Cadastrar beneficiado")

            if confirm_benefited_data and register_new_creditor:
                with col2:
                    st.subheader(body=":white_check_mark: Validação de Dados")

                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)

                    with st.expander(label="Validação dos dados", expanded=True):

                        is_document_valid = Documents().validate_owner_document(benefited_document)

                        if is_document_valid == True and benefited_name != '' and benefited_phone != '':
                            benefited_document = int(benefited_document)
                            st.success(body="Documento válido.")

                        if (benefited_name != user_name) and (benefited_document != int(user_document)):
                            insert_benefited_query = '''INSERT INTO beneficiados (`nome`, `documento`, `telefone`) VALUES (%s, %s, %s)'''
                            query_values = (benefited_name, benefited_document, benefited_phone)

                            QueryExecutor().insert_query(insert_benefited_query, query_values, "Beneficiado cadastrado com sucesso!", "Erro ao cadastrar beneficiado:")

                            actual_time = GetActualTime().get_actual_time()
                            log_query = '''INSERT INTO logs_atividades (data_log, horario_log, usuario_log, tipo_log, conteudo_log) VALUES (%s, %s, %s, %s, %s)'''
                            log_values = (today, actual_time, logged_user, "Cadastro", "O usuário cadastrou o beneficiado {}.".format(benefited_name))

                            QueryExecutor().insert_query(log_query, log_values, "Log gravado com sucesso!", "Erro ao gravar log:")

                        if (benefited_name == user_name) or (benefited_document == int(user_document)):
                            if benefited_name == user_name:
                                st.error(body="Este beneficiado já foi cadastrado anteriormente.")
                            if benefited_document == int(user_document):
                                st.error(body="Este documento já está sendo utilizado por outro beneficiado.")

    def main_menu(self, menu_position):
        """
        Exibe o menu.

        Parameters
        ----------
        menu_position : Any
            Define a posição de exibição do menu.
        """

        menu_options = {
            "Cadastrar beneficiado": self.new_benefited,
            "Atualizar beneficiado": self.update_benefited
        }

        with menu_position:
            selected_option = st.selectbox(
                label="Menu de Beneficiados", options=menu_options.keys())
            selected_function = menu_options[selected_option]

        st.divider()

        selected_function()
