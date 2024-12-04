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
        """
        Classe responsável pelo cálculo total e detalhado das contas.

        Attributes
        ----------
        calculate_total_revenues()
            Realiza o cálculo do valor total das receitas e despesas.
        balance()
            Realiza o cálculo do saldo total.
        accounts_balance()
            Realiza o cálculo do saldo das contas.
        list_values()
            Realiza a consulta e retorno dos maiores e mais recentes registros de receitas e despesas.
        """
        
        def calculate_total_revenues(self):
            """
            Realiza o cálculo do valor total das receitas e despesas.

            Returns
            -------
            total_revenues: float
                O valor total das receitas.
            total_expenses: float
                O valor total das despesas.
            """

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
                
            return total_revenues, total_expenses

        def balance(self):
            """
            Realiza o cálculo do saldo total.
            
            Returns
            -------
            balance: float
                Retorna o valor do saldo total.
            """

            total_revenues, total_expenses = self.calculate_total_revenues()
            if total_revenues is not None and total_expenses is not None:
                balance = total_revenues - total_expenses
                return balance
            else:
                return None

        def accounts_balance(self):
            """
            Realiza o cálculo do saldo das contas.

            Returns
            -------
            accounts: list
                Lista das contas.
            balance_list: list
                Lista com o saldo das contas.
            future_balance_list: list
                Lista com o saldo futuro das contas.
            """
            query_executor = QueryExecutor()

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

        def list_values(self):
            """
            Realiza a consulta e retorno dos maiores e mais recentes registros de receitas e despesas.

            Returns
            -------
            last_expenses: list
                Lista com as últimas despesas.
            last_revenues: list
                Lista com as últimas receitas.
            max_expenses: list
                Lista com as maiores despesas.
            max_revenues: list
                Lista com as maiores receitas.
            """
            query_executor = QueryExecutor()

            last_expenses = query_executor.complex_consult_query(last_expense_query)
            last_revenues = query_executor.complex_consult_query(last_revenue_query)
            max_revenues = query_executor.complex_consult_query(max_revenue_query)
            max_expenses = query_executor.complex_consult_query(max_expense_query)

            return last_revenues, last_expenses, max_revenues, max_expenses
