from dictionary.app_vars import account_models
from dictionary.sql.account_queries import (
    unique_account_id_query,
    user_all_current_accounts_query,
    insert_account_query,
    update_account_query
)
from dictionary.sql.user_queries import user_login_query
from dictionary.sql.expenses_queries import insert_expense_query
from dictionary.sql.revenues_queries import insert_revenue_query
from dictionary.vars import (
    ACCOUNTS_TYPE,
    DECIMAL_VALUES,
    DEFAULT_ACCOUNT_IMAGE,
    SAVE_FOLDER,
    TO_REMOVE_LIST,
    today
)
from functions.get_actual_time import GetActualTime
from functions.login import Login
from functions.query_executor import QueryExecutor
from PIL import Image
from time import sleep
import os
import streamlit as st


user_id, user_document = Login().get_user_data()
actual_horary = GetActualTime().get_actual_time()


class UpdateAccounts:
    """
    Classe que representa o cadastro e atualização do usuário.
    """

    def get_new_account(self):
        """
        Coleta os dados e cadastra uma nova conta.
        """
        def validate_image(image: any, account_name: str):
            """
            Realiza a validação da imagem, retornando o caminho real
            e relativo do arquivo.

            Parameters
            ----------
            image : any
                A imagem obtida a partir do menu.
            account_name : str
                O nome da conta associada a imagem.

            Returns
            -------

            """

            user_login = QueryExecutor().simple_consult_query(
                user_login_query,
                (user_id, user_document)
            )
            user_login = QueryExecutor().treat_simple_result(
                user_login,
                TO_REMOVE_LIST
            )
            image_type = type(get_account_image).__name__
            save_folder = SAVE_FOLDER + f"{user_login}/"
            new_file_name = ""

            if image_type != "NoneType":

                image = Image.open(image)
                width, height = image.size

                if width == height and (width + height <= 200):
                    account_name = account_name.lower()
                    account_name = account_name.replace(
                        " ", "_"
                    )
                    library_file_name = f"{account_name}.png"
                    new_file_name = save_folder + library_file_name

                else:
                    st.error(
                        body="""
                        A imagem precisa ter as dimensões iguais,
                        com no máximo 100.
                        """
                    )

            elif image_type == "NoneType":
                file_destination = SAVE_FOLDER + DEFAULT_ACCOUNT_IMAGE
                library_file_name = DEFAULT_ACCOUNT_IMAGE
                image = Image.open(file_destination)
                new_file_name = DEFAULT_ACCOUNT_IMAGE

            save_path = os.path.join(SAVE_FOLDER, new_file_name)
            image.save(save_path)

            return save_path, library_file_name

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(body=":computer: Entrada de Dados")
            with st.expander(label="Dados cadastrais", expanded=True):
                account_name = st.selectbox(
                    label=":lower_left_ballpoint_pen: Nome da conta",
                    options=account_models.keys()
                )
                account_type = st.selectbox(
                    label=":card_index_dividers: Tipo da conta",
                    options=ACCOUNTS_TYPE
                )
                get_account_first_value = st.number_input(
                    label=":heavy_dollar_sign: Valor inicial",
                    step=0.01,
                    min_value=0.00,
                    help="Não é possível cadastrar sem um valor inicial."
                )
                get_account_image = st.file_uploader(
                    label=":camera: Imagem da conta",
                    type=['png', 'jpg'],
                    help="O envio da imagem não é obrigatório."
                )
                confirm_values_ckecbox = st.checkbox(label="Confirmar Dados")

            register_account = st.button(label=":floppy_disk: Registrar Conta")

            if confirm_values_ckecbox and register_account:

                with col2:
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)

                    st.subheader(body=":white_check_mark: Validação de Dados")
                    data_expander = st.expander(label="Dados", expanded=True)

                    with data_expander:
                        str_value = str(get_account_first_value)
                        str_value = str_value.replace(".", ",")
                        last_two_values = str_value[-2:]
                        if last_two_values in DECIMAL_VALUES:
                            str_value = str_value + "0"
                        st.info(body="Nome da conta: {}".format(account_name))
                        st.info(body="Tipo da conta: {}".format(account_type))
                        st.info(
                            body="""
                            Aporte inicial: :heavy_dollar_sign: {}
                            """.format(
                                str_value
                            )
                        )

                    save_path, library_file_name = validate_image(
                        get_account_image,
                        account_name
                    )

                    with data_expander:
                        st.success(
                            body="""
                            A imagem foi salva em: {}
                            """.format(save_path)
                        )

                    new_account_values = (
                        account_name,
                        account_models[account_name],
                        user_id,
                        user_document,
                        library_file_name
                    )
                    QueryExecutor().insert_query(
                        insert_account_query,
                        new_account_values,
                        "Conta cadastrada com sucesso!",
                        "Erro ao cadastrar conta:"
                    )

                    log_values = (
                        user_id,
                        "Cadastro",
                        "Cadastrou a conta {}.".format(account_name)
                    )
                    QueryExecutor().register_log_query(
                        log_values
                    )
                    account_id = QueryExecutor().simple_consult_query(
                        unique_account_id_query,
                        params=(account_name, user_id, user_document)
                    )
                    account_id = QueryExecutor().treat_simple_result(
                        account_id,
                        TO_REMOVE_LIST
                    )
                    account_id = int(account_id)

                    new_account_first_revenue_values = (
                        "Aporte Inicial",
                        get_account_first_value,
                        today,
                        actual_horary,
                        "Depósito",
                        account_id,
                        user_id,
                        user_document,
                        "S"
                    )

                    new_account_first_future_revenue_values = (
                        "Aporte Inicial",
                        0,
                        '2099-12-31',
                        actual_horary,
                        "Depósito",
                        account_id,
                        user_id,
                        user_document,
                        "N"
                    )

                    new_account_first_expense_values = (
                        "Valor Inicial",
                        0,
                        today,
                        actual_horary,
                        "Ajuste",
                        account_id,
                        user_id,
                        user_document,
                        "S")

                    new_account_first_future_expense_values = (
                        "Valor Inicial",
                        0,
                        '2099-12-31',
                        actual_horary,
                        "Ajuste",
                        account_id,
                        user_id,
                        user_document,
                        "N"
                    )
                    QueryExecutor().insert_query(
                        insert_revenue_query,
                        new_account_first_revenue_values,
                        "Aporte inicial registrado com sucesso!",
                        "Erro ao registrar aporte inicial:"
                    )
                    QueryExecutor().insert_query(
                        insert_revenue_query,
                        new_account_first_future_revenue_values,
                        "Aporte inicial registrado com sucesso!",
                        "Erro ao registrar aporte inicial:"
                    )
                    QueryExecutor().insert_query(
                        insert_expense_query,
                        new_account_first_expense_values,
                        "Valor inicial registrado com sucesso!",
                        "Erro ao registrar valor inicial:"
                    )
                    QueryExecutor().insert_query(
                        insert_expense_query,
                        new_account_first_future_expense_values,
                        "Valor inicial registrado com sucesso!",
                        "Erro ao registrar valor inicial:"
                    )

            elif confirm_values_ckecbox is False and register_account:

                with col3:
                    cm_cl1, cm_cl2 = st.columns(2)

                with cm_cl2:
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)
                    st.warning(
                        body="Revise e confirme os dados antes de prosseguir."
                    )

    def update_account(self):
        """
        Realiza a atualização dos dados da conta do usuário.
        """

        col1, col2, col3 = st.columns(3)
        user_accounts = QueryExecutor().complex_consult_query(
            query=user_all_current_accounts_query,
            params=(user_id, user_document)
        )
        user_accounts = QueryExecutor().treat_simple_results(
            user_accounts,
            TO_REMOVE_LIST
        )
        options = {
            "Não": "N",
            "Sim": "S"
        }
        with col1:
            st.subheader(body=":computer: Entrada de Dados")
            with st.expander(label="Dados", expanded=True):
                account_selected = st.selectbox(
                    label="Conta",
                    options=user_accounts,
                    help="Selecione uma conta para atualizar."
                )
                account_type = st.selectbox(
                    label="Tipo de conta",
                    options=[
                        "Conta Corrente",
                        "Conta Móvel",
                        "Fundo de Garantia",
                        "Vale Alimentação"
                    ]
                )
                inactive_selected_account = st.selectbox(
                    label="Inativar Conta",
                    options=options.keys()
                )
                confirm_account_checkbox = st.checkbox(label="Confirmar dados")

            update_button = st.button(label=":floppy_disk: Atualizar conta")

            if update_button and confirm_account_checkbox:
                inactive_selected_account = options[
                    inactive_selected_account
                ]
                QueryExecutor().update_unique_register(
                    update_account_query,
                    (
                        inactive_selected_account,
                        account_type,
                        account_selected,
                        user_id,
                        user_document
                    ),
                    "Conta atualizada com sucesso!",
                    "Erro ao atualizar conta:"
                )
                log_values = (
                    user_id,
                    "Atualização",
                    "Atualizou a conta {}.".format(account_selected)
                )
                QueryExecutor().register_log_query(
                    log_values
                )

    def main_menu(self, menu_position):
        """
        Exibe o menu.

        Parameters
        ----------
        menu_position : Any
            Define a posição de exibição do menu.
        """
        menu_options = {
            "Cadastrar Conta": self.get_new_account,
            "Atualizar Conta": self.update_account
        }

        with menu_position:
            account_selected_option = st.selectbox(
                label="Menu de Contas",
                options=menu_options.keys()
            )
            selected_function = menu_options[account_selected_option]

        st.divider()

        selected_function()
