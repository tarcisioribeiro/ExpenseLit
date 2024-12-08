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

light_theme = '''[theme]
primaryColor = "#bd93f9"
backgroundColor = "#f8f8f2"
secondaryBackgroundColor = "#e0e0e0"
textColor = "#282a36"'''

server_config = """
[server]
headless = true
enableStaticServing = true"""

main_image = Image.open("{}/library/favicon.png".format(absolute_app_path))

ben_visa_vale_image: str = Image.open("{}/library/images/ben_visa_vale.png".format(absolute_app_path))
caixa_image: str = Image.open("{}/library/images/caixa.png".format(absolute_app_path))
wallet_image: str = Image.open("{}/library/images/wallet.png".format(absolute_app_path))
mercado_pago_image: str = Image.open("{}/library/images/mercado_pago.png".format(absolute_app_path))
nubank_image: str = Image.open("{}/library/images/nubank.png".format(absolute_app_path))
picpay_image: str = Image.open("{}/library/images/picpay.png".format(absolute_app_path))
sicoob_image: str = Image.open("{}/library/images/sicoob.png".format(absolute_app_path))
transfer_image: str = Image.open("{}/library/images/transfer.png".format(absolute_app_path))

accounts_images: list = [ben_visa_vale_image,caixa_image,wallet_image,mercado_pago_image,nubank_image,picpay_image,sicoob_image]

ben_visa_vale_image_path = ("{}/library/images/ben_visa_vale.png".format(absolute_app_path))
caixa_image_path = "{}/library/images/caixa.png".format(absolute_app_path)
wallet_image_path = "{}/library/images/wallet.png".format(absolute_app_path)
mercado_pago_image_path = ("{}/library/images/mercado_pago.png".format(absolute_app_path))
nubank_image_path = "{}/library/images/nubank.png".format(absolute_app_path)
picpay_image_path = "{}/library/images/picpay.png".format(absolute_app_path)
sicoob_image_path = "{}/library/images/sicoob.png".format(absolute_app_path)
transfer_image_path = "{}/library/images/transfer.png".format(absolute_app_path)

accounts_images_paths: list = [ben_visa_vale_image_path,wallet_image_path,caixa_image_path,mercado_pago_image_path,nubank_image_path,picpay_image_path,sicoob_image_path]

static_ben_visa_vale_image: str = "app/static/ben_visa_vale.png"
static_caixa_image: str = "app/static/caixa.png"
static_wallet_image: str = "app/static/wallet.png"
static_mercado_pago_image: str = "app/static/mercado_pago.png"
static_nubank_image: str = "app/static/nubank.png"
static_picpay_image: str = "app/static/picpay.png"
static_sicoob_image: str = "app/static/sicoob.png"
static_transfer_image: str = "app/static/transfer.png"

static_accounts_images: list = [static_ben_visa_vale_image,static_caixa_image,static_wallet_image,static_mercado_pago_image,static_nubank_image,static_picpay_image,static_sicoob_image]

months: list = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
years: list = [2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033]

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

string_actual_month = ""

if actual_month == 1:
    string_actual_month = "Janeiro"
elif actual_month == 2:
    string_actual_month = "Fevereiro"
elif actual_month == 3:
    string_actual_month = "Março"
elif actual_month == 4:
    string_actual_month = "Abril"
elif actual_month == 5:
    string_actual_month = "Maio"
elif actual_month == 6:
    string_actual_month = "Junho"
elif actual_month == 7:
    string_actual_month = "Julho"
elif actual_month == 8:
    string_actual_month = "Agosto"
elif actual_month == 9:
    string_actual_month = "Setembro"
elif actual_month == 10:
    string_actual_month = "Outubro"
elif actual_month == 11:
    string_actual_month = "Novembro"
elif actual_month == 12:
    string_actual_month = "Dezembro"

menu_options: list = ["Selecione uma opção", "Registrar despesa", "Registrar receita", "Registrar transferência", "Empréstimos", "Relatórios", "Cadastros", "Configurações"]
expense_categories: list = ["Selecione uma opção","Casa","Lazer","Eletroeletrônicos","Serviços","Entretenimento","Presente","Restaurante","Saúde","Supermercado","Transporte","Vestuário"]
revenue_categories: list = ["Selecione uma opção","Ajuste","Depósito","Prêmio","Salário","Vale","Rendimentos"]
transfer_categories: list = ["Selecione uma opção", "DOC", "TED", "Pix"]
accounts = ["Selecione uma opção","Ben Visa Vale","Carteira","Caixa","Mercado Pago","Nubank", "Pagbank", "Picpay","Sicoob"]
accounts_type = ["Conta Corrente","Conta Salário","Fundo de Garantia","Vale Alimentação"]

to_remove_list: list = ["'", ")", "(", ",", "Decimal", '"', "[", "]", "datetime.date"]