from datetime import datetime
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
actual_horary = datetime.now().strftime("%H:%M:%S")
actual_year = today.year
actual_year = str(actual_year)
actual_month = today.month
next_month = actual_month + 1
first_month_day = datetime(today.year, today.month, 1)
first_month_day = first_month_day.date()
today = str(today)
first_month_day = str(first_month_day)

MONTHS_DICTIONARY = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

string_actual_month = MONTHS_DICTIONARY[actual_month]

SPECIAL_CARACTERS_DICTIONARY = {
    "í": "i",
    "ú": "u",
    "ô": "o",
}

EXPENSE_CATEGORIES: list = [
    "Casa",
    "Eletroeletrônicos",
    "Entretenimento",
    "Lazer",
    "Presente",
    "Restaurante",
    "Saúde",
    "Serviços",
    "Supermercado",
    "Transporte",
    "Vestuário"
]

REVENUE_CATEGORIES: list = [
    "Ajuste",
    "Depósito",
    "Prêmio",
    "Salário",
    "Vale",
    "Rendimentos"
]

TRANSFER_CATEGORIES: list = ["DOC", "TED", "Pix"]

ACCOUNTS_TYPE = [
    "Conta Corrente",
    "Conta Salário",
    "Fundo de Garantia",
    "Vale Alimentação"
]

TO_REMOVE_LIST: list = [
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
