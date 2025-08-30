"""
Menu principal da aplicação ExpenseLit.

Este módulo implementa o menu principal com navegação via selectbox,
seguindo o padrão do projeto CodexDB.
"""

import streamlit as st
from time import sleep
from components.auth import auth_component


class HomePage:
    """
    Classe que representa o menu principal da aplicação.
    """

    def main_menu(self):
        """
        Menu principal da aplicação com navegação via selectbox.
        """
        # Importações locais para evitar dependências circulares
        from pages.dashboard import DashboardPage
        from pages.accounts import AccountsPage
        from pages.expenses import ExpensesPage
        from pages.revenues import RevenuesPage
        from pages.credit_cards import CreditCardsPage
        from pages.loans import LoansPage
        from pages.transfers import TransfersPage
        from pages.members import MembersPage
        from pages.reports import ReportsPage
        from pages.settings import SettingsPage

        # Obtém dados do usuário
        username = st.session_state.get('username', 'Usuário')
        user_permissions = st.session_state.get('user_permissions', {})

        # Opções do menu organizadas por categoria
        menu_options = {
            "📊 Dashboard": DashboardPage,
            "🏦 Contas": AccountsPage,
            "💸 Despesas": ExpensesPage,
            "💰 Receitas": RevenuesPage,
            "💳 Cartões de Crédito": CreditCardsPage,
            "🏠 Empréstimos": LoansPage,
            "↔️ Transferências": TransfersPage,
            "👥 Membros": MembersPage,
            "📈 Relatórios": ReportsPage,
            "⚙️ Configurações": SettingsPage
        }
        
        # Mapeamento para redirecionamentos
        redirect_map = {
            "accounts": "🏦 Contas",
            "credit_cards": "💳 Cartões de Crédito",
            "expenses": "💸 Despesas",
            "revenues": "💰 Receitas"
        }

        with st.sidebar:
            # Header com logo/nome da aplicação
            st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <h1>💰 ExpenseLit</h1>
                <p>Controle Financeiro</p>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # Verifica se há redirecionamento pendente
            default_index = 0  # Dashboard como padrão
            if 'redirect_to' in st.session_state:
                redirect_page = st.session_state.pop('redirect_to')
                if redirect_page in redirect_map:
                    target_option = redirect_map[redirect_page]
                    if target_option in menu_options:
                        default_index = list(menu_options.keys()).index(target_option)

            # Selectbox para navegação (padrão CodexDB)
            selected_option = st.selectbox(
                label="📍 Navegação",
                options=list(menu_options.keys()),
                index=default_index
            )

            st.divider()

            # Informações do usuário
            st.markdown("### 👤 Sessão")
            st.markdown(f"**Usuário:** {username}")

            # Botão de logout
            if st.button("🔓 Sair", width='stretch'):
                self._handle_logout()

        # Renderiza a página selecionada
        selected_class = menu_options[selected_option]
        page_instance = selected_class()

        # Chama o método main_menu da página (padrão CodexDB)
        if hasattr(page_instance, 'main_menu'):
            page_instance.main_menu(
                token=st.session_state.get('access_token'),
                permissions=user_permissions
            )
        else:
            # Fallback para páginas que usam render()
            page_instance.render()

    def _handle_logout(self):
        """Gerencia o processo de logout."""
        # Realiza logout
        auth_component.logout()

        st.toast("👋 Logout realizado com sucesso!")

        # Limpa session_state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # Aguarda um momento e recarrega
        with st.spinner("Saindo..."):
            sleep(1)

        st.rerun()
