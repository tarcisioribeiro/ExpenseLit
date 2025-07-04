from dictionary.sql.others_queries import (
    account_models_query,
    get_actual_month_query,
    months_query,
    years_query
)
from dictionary.vars import actual_month, TO_REMOVE_LIST
from functions.query_executor import QueryExecutor


months = QueryExecutor().complex_consult_query(
    months_query,
    ()
)
months = QueryExecutor().treat_simple_results(months, TO_REMOVE_LIST)  # type: ignore

account_models = QueryExecutor().complex_compund_query(
    account_models_query,
    2,
    ()
)

account_models = QueryExecutor().treat_compund_result(
    account_models,  # type: ignore
    TO_REMOVE_LIST
)

values = account_models[0]
index = account_models[1]

account_models = dict(zip(index, values))

years = QueryExecutor().complex_consult_query(
    years_query,
    ()
)

years = QueryExecutor().treat_simple_results(years, TO_REMOVE_LIST)  # type: ignore

string_actual_month = QueryExecutor().simple_consult_query(
    get_actual_month_query,
    (actual_month,)
)
string_actual_month = QueryExecutor().treat_simple_result(
    string_actual_month,  # type: ignore
    TO_REMOVE_LIST
)
