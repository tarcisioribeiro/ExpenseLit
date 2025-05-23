from dictionary.sql.account_queries import (
    current_accounts_query
)
from dictionary.sql.expenses_queries import (
    total_expense_query,
    accounts_expenses_query,
    future_accounts_expenses_query,
    max_expense_query,
    last_expense_query
)
from dictionary.sql.revenues_queries import (
    total_revenue_query,
    last_revenue_query,
    max_revenue_query,
    future_accounts_revenue_query,
    accounts_revenue_query
)
from dictionary.vars import TO_REMOVE_LIST, today
from functions.login import Login
from functions.query_executor import QueryExecutor


user_id, user_document = Login().get_user_data()


class GetBalance:
    """
    Classe responsável pela consulta dos valores do balannço de contas.
    """

    def get_values(self):
        """
        Faz a consulta dos valores de despesas e receitas.

        Returns
        -------
        total_revenues : float
            O valor total das receitas.
        total_expenses : float
            O valor total das despesas.
        """

        str_total_expenses = QueryExecutor().simple_consult_query(
            query=total_expense_query,
            params=(user_id, user_document)
        )
        str_total_expenses = QueryExecutor().treat_simple_result(
            str_total_expenses,
            TO_REMOVE_LIST
        )

        if str_total_expenses == 'None':
            total_expenses = 0.00
        else:
            total_expenses = float(str_total_expenses)

        str_total_revenues = QueryExecutor().simple_consult_query(
            query=total_revenue_query,
            params=(user_id, user_document)
        )
        str_total_revenues = QueryExecutor().treat_simple_result(
            str_total_revenues,
            TO_REMOVE_LIST
        )

        if str_total_revenues == 'None':
            total_revenues = 0.00

        else:
            total_revenues = float(str_total_revenues)

        return total_revenues, total_expenses

    def balance(self):
        """
        Calcula o valor do balanço.

        Returns
        -------
        balance : float
            O valor do balanço.
        """
        total_revenues, total_expenses = self.get_values()

        if total_revenues is not None and total_expenses is not None:
            balance = round((total_revenues - total_expenses), 2)
            return balance
        else:
            return None

    def accounts_balance(self):
        """
        Realiza o cálculo do balanço das contas.

        Returns
        -------
        accounts : list
            A lista com o nome das contas.
        balance_list : list
            A lista com o balanço das contas.
        future_balance_list : list
            A lista com o balanço futuro das contas.
        """

        accounts_expenses = QueryExecutor().complex_consult_query(
            query=accounts_expenses_query,
            params=(
                today,
                user_id,
                user_document
            )
        )
        # st.info(accounts_expenses)
        accounts_expenses = QueryExecutor().treat_simple_results(
            accounts_expenses,
            TO_REMOVE_LIST
        )

        accounts_revenues = QueryExecutor().complex_consult_query(
            query=accounts_revenue_query,
            params=(today, user_id, user_document)
        )
        accounts_revenues = QueryExecutor().treat_simple_results(
            accounts_revenues,
            TO_REMOVE_LIST
        )

        future_accounts_expenses = QueryExecutor().complex_consult_query(
            query=future_accounts_expenses_query,
            params=(today, user_id, user_document)
        )
        future_accounts_expenses = (
            QueryExecutor().treat_simple_results(
                future_accounts_expenses,
                TO_REMOVE_LIST
            )
        )

        future_accounts_revenues = QueryExecutor().complex_consult_query(
            query=future_accounts_revenue_query,
            params=(user_id, user_document)
        )
        future_accounts_revenues = (
            QueryExecutor().treat_simple_results(
                future_accounts_revenues,
                TO_REMOVE_LIST
            )
        )

        accounts = QueryExecutor().complex_consult_query(
            query=current_accounts_query,
            params=(user_id, user_document)
        )
        accounts = QueryExecutor().treat_simple_results(
            accounts,
            TO_REMOVE_LIST
        )

        balance_list = []
        future_balance_list = []

        if len(accounts_revenues) == len(accounts_expenses):
            for i in range(0, len(accounts_revenues)):
                revenue = float(accounts_revenues[i])
                expense = float(accounts_expenses[i])
                balance_list.append(revenue - expense)

        if len(future_accounts_expenses) == len(future_accounts_revenues):
            for i in range(0, len(future_accounts_revenues)):
                future_revenue = float(future_accounts_revenues[i])
                future_expense = float(future_accounts_expenses[i])
                future_balance_list.append(
                    (future_revenue - future_expense) + balance_list[i])

        return accounts, balance_list, future_balance_list

    def list_values(self):
        """
        Faz a consultas das maiores e últimas despesas e receitas.

        Returns
        -------
        last_revenues : list
            Lista com as últimas receitas.
        last_expenses : list
            Lista com as últimas despesas.
        max_revenues : list
            Lista com as maiores receitas.
        max_expenses : list
            Lista com as maiores despesas.
        """

        last_expenses = QueryExecutor().complex_consult_query(
            query=last_expense_query,
            params=(user_id, user_document)
        )
        last_revenues = QueryExecutor().complex_consult_query(
            query=last_revenue_query,
            params=(today, user_id, user_document)
        )
        max_revenues = QueryExecutor().complex_consult_query(
            query=max_revenue_query,
            params=(today, user_id, user_document)
        )
        max_expenses = QueryExecutor().complex_consult_query(
            query=max_expense_query,
            params=(user_id, user_document)
        )

        return last_revenues, last_expenses, max_revenues, max_expenses
