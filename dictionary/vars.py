from datetime import datetime
from PIL import Image
import os


operational_system = os.name

config_file_path: str = ".streamlit/config.toml"
session_state_path: str = "data/cache/session_state.py"
absolute_app_path = os.getcwd()


dark_theme = '''[theme]
primaryColor="#bd93f9"
backgroundColor="#282a36"
secondaryBackgroundColor="#44475a"
textColor="#f8f8f2"'''

""" 

dark_theme = '''[theme]
primaryColor = "#61afef"
backgroundColor = "#282c34"
secondaryBackgroundColor = "#3c4048"
textColor = "#abb2bf"'''

"""


"""
light_theme = '''[theme]
primaryColor = "#bd93f9"
backgroundColor = "#f8f8f2"
secondaryBackgroundColor = "#e0e0e0"
textColor = "#282a36"'''
"""

light_theme = """[theme]
primaryColor = "#61afef"
backgroundColor = "#fefefe"
secondaryBackgroundColor = "#e6e6e6"
textColor = "#3c4048"
"""

server_config = """
[server]
headless = true
enableStaticServing = true"""

fonts_dictionary = {
    "sans serif": "/library/fonts/sans_serif/RobotoRegular.ttf",
    "serif": "/library/fonts/serif/CrimsonTextRegular.ttf",
    "monospace": "/library/fonts/monospace/CourierPrimeRegular.ttf"
}

main_image = Image.open("{}/library/favicon.png".format(absolute_app_path))
transfer_image: str = Image.open("{}/library/images/transfer.png".format(absolute_app_path))

transfer_image_path = "{}/library/images/transfer.png".format(absolute_app_path)

default_account_image = "default.png"

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

months_dictionary = {
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

string_actual_month = months_dictionary[actual_month]

special_caracters_dictionary = {
    "í": "i",
    "ú": "u",
    "ô": "o",
}

expense_categories: list = ["Selecione uma opção","Casa","Lazer","Eletroeletrônicos","Serviços","Entretenimento","Presente","Restaurante","Saúde","Supermercado","Transporte","Vestuário"]
revenue_categories: list = ["Selecione uma opção","Ajuste","Depósito","Prêmio","Salário","Vale","Rendimentos"]
transfer_categories: list = ["Selecione uma opção", "DOC", "TED", "Pix"]
accounts_type = ["Conta Corrente","Conta Salário","Fundo de Garantia","Vale Alimentação"]

to_remove_list: list = ["'", ")", "(", ",", "Decimal", '"', "[", "]", "datetime.date"]

decimal_values = [",0", ",1", ",2", ",3", ",4", ",5", ",6", ",7", ",8", ",9", "0,0"]

SAVE_FOLDER = absolute_app_path + "/library/images/accounts/"