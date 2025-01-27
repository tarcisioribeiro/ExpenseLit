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
from dictionary.vars import to_remove_list
from functions.query_executor import QueryExecutor


class GetBalance:

    def get_values(self):
        str_total_expenses = QueryExecutor().simple_consult_query(total_expense_query)
        str_total_expenses = QueryExecutor().treat_simple_result(
            str_total_expenses, to_remove_list)

        if str_total_expenses == 'None':
            total_expenses = 0.00
        else:
            total_expenses = float(str_total_expenses)

        str_total_revenues = QueryExecutor().simple_consult_query(
            total_revenue_query)
        str_total_revenues = QueryExecutor().treat_simple_result(
            str_total_revenues, to_remove_list)

        if str_total_revenues == 'None':
            total_revenues = 0.00

        else:
            total_revenues = float(str_total_revenues)

        return total_revenues, total_expenses

    def get_balance(self):
        total_revenues, total_expenses = self.get_values()

        if total_revenues is not None and total_expenses is not None:
            balance = round((total_revenues - total_expenses), 2)
            return balance
        else:
            return None

    def get_accounts_balance(self):
        accounts_expenses = QueryExecutor().complex_consult_query(
            accounts_expenses_query)
        accounts_expenses = QueryExecutor().treat_numerous_simple_result(
            accounts_expenses, to_remove_list)

        accounts_revenues = QueryExecutor().complex_consult_query(
            accounts_revenue_query)
        accounts_revenues = QueryExecutor().treat_numerous_simple_result(
            accounts_revenues, to_remove_list)

        future_accounts_expenses = QueryExecutor().complex_consult_query(
            future_accounts_expenses_query)
        future_accounts_expenses = QueryExecutor().treat_numerous_simple_result(
            future_accounts_expenses, to_remove_list)

        future_accounts_revenues = QueryExecutor().complex_consult_query(
            future_accounts_revenue_query)
        future_accounts_revenues = QueryExecutor().treat_numerous_simple_result(
            future_accounts_revenues, to_remove_list)

        accounts = QueryExecutor().complex_consult_query(accounts_query)
        accounts = QueryExecutor().treat_numerous_simple_result(
            accounts, to_remove_list)

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
        last_expenses = QueryExecutor().complex_consult_query(last_expense_query)
        last_revenues = QueryExecutor().complex_consult_query(last_revenue_query)
        max_revenues = QueryExecutor().complex_consult_query(max_revenue_query)
        max_expenses = QueryExecutor().complex_consult_query(max_expense_query)

        return last_revenues, last_expenses, max_revenues, max_expenses
