from functions.query_executor import QueryExecutor

to_remove_list: list = [
    "'",
    ")",
    "(",
    ",",
    "Decimal",
    '"',
    "[",
    "]",
    "datetime.date"
]

months_query = '''SELECT nome_mes FROM meses;'''
account_models_query = '''SELECT nome_instituicao FROM modelos_conta;'''
years_query = '''SELECT ano FROM anos;'''

months = QueryExecutor().complex_consult_brute_query(months_query)
months = QueryExecutor().treat_numerous_simple_result(months, to_remove_list)

account_models = QueryExecutor().complex_consult_brute_query(
    account_models_query
)
account_models = QueryExecutor().treat_numerous_simple_result(
    account_models,
    to_remove_list
)

years = QueryExecutor().complex_consult_brute_query(years_query)
years = QueryExecutor().treat_numerous_simple_result(years, to_remove_list)
