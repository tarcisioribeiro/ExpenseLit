from dictionary.sql.creditor_queries import (
    creditors_complete_data_query,
    creditors_quantity_query,
    creditors_names_query,
    get_loans_creditor_ids_query,
    insert_creditor_query,
    is_entire_creditor_data_valid_query,
    is_new_creditor_document_valid_query,
    is_new_creditor_name_valid_query,
    is_new_creditor_phone_valid_query,
    new_creditor_data_query,
    new_creditor_loans_data_query
)
from dictionary.vars import TO_REMOVE_LIST
from functions.login import Login
from functions.query_executor import QueryExecutor
from functions.validate_document import Documents
from time import sleep
import streamlit as st


user_id, user_document = Login().get_user_data()


class Creditors:
    """
    Classe que representa o cadastro e atualização dos dados dos credores.
    """

    def is_creditor_new_values_valid(
        self,
        creditor_id: int,
        creditor_new_name: str,
        creditor_new_document: str,
        creditor_new_phone: str
    ):
        """
        Realiza a verificação dos novos dados passados do credor.
        Caso sejam válidos e não utilizados, é retornada a resposta positiva,
        caso contrário, é retornada uma resposta negativa.

        Parameters
        ----------
        creditor_new_name : str
            O novo nome pretendido para o credor.
        creditor_new_document : str
            O novo documento pretendido para o credor.
        creditor_new_phone : str
            O novo telefone pretendido para o credor.

        Returns
        -------
        is_new_register_valid : boolean
            O retorno da verificação de validade dos novos dados do registro.
        """

        is_new_register_valid = True

        is_new_name_valid = QueryExecutor().simple_consult_query(
            is_new_creditor_name_valid_query,
            params=(
                creditor_new_name,
                creditor_id
            )
        )
        is_new_name_valid = QueryExecutor().treat_simple_result(
            is_new_name_valid,
            TO_REMOVE_LIST
        )

        is_document_valid = Documents().validate_owner_document(
            creditor_new_document
        )

        is_new_document_valid = QueryExecutor().simple_consult_query(
            is_new_creditor_document_valid_query,
            params=(
                creditor_new_document,
                creditor_id
                )
            )
        is_new_document_valid = QueryExecutor().treat_simple_result(
            is_new_document_valid,
            TO_REMOVE_LIST
        )

        if is_document_valid is False:
            is_new_register_valid = False
            st.error(body="Os novos dados não são válidos.")

        is_new_phone_valid = QueryExecutor().simple_consult_query(
            is_new_creditor_phone_valid_query,
            params=(
                creditor_new_phone,
                creditor_id
                )
            )
        is_new_phone_valid = QueryExecutor().treat_simple_result(
            is_new_phone_valid,
            TO_REMOVE_LIST
        )

        if is_new_name_valid == "1":
            st.error(
                body="""
                O nome {} já está em uso.
                """.format(creditor_new_name)
            )
        if is_new_document_valid == "1":
            st.error(
                body="""
                O documento {} já está em uso.
                """.format(creditor_new_document)
            )
        if is_new_phone_valid == "1":
            st.error(
                body="""
                O telefone {} já está em uso.
                """.format(creditor_new_phone)
            )

        is_entire_data_valid = QueryExecutor().simple_consult_query(
            is_entire_creditor_data_valid_query,
            params=(
                creditor_new_name,
                creditor_new_document,
                creditor_new_phone
            )
        )
        is_entire_data_valid = QueryExecutor().treat_simple_result(
            is_entire_data_valid,
            TO_REMOVE_LIST
        )

        if (
            is_new_name_valid == "0"
            ) and (
                is_new_document_valid == "0"
            ) and (
                is_new_phone_valid == "0"
            ) and (
                is_entire_data_valid == "0"
        ):
            is_new_register_valid = True
            st.success(body="Os novos dados são válidos.")
        elif (
            is_new_name_valid == "1"
            ) or (
                is_new_document_valid == "1"
            ) or (
                is_new_phone_valid == "1"
        ):
            is_new_register_valid = False
            st.error(body="Os novos dados não são válidos.")

        return is_new_register_valid

    def update_creditor(self):
        """
        Atualiza os dados do credor.
        """

        creditors_quantity = QueryExecutor().simple_consult_query(
            query=creditors_quantity_query,
            params=(user_id, user_document)
        )
        creditors_quantity = QueryExecutor().treat_simple_result(
            creditors_quantity,
            TO_REMOVE_LIST
        )
        creditors_quantity = int(creditors_quantity)

        if creditors_quantity == 0:
            col1, col2, col3 = st.columns(3)
            with col2:
                st.warning(body="Ainda não foram cadastrados credores.")

        elif creditors_quantity >= 1:

            creditors = QueryExecutor().complex_consult_query(
                query=creditors_names_query,
                params=(user_id, user_document)
            )
            creditors = QueryExecutor().treat_simple_results(
                creditors,
                TO_REMOVE_LIST
            )

            col1, col2, col3, col4 = st.columns(4)

            with col4:
                selected_creditor = st.selectbox(
                    label="Beneficiado",
                    options=creditors
                )

            creditors_complete_data = QueryExecutor().complex_compund_query(
                query=creditors_complete_data_query,
                list_quantity=3,
                params=(user_id, user_document, selected_creditor)
            )
            creditors_complete_data = QueryExecutor().treat_complex_result(
                creditors_complete_data,
                TO_REMOVE_LIST
            )

            with col1:
                st.subheader(body=":floppy_disk: Registro")
                with st.expander(
                    label="Dados atuais de {}".format(selected_creditor),
                    expanded=True
                ):
                    st.write("**Nome**")
                    st.info(selected_creditor)
                    st.write("**Documento**")
                    st.info(creditors_complete_data[1])
                    st.write("**Telefone**")
                    st.info(creditors_complete_data[2])
                confirm_selection = st.checkbox(label="Confirmar seleção")

            if confirm_selection:

                with col2:

                    st.subheader(body=":computer: Entrada de Dados")

                    with st.expander(
                        label="Novos dados de {}".format(selected_creditor),
                        expanded=True
                    ):
                        new_name = st.text_input(
                            label="**Novo nome**",
                            max_chars=100,
                            help="""
                            Novo nome do credor.
                            """,
                            placeholder=selected_creditor
                        )
                        new_document = st.text_input(
                            label="**Novo documento**",
                            help="""
                            Novo CPF/CNPJ do credor,
                            sem barras, pontos e hifens.
                            """,
                            placeholder=creditors_complete_data[1]
                        )
                        new_phone = st.text_input(
                            label="**Novo telefone**",
                            max_chars=11,
                            help="Novo telefone do credor, apenas números.",
                            placeholder=creditors_complete_data[2]
                        )

                    confirm_changes_button = st.button(
                        label=":floppy_disk: Confirmar mudanças")

                    if confirm_changes_button:
                        if new_name == "":
                            new_name = creditors_complete_data[1]
                        if new_document == "":
                            new_document = creditors_complete_data[2]
                        if new_phone == "":
                            new_phone = creditors_complete_data[3]

                        with col3:
                            with st.spinner(text="Aguarde..."):
                                sleep(1.25)
                            st.subheader(
                                body=":white_check_mark: Validação de Dados"
                            )
                            with st.expander(
                                label="Validação",
                                expanded=True
                            ):
                                is_data_passed_valid = (
                                    self.is_creditor_new_values_valid(
                                        int(creditors_complete_data[0]),
                                        new_name,
                                        new_document,
                                        new_phone
                                    )
                                )

                            if is_data_passed_valid is True:

                                loans_ids = (
                                    QueryExecutor().complex_consult_query(
                                        query=get_loans_creditor_ids_query,
                                        params=(
                                            creditors_complete_data[1],
                                            creditors_complete_data[2]
                                        )
                                    )
                                )
                                loans_ids = (
                                    QueryExecutor().treat_complex_result(
                                        loans_ids,
                                        TO_REMOVE_LIST
                                    )
                                )

                                if len(loans_ids) >= 1:
                                    ids = []
                                    for i in range(0, len(loans_ids)):
                                        ids.append(int(loans_ids[i]))
                                    ids = tuple(ids)

                                    QueryExecutor().update_unique_register(
                                        new_creditor_loans_data_query,
                                        (
                                            new_name,
                                            new_document,
                                            creditors_complete_data[1],
                                            creditors_complete_data[2],
                                            ids
                                        ),
                                        "Registros atualizados com sucesso!",
                                        "Erro ao atualizar registros:"
                                    )

                                QueryExecutor().update_unique_register(
                                    new_creditor_data_query,
                                    (
                                        new_name,
                                        new_document,
                                        new_phone,
                                        int(creditors_complete_data[0])
                                    ),
                                    "Credor atualizado com sucesso!",
                                    "Erro ao atualizar credor:"
                                )

                                log_values = (
                                    user_id,
                                    "Atualização",
                                    """
                                    O usuário atualizou o credor {}.
                                    """.format(
                                        creditors_complete_data[1]
                                    )
                                )

                                QueryExecutor().register_log_query(
                                    log_values,
                                )

    def new_creditor(self):
        """
        Realiza o cadastro de um novo credor.
        """

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(body=":computer: Entrada de Dados")

            with st.expander(label="Dados do credor", expanded=True):
                creditor_name = st.text_input(
                    label=":lower_left_ballpoint_pen: Nome",
                    max_chars=100,
                    help="Nome do credor."
                )
                creditor_document = st.text_input(
                    label=":lower_left_ballpoint_pen: Documento",
                    help="CPF/CNPJ do credor, sem pontos e barras."
                )
                creditor_phone = st.text_input(
                    label=":telephone_receiver: Telefone/Celular",
                    max_chars=11,
                    help="Número de telefone do credor."
                )
                confirm_creditor_data = st.checkbox(label="Confirmar dados")

            register_new_creditor = st.button(
                label=":floppy_disk: Cadastrar credor"
            )

            if confirm_creditor_data and register_new_creditor:
                with col2:
                    st.subheader(body=":white_check_mark: Validação de Dados")
                    with st.spinner(text="Aguarde..."):
                        sleep(1.25)
                    with st.expander(label="Aviso", expanded=True):

                        is_document_valid = (
                            Documents().validate_owner_document(
                                creditor_document
                            )
                        )

                        if (
                            is_document_valid is True
                        ) and (
                                creditor_name != ''
                        ) and (
                                creditor_phone != ''
                        ):
                            creditor_document = int(creditor_document)
                            st.success(body="Documento válido.")

                            if (
                                creditor_name != user_id
                            ) and (
                                    creditor_document != int(user_document)
                            ):

                                query_values = (
                                    creditor_name,
                                    creditor_document,
                                    creditor_phone
                                )

                                QueryExecutor().insert_query(
                                    insert_creditor_query,
                                    query_values,
                                    "Credor cadastrado com sucesso!",
                                    "Erro ao cadastrar credor:"
                                )

                                log_values = (
                                    user_id,
                                    "Cadastro",
                                    """
                                    O usuário cadastrou o credor {}.
                                    """.format(creditor_name)
                                )

                                QueryExecutor().register_log_query(
                                    log_values,
                                )

                            if (
                                creditor_name == user_id
                            ) or (
                                    creditor_document == int(user_document)
                            ):
                                if creditor_name == user_id:
                                    st.error(
                                        body="""
                                        Este credor já foi cadastrado"""
                                    )
                                if creditor_document == int(user_document):
                                    st.error(
                                        body="""
                                        Este documento já está sendo usado."""
                                    )

                        elif is_document_valid is False:
                            st.error(
                                body="""
                                O documento {} informado não é válido.
                                """.format(creditor_document)
                            )

    def main_menu(self, menu_position):
        """
        Menu principal.

        Parameters
        ----------
        menu_position : Any
            Define a posição de exibição do menu.
        """

        menu_options = {
            "Cadastrar credor": self.new_creditor,
            "Atualizar credor": self.update_creditor
        }

        with menu_position:
            selected_option = st.selectbox(
                label="Menu de Credores",
                options=menu_options.keys()
            )
            selected_function = menu_options[selected_option]

        st.divider()

        selected_function()
