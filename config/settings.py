"""
Configurações centralizadas da aplicação ExpenseLit.

Este módulo contém todas as configurações necessárias para o funcionamento
da aplicação Streamlit integrada com a expenselit-api.
"""

import os
from typing import Dict
# Any
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


class ApiConfig:
    """
    Configurações da API ExpenseLit.

    Esta classe centraliza todas as configurações relacionadas à API,
    incluindo URLs base, endpoints e configurações de autenticação.
    """

    # URLs base
    BASE_URL = os.getenv("API_BASE_URL")
    API_VERSION: str = "v1"
    API_BASE_PATH: str = f"/api/{API_VERSION}"

    @classmethod
    def get_full_url(cls, endpoint: str = "") -> str:
        """
        Constrói a URL completa para um endpoint específico.

        Parameters
        ----------
        endpoint : str, optional
            Endpoint específico da API, por padrão ""

        Returns
        -------
        str
            URL completa formatada

        Examples
        --------
        >>> ApiConfig.get_full_url("accounts/")
        'http://localhost:8002/api/v1/accounts/'
        """
        return f"{cls.BASE_URL}{cls.API_BASE_PATH}/{endpoint}"


class AuthConfig:
    """
    Configurações de autenticação JWT.

    Esta classe gerencia as configurações relacionadas à autenticação
    JWT da aplicação.
    """

    TOKEN_ENDPOINT: str = "authentication/token/"
    REFRESH_ENDPOINT: str = "authentication/token/refresh/"
    USER_PERMISSIONS_ENDPOINT: str = "authentication/user-permissions/"

    # Timeouts em minutos
    ACCESS_TOKEN_LIFETIME: int = 15
    REFRESH_TOKEN_LIFETIME: int = 60


class AppConfig:
    """
    Configurações gerais da aplicação.

    Esta classe contém configurações gerais do Streamlit e da aplicação.
    """

    # Configurações do Streamlit
    PAGE_TITLE: str = "ExpenseLit - Controle Financeiro"
    PAGE_ICON: str = "💰"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "auto"

    # Diretórios
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    LIBRARY_DIR: Path = BASE_DIR / "library"

    # Configurações de sessão
    SESSION_TIMEOUT_MINUTES: int = 30


