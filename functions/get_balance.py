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
    def __init__(self):
        query_executor = QueryExecutor()

        str_total_expenses = query_executor.simple_consult_query(total_expense_query)
        str_total_expenses = query_executor.treat_simple_result(str_total_expenses, to_remove_list)

        if str_total_expenses == 'None':
            total_expenses = 0.00
        else:
            total_expenses = float(str_total_expenses)

        str_total_revenues = query_executor.simple_consult_query(total_revenue_query)
        str_total_revenues = query_executor.treat_simple_result(str_total_revenues, to_remove_list)

        if str_total_revenues == 'None':
            total_revenues = 0.00
            
        else:
            total_revenues = float(str_total_revenues)

        def get_balance():
            if total_revenues is not None and total_expenses is not None:
                balance = total_revenues - total_expenses
                return balance
            else:
                return None

        def get_accounts_balance():
            accounts_expenses = query_executor.complex_consult_query(accounts_expenses_query)
            accounts_expenses = query_executor.treat_numerous_simple_result(accounts_expenses, to_remove_list)

            accounts_revenues = query_executor.complex_consult_query(accounts_revenue_query)
            accounts_revenues = query_executor.treat_numerous_simple_result(accounts_revenues, to_remove_list)

            future_accounts_expenses = query_executor.complex_consult_query(future_accounts_expenses_query)
            future_accounts_expenses = query_executor.treat_numerous_simple_result(future_accounts_expenses, to_remove_list)

            future_accounts_revenues = query_executor.complex_consult_query(future_accounts_revenue_query)
            future_accounts_revenues = query_executor.treat_numerous_simple_result(future_accounts_revenues, to_remove_list)

            accounts = query_executor.complex_consult_query(accounts_query)
            accounts = query_executor.treat_numerous_simple_result(accounts, to_remove_list)

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

        def list_values():
            last_expenses = query_executor.complex_consult_query(last_expense_query)
            last_revenues = query_executor.complex_consult_query(last_revenue_query)
            max_revenues = query_executor.complex_consult_query(max_revenue_query)
            max_expenses = query_executor.complex_consult_query(max_expense_query)

            return last_revenues, last_expenses, max_revenues, max_expenses

        self.balance = get_balance
        self.accounts_balance = get_accounts_balance
        self.list_values = list_values
