from datetime import datetime
from dictionary.sql.others_queries import (
    accounts_type_query,
    expense_categories_query,
    revenue_categories_query,
    transfer_categories_query
)
from functions.query_executor import QueryExecutor
import os

operational_system = os.name

C0NFIG_FILE_PATH: str = ".streamlit/config.toml"
SESSION_STATE_PATH: str = "data/cache/session_state.py"

DARK_THEME = '''[theme]
primaryColor="#bd93f9"
backgroundColor="#282a36"
secondaryBackgroundColor="#44475a"
textColor="#f8f8f2"'''

LIGHT_THEME = """[theme]
primaryColor = "#61afef"
backgroundColor = "#fefefe"
secondaryBackgroundColor = "#e6e6e6"
textColor = "#3c4048"
"""

SERVER_CONFIG = """
[server]
headless = true
enableStaticServing = true"""

FONTS_DICTIONARY = {
    "sans serif": "/library/fonts/sans_serif/RobotoRegular.ttf",
    "serif": "/library/fonts/serif/CrimsonTextRegular.ttf",
    "monospace": "/library/fonts/monospace/CourierPrimeRegular.ttf"
}

DEFAULT_ACCOUNT_IMAGE = "default.png"

today = datetime.now()
today = today.date()
actual_year = today.year
actual_year = str(actual_year)
actual_month = today.month
next_month = actual_month + 1
first_month_day = datetime(today.year, today.month, 1)
first_month_day = first_month_day.date()
today = str(today)
first_month_day = str(first_month_day)


TO_REMOVE_LIST = [
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

SPECIAL_CARACTERS_DICTIONARY = {
    "í": "i",
    "ú": "u",
    "ô": "o",
}

EXPENSE_CATEGORIES = QueryExecutor().complex_consult_query(
    expense_categories_query,
    ()
)
EXPENSE_CATEGORIES = QueryExecutor().treat_simple_results(
    EXPENSE_CATEGORIES,
    TO_REMOVE_LIST
)

REVENUE_CATEGORIES = QueryExecutor().complex_consult_query(
    revenue_categories_query,
    ()
)
REVENUE_CATEGORIES = QueryExecutor().treat_simple_results(
    REVENUE_CATEGORIES,
    TO_REMOVE_LIST
)

TRANSFER_CATEGORIES = QueryExecutor().complex_consult_query(
    transfer_categories_query,
    params=()
)
TRANSFER_CATEGORIES = QueryExecutor().treat_simple_results(
    TRANSFER_CATEGORIES,
    TO_REMOVE_LIST
)

ACCOUNTS_TYPE = QueryExecutor().complex_consult_query(
    accounts_type_query,
    ()
)
ACCOUNTS_TYPE = QueryExecutor().treat_simple_results(
    ACCOUNTS_TYPE,
    TO_REMOVE_LIST
)

ABSOLUTE_APP_PATH = os.getcwd()

DECIMAL_VALUES = [
    ",0",
    ",1",
    ",2",
    ",3",
    ",4",
    ",5",
    ",6",
    ",7",
    ",8",
    ",9",
    "0,0"
]

TRANSFER_IMAGE = "{}/library/images/transfer.png".format(ABSOLUTE_APP_PATH)
SAVE_FOLDER = "{}/library/images/accounts/".format(ABSOLUTE_APP_PATH)
