"""
Aplicação ExpenseLit - Ponto de entrada único.

Sistema de controle financeiro pessoal seguindo o padrão de navegação
centralizada com um único arquivo de entrada.
"""

import streamlit as st
from components.auth import AuthLogin
from services.api_client import api_client

# Configuração da página
st.set_page_config(
    page_title="ExpenseLit - Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)


# Carrega estilos customizados
def load_css():
    """Carrega arquivo CSS customizado."""
    import logging
    from pathlib import Path

    logger = logging.getLogger(__name__)

    try:
        css_path = Path("static/style.css")
        if css_path.exists():
            with open(css_path) as f:
                st.markdown(
                    f"<style>{f.read()}</style>",
                    unsafe_allow_html=True
                )
    except Exception as e:
        logger.warning(f"Erro ao carregar CSS: {e}")


# Aplicar tema inicial
def apply_initial_theme():
    """Aplica o tema inicial baseado no session_state."""
    theme = st.session_state.get('theme', 'dark')
    
    # Aplica o tema via JavaScript
    theme_js = f"""
    <script>
    document.documentElement.setAttribute('data-theme', '{theme}');
    </script>
    """
    
    st.markdown(theme_js, unsafe_allow_html=True)


load_css()
apply_initial_theme()

def main():
    """Função principal da aplicação com validação de token automática."""
    # Tenta restaurar sessão do cookie automaticamente
    if not st.session_state.get('is_authenticated', False):
        api_client.restore_session_if_available()
    
    # Se está autenticado, vai direto para o dashboard
    if st.session_state.get('is_authenticated', False):
        from home.main import HomePage
        HomePage().main_menu()
    else:
        # Se não está autenticado, mostra tela de login
        AuthLogin().get_login()


if __name__ == "__main__":
    main()
