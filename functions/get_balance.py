from dictionary.sql import (
    total_expense_query,
    total_revenue_query,
    last_expense_query,
    last_revenue_query,
    max_expense_query,
    max_revenue_query,
    future_accounts_expenses_query,
    future_accounts_revenue_query,
    accounts_revenue_query,
    accounts_expenses_query,
    accounts_query,
)
from dictionary.vars import to_remove_list, today
from functions.query_executor import QueryExecutor
from functions.login import Login


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

        user_name, user_document = Login().get_user_data(return_option="user_doc_name")

        str_total_expenses = QueryExecutor().simple_consult_query(query=total_expense_query, params=(user_name, user_document))
        str_total_expenses = QueryExecutor().treat_simple_result(str_total_expenses, to_remove_list)

        if str_total_expenses == 'None':
            total_expenses = 0.00
        else:
            total_expenses = float(str_total_expenses)

        str_total_revenues = QueryExecutor().simple_consult_query(query=total_revenue_query, params=(user_name, user_document))
        str_total_revenues = QueryExecutor().treat_simple_result(str_total_revenues, to_remove_list)

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
        user_name, user_document = Login().get_user_data(return_option="user_doc_name")

        accounts_expenses = QueryExecutor().complex_consult_query(query=accounts_expenses_query, params=(today, user_name, user_document))
        accounts_expenses = QueryExecutor().treat_numerous_simple_result(accounts_expenses, to_remove_list)

        accounts_revenues = QueryExecutor().complex_consult_query(query=accounts_revenue_query, params=(today, user_name, user_document))
        accounts_revenues = QueryExecutor().treat_numerous_simple_result(accounts_revenues, to_remove_list)

        future_accounts_expenses = QueryExecutor().complex_consult_query(query=future_accounts_expenses_query, params=(today, user_name, user_document))
        future_accounts_expenses = QueryExecutor().treat_numerous_simple_result(future_accounts_expenses, to_remove_list)

        future_accounts_revenues = QueryExecutor().complex_consult_query(query=future_accounts_revenue_query, params=(user_name, user_document))
        future_accounts_revenues = QueryExecutor().treat_numerous_simple_result(future_accounts_revenues, to_remove_list)

        accounts = QueryExecutor().complex_consult_query(query=accounts_query, params=(user_name, user_document))
        accounts = QueryExecutor().treat_numerous_simple_result(accounts, to_remove_list)

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

        user_name, user_document = Login().get_user_data(return_option="user_doc_name")
        last_expenses = QueryExecutor().complex_consult_query(query=last_expense_query, params=(user_name, user_document))
        last_revenues = QueryExecutor().complex_consult_query(query=last_revenue_query, params=(today, user_name, user_document))
        max_revenues = QueryExecutor().complex_consult_query(query=max_revenue_query, params=(today, user_name, user_document))
        max_expenses = QueryExecutor().complex_consult_query(query=max_expense_query, params=(user_name, user_document))

        return last_revenues, last_expenses, max_revenues, max_expenses
