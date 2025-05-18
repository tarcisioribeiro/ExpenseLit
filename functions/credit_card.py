from dictionary.sql.credit_card_expenses_queries import (
    credit_card_id_expenses_query,
    credit_card_limit_query,
    credit_card_month_expenses_query,
    credit_card_month_expenses_complete_query,
    credit_card_next_expenses_query,
    credit_card_not_payed_expenses_query,
    month_query,
    card_key_query
)
from dictionary.vars import (
    actual_year,
    TO_REMOVE_LIST
)
from dictionary.app_vars import string_actual_month
from functions.login import Login
from functions.query_executor import QueryExecutor


user_id, user_document = Login().get_user_data()


class Credit_Card:
    """
    Classe com métodos que representam as operações de um cartão de crédito.
    """

    def get_card_month(self, selected_card: str):
        """
        Obtém o mês de fatura do cartão no qual a data atual se encontra.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        actual_month : str
            O nome do mês de fatura do cartão no qual a data atual se encontra.
        """

        actual_month = QueryExecutor().simple_consult_query(
            month_query,
            (selected_card, user_document, user_id)
        )
        actual_month = QueryExecutor().treat_simple_result(
            actual_month,
            TO_REMOVE_LIST
        )

        return actual_month

    def not_payed_expenses(self, selected_card: str):
        """
        Consulta as despesas de cartão que ainda não foram pagas.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        """

        actual_month = self.get_card_month(selected_card)

        not_payed_expenses = QueryExecutor().simple_consult_query(
            credit_card_not_payed_expenses_query,
            (
                selected_card,
                actual_year,
                actual_month,
                user_id,
                user_document
            )
        )

        not_payed_expenses = QueryExecutor().treat_simple_result(
            not_payed_expenses,
            TO_REMOVE_LIST
        )

        return float(not_payed_expenses)

    def month_expenses(
        self,
        selected_card: str,
        year: int,
        selected_month: str
    ):
        """
        Consulta as despesas de cartão no mês e cartão selecionados.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        year : int
            O ano passado como parâmetro.
        selected_month : str
            O mês selecionado pelo usuário.

        Returns
        -------
        float
            O valor total das despesas do cartão no mês.
        """

        month_expenses = QueryExecutor().simple_consult_query(
            credit_card_month_expenses_query,
            (
                selected_card,
                user_id,
                user_document,
                year,
                selected_month,
                user_id,
                user_document
            )
        )

        month_expenses = QueryExecutor().treat_simple_result(
            month_expenses,
            TO_REMOVE_LIST
        )

        return float(month_expenses)

    def get_complete_card_month_expenses(
            self,
            selected_card: str,
            year: int,
            selected_month: str
    ):
        """
        Consulta os detalhes das despesas de cartão no mês selecionado.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        year : int
            O ano passado como parâmetro.
        selected_month : str
            O mês selecionado pelo usuário.

        Returns
        -------
        description_list : list
            A lista com a descrição das despesas.
        value_list : list
            A lista com o valor das despesas.
        date_list : list
            A lista com a data das despesas.
        category_list : list
            A lista com a categoria das despesas.
        installment_list : list
            A lista com a parcela das despesas.
        """

        (
            descrption_list,
            value_list,
            date_list,
            category_list,
            installment_list,
        ) = QueryExecutor().complex_compund_query(
                credit_card_month_expenses_complete_query,
                5,
                (
                    selected_card,
                    year,
                    selected_month,
                    user_id,
                    user_document
                )
            )

        return (
            descrption_list,
            value_list,
            date_list,
            category_list,
            installment_list,
        )

    def get_card_id_month_expenses(
        self,
        selected_card: str,
        year: int,
        selected_month: str
    ):
        """
        Consulta o id das despesas de cartão no mês selecionado.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.
        year : int
            O ano passado como parâmetro.
        selected_month : str
            O mês da fatura selecionada.

        Returns
        -------
        converted_id_list : list
            A lista com os ID's de despesas de cartão no mês.
        """

        id_list = QueryExecutor().complex_consult_query(
            credit_card_id_expenses_query,
            (
                selected_card,
                user_id,
                user_document,
                year,
                selected_month,
                user_id,
                user_document
            )
        )

        id_list = QueryExecutor().treat_complex_result(
            id_list,
            TO_REMOVE_LIST
        )

        return id_list

    def future_expenses(self, selected_card: str):
        """
        Consulta o valor das próximas despesas do cartão.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        float
            O valor total das despesas futuras.
        """

        actual_month = self.get_card_month(selected_card)

        next_expenses = QueryExecutor().complex_consult_query(
            credit_card_next_expenses_query,
            (
                selected_card,
                actual_year,
                actual_month,
                user_id,
                user_document
            )
        )
        next_expenses = QueryExecutor().treat_simple_result(
            next_expenses,
            TO_REMOVE_LIST
        )

        return float(next_expenses)

    def card_limit(self, selected_card: str):
        """
        Consulta o limite do cartão.

        Parameters
        ----------
        selected_card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        float
            O limite de crédito do cartão.
        """

        card_limit = QueryExecutor().simple_consult_query(
            credit_card_limit_query,
            (
                selected_card,
                user_id,
                user_document
            )
        )

        card_limit = QueryExecutor().treat_simple_result(
            card_limit,
            TO_REMOVE_LIST
        )

        return float(card_limit)

    def get_credit_card_key(self, card: str):
        """
        Consulta os dados do cartão selecionado.

        Parameters
        ----------
        card : str
            O cartão selecionado pelo usuário.

        Returns
        -------
        card_number : str
            O número do cartão.
        card_owner : str
            O nome do proprietário do cartão.
        card_owner_document : int
            O documento do proprietário do cartão.
        card_security_code : str
            O código de segurança do cartão.
        """

        (
            card_id,
            card_number,
            card_owner,
            card_owner_document,
            card_security_code,
        ) = QueryExecutor().complex_compund_query(
            card_key_query,
            5,
            (
                card,
                user_id,
                user_document
            )
        )

        card_id = int(card_id[0])
        card_number = card_number[0]
        card_owner = int(card_owner[0])
        card_owner_document = str(card_owner_document)
        card_owner_document = card_owner_document.replace("[", "")
        card_owner_document = card_owner_document.replace("]", "")
        card_owner_document = card_owner_document.replace("'", "")
        card_security_code = str(card_security_code)
        card_security_code = card_security_code.replace("[", "")
        card_security_code = card_security_code.replace("]", "")
        card_security_code = card_security_code.replace("'", "")

        return (
            card_id,
            card_number,
            card_owner,
            card_owner_document,
            card_security_code,
        )

    def card_remaining_limit(self, selected_card: str):
        """
        Calcula o limite restante do cartão de crédito.

        Parameters
        ----------
        selected_card : str
            O cartão de crédito selecionado.

        Returns
        -------
        remaining_limit : float
            0 valor do limite restante do cartão.
        """

        card_total_limit = self.card_limit(selected_card)
        not_payed_expenses = self.not_payed_expenses(selected_card)
        month_card_expenses = self.month_expenses(
            selected_card,
            actual_year,
            string_actual_month
        )
        future_card_expenses = self.future_expenses(selected_card)

        total_card_expenses = month_card_expenses + \
            future_card_expenses + not_payed_expenses

        remaining_limit = card_total_limit - total_card_expenses

        return remaining_limit
