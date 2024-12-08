from functions.query_executor import QueryExecutor


to_remove_list: list = ["'", ")", "(", ",", "Decimal", '"', "[", "]", "datetime.date"]
query_executor = QueryExecutor()

months_query = '''SELECT nome_mes FROM meses;'''
account_models_query = '''SELECT nome_instituicao FROM modelos_conta;'''
years_query = '''SELECT ano FROM anos;'''

months = query_executor.complex_consult_query(months_query)
months = query_executor.treat_numerous_simple_result(months, to_remove_list)

account_models = query_executor.complex_consult_query(account_models_query)
account_models = query_executor.treat_numerous_simple_result(account_models, to_remove_list)

years = query_executor.complex_consult_query(years_query)
years = query_executor.treat_numerous_simple_result(years, to_remove_list)