"""
Menu principal da aplicação ExpenseLit.

Este módulo implementa o menu principal com navegação via selectbox,
seguindo o padrão do projeto CodexDB.
"""

import streamlit as st
from time import sleep
from components.auth import auth_component
from services.permissions_service import PermissionsService
from utils.ui_utils import ui_components


class HomePage:
    """
    Classe que representa o menu principal da aplicação.
    """

    def main_menu(self):
        """
        Menu principal da aplicação com navegação via selectbox.
        """
        # Verifica se o usuário tem acesso ao sistema
        if not PermissionsService.has_system_access():
            st.error("🚫 **Acesso Negado**")
            st.warning(
                "Você não possui as permissões necessárias para acessar "
                "este sistema."
            )
            st.info(
                "💡 **Entre em contato com o administrador** para ser "
                "adicionado ao grupo 'Membros'."
            )

            # Mostra botão de logout
            if st.button("🔓 Sair", type="primary"):
                self._handle_logout()

            st.stop()

        # Importações locais para evitar dependências circulares
        from pages.dashboard import DashboardPage
        from pages.accounts import AccountsPage
        from pages.expenses import ExpensesPage
        from pages.revenues import RevenuesPage
        from pages.credit_cards import CreditCardsPage
        # from pages.loans import LoansPage
        from pages.transfers import TransfersPage
        from pages.members import MembersPage
        # from pages.reports import ReportsPage

        # Obtém dados do usuário
        username = st.session_state.get('username', 'Usuário')
        user_permissions = st.session_state.get('user_permissions', {})

        # Opções do menu organizadas por categoria
        all_menu_options = {
            "📊 Dashboard": (DashboardPage, None),  # Sempre disponível
            "🏦 Contas": (AccountsPage, "accounts"),
            "💸 Despesas": (ExpensesPage, "expenses"),
            "💰 Receitas": (RevenuesPage, "revenues"),
            "💳 Cartões de Crédito": (CreditCardsPage, "credit_cards"),
            # "🏠 Empréstimos": (LoansPage, "loans"),
            "↔️ Transferências": (TransfersPage, "transfers"),
            "👥 Membros": (MembersPage, "members"),
            # "📈 Relatórios": (ReportsPage, None),  # Sempre disponível
        }

        # Filtra opções do menu baseado nas permissões
        menu_options = {}
        for label, (page_class, app_name) in all_menu_options.items():
            if app_name is None:
                # Páginas sempre disponíveis
                menu_options[label] = page_class
            elif PermissionsService.has_permission(app_name, "read"):
                # Páginas que precisam de permissão de leitura
                menu_options[label] = page_class

        # Mapeamento para redirecionamentos
        redirect_map = {
            "accounts": "🏦 Contas",
            "credit_cards": "💳 Cartões de Crédito",
            "expenses": "💸 Despesas",
            "revenues": "💰 Receitas"
        }

        with st.sidebar:
            # Header com logo/nome da aplicação aprimorado
            st.markdown("""
            <div style="
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #bd93f9, #ff79c6);
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(189, 147, 249, 0.3);
            ">
                <h1 style="color: #282a36; margin: 0; font-size: 2.2em;">
                    💰 ExpenseLit
                </h1>
                <p style="color: #44475a; margin: 5px 0; font-weight: 500;">
                    ✨ Controle Financeiro Inteligente
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Timer da sessão
            ui_components.render_session_timer()

            st.divider()

            # Verifica se há redirecionamento pendente
            default_index = 0  # Dashboard como padrão
            if 'redirect_to' in st.session_state:
                redirect_page = st.session_state.pop('redirect_to')
                if redirect_page in redirect_map:
                    target_option = redirect_map[redirect_page]
                    if target_option in menu_options:
                        default_index = list(menu_options.keys()).index(
                            target_option
                        )

            # Selectbox para navegação (padrão CodexDB)
            selected_option = st.selectbox(
                label="📍 Navegação",
                options=list(menu_options.keys()),
                index=default_index
            )

            st.divider()

            # Informações do usuário aprimoradas
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #44475a, #6272a4);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #8be9fd;
            ">
                <div style="color: #8be9fd; font-size: 14px; font-weight: bold;
                             margin-bottom: 8px;">
                    👤 Informações da Sessão
                </div>
                <div style="color: #f8f8f2; font-weight: 500;">
                    🧑‍💼 <strong>Usuário:</strong> """ + username + """
                </div>
                <div style="color: #50fa7b; font-size: 12px; margin-top: 8px;">
                    🟢 Conectado
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Botão de logout aprimorado
            if st.button("🔓 Sair", type="secondary", width='stretch'):
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

        ui_components.show_success_toast(
            "👋 Logout realizado com sucesso!", 2.0
        )

        # Limpa session_state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # Aguarda um momento e recarrega
        with st.spinner("Saindo..."):
            sleep(1)

        st.rerun()