class DatabaseCategories:
    """
    Categorias e tipos disponíveis na API.

    Esta classe centraliza todas as categorias e tipos utilizados
    pelos diferentes módulos da API.
    """

    # Tipos de conta
    ACCOUNT_TYPES: Dict[str, str] = {
        "CC": "Conta Corrente",
        "CS": "Conta Salário",
        "FG": "Fundo de Garantia",
        "VA": "Vale Alimentação"
    }

    # Instituições
    INSTITUTIONS: Dict[str, str] = {
        "NUB": "Nubank",
        "SIC": "Sicoob",
        "MPG": "Mercado Pago",
        "IFB": "Ifood Benefícios",
        "CEF": "Caixa Econômica Federal"
    }

    # Categorias de despesas
    EXPENSE_CATEGORIES: Dict[str, str] = {
        "food and drink": "Comida e bebida",
        "bills and services": "Contas e serviços",
        "electronics": "Eletrônicos",
        "family and friends": "Amizades e Família",
        "pets": "Animais de estimação",
        "digital signs": "Assinaturas digitais",
        "house": "Casa",
        "purchases": "Compras",
        "donate": "Doações",
        "education": "Educação",
        "loans": "Empréstimos",
        "entertainment": "Entretenimento",
        "taxes": "Impostos",
        "investments": "Investimentos",
        "others": "Outros",
        "vestuary": "Roupas",
        "health and care": "Saúde e cuidados pessoais",
        "professional services": "Serviços profissionais",
        "supermarket": "Supermercado",
        "rates": "Taxas",
        "transport": "Transporte",
        "travels": "Viagens"
    }

    # Categorias de receitas
    REVENUE_CATEGORIES: Dict[str, str] = {
        "deposit": "Depósito",
        "award": "Prêmio",
        "salary": "Salário",
        "ticket": "Vale",
        "income": "Rendimentos",
        "refund": "Reembolso",
        "cashback": "Cashback",
        "transfer": "Transferência Recebida",
        "received_loan": "Empréstimo Recebido",
        "loan_devolution": "Devolução de empréstimo"
    }

    # Bandeiras de cartão
    CARD_FLAGS: Dict[str, str] = {
        "MSC": "Master Card",
        "VSA": "Visa",
        "ELO": "Elo",
        "EXP": "American Express",
        "HCD": "Hipercard"
    }

    # Sexo
    SEX_CHOICES: Dict[str, str] = {
        "M": "Masculino",
        "F": "Feminino"
    }

    # Emojis por categoria de despesa
    EXPENSE_CATEGORY_EMOJIS: Dict[str, str] = {
        "food and drink": "🍽️",
        "bills and services": "🧾",
        "electronics": "📱",
        "family and friends": "👨‍👩‍👧‍👦",
        "pets": "🐕",
        "digital signs": "💻",
        "house": "🏠",
        "purchases": "🛒",
        "donate": "💝",
        "education": "📚",
        "loans": "💰",
        "entertainment": "🎭",
        "taxes": "🏛️",
        "investments": "📈",
        "others": "💸",
        "vestuary": "👕",
        "health and care": "🏥",
        "professional services": "⚙️",
        "supermarket": "🏬",
        "rates": "📊",
        "transport": "🚗",
        "travels": "✈️"
    }

    # Emojis por categoria de receita
    REVENUE_CATEGORY_EMOJIS: Dict[str, str] = {
        "deposit": "💰",
        "award": "🏆",
        "salary": "💵",
        "ticket": "🎫",
        "income": "📈",
        "refund": "💸",
        "cashback": "🔄",
        "transfer": "💰",
        "received_loan": "🤝",
        "loan_devolution": "↩️"
    }

    # Dicionários traduzidos (chaves/valores invertidos para interface)
    TRANSLATED_ACCOUNT_TYPES: Dict[str, str] = {
        "Conta Corrente": "CC",
        "Conta Salário": "CS",
        "Fundo de Garantia": "FG",
        "Vale Alimentação": "VA"
    }

    TRANSLATED_INSTITUTIONS: Dict[str, str] = {
        "Nubank": "NUB",
        "Sicoob": "SIC",
        "Mercado Pago": "MPG",
        "Ifood Benefícios": "IFB",
        "Caixa Econômica Federal": "CEF"
    }

    TRANSLATED_EXPENSE_CATEGORIES: Dict[str, str] = {
        "Comida e bebida": "food and drink",
        "Contas e serviços": "bills and services",
        "Eletrônicos": "electronics",
        "Amizades e Família": "family and friends",
        "Animais de estimação": "pets",
        "Assinaturas digitais": "digital signs",
        "Casa": "house",
        "Compras": "purchases",
        "Doações": "donate",
        "Educação": "education",
        "Empréstimos": "loans",
        "Entretenimento": "entertainment",
        "Impostos": "taxes",
        "Investimentos": "investments",
        "Outros": "others",
        "Roupas": "vestuary",
        "Saúde e cuidados pessoais": "health and care",
        "Serviços profissionais": "professional services",
        "Supermercado": "supermarket",
        "Taxas": "rates",
        "Transporte": "transport",
        "Viagens": "travels"
    }

    TRANSLATED_REVENUE_CATEGORIES: Dict[str, str] = {
        "Depósito": "deposit",
        "Prêmio": "award",
        "Salário": "salary",
        "Vale": "ticket",
        "Rendimentos": "income",
        "Reembolso": "refund",
        "Cashback": "cashback",
        "Transferência Recebida": "transfer",
        "Empréstimo Recebido": "received_loan",
        "Devolução de empréstimo": "loan_devolution"
    }

    TRANSLATED_CARD_FLAGS: Dict[str, str] = {
        "Master Card": "MSC",
        "Visa": "VSA",
        "Elo": "ELO",
        "American Express": "EXP",
        "Hipercard": "HCD"
    }

    TRANSLATED_SEX_CHOICES: Dict[str, str] = {
        "Masculino": "M",
        "Feminino": "F"
    }

    DARK_THEME = '''[theme]
primaryColor="#bd93f9"
backgroundColor="#282a36"
secondaryBackgroundColor="#44475a"
textColor="#f8f8f2"
showWidgetBorder=true
'''

    LIGHT_THEME = """[theme]
primaryColor = "#61afef"
backgroundColor = "#fefefe"
secondaryBackgroundColor = "#e6e6e6"
textColor = "#3c4048"
showWidgetBorder=true
"""


# Instâncias globais das configurações
api_config = ApiConfig()
auth_config = AuthConfig()
app_config = AppConfig()
db_categories = DatabaseCategories()
