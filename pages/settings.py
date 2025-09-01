"""
Página de configurações.
"""

import streamlit as st
from pages.router import BasePage
import time


class SettingsPage(BasePage):
    def __init__(self):
        super().__init__("Configurações", "⚙️")

    def main_menu(self, token=None, permissions=None):
        """
        Método principal seguindo padrão CodexDB.

        Parameters
        ----------
        token : str, optional
            Token de autenticação (mantido para compatibilidade)
        permissions : dict, optional
            Permissões do usuário (mantido para compatibilidade)
        """
        st.subheader("⚙️ Configurações")
        self.render()

    def render(self) -> None:
        """
        Renderiza as configurações da aplicação.
        """
        # Configurações do sistema
        self._render_system_settings()

    def _render_system_settings(self) -> None:
        """
        Renderiza as configurações do sistema.
        """
        st.markdown("### 🔧 Configurações do Sistema")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Configurações de Interface:**")

            # Configuração de spinners
            spinner_duration = st.slider(
                "⏱️ Duração dos Spinners (segundos)",
                min_value=1,
                max_value=5,
                value=2,
                help="Tempo de exibição dos indicadores de carregamento"
            )

            # Configuração de toast
            toast_duration = st.slider(
                "🍞 Duração das Notificações (segundos)",
                min_value=1,
                max_value=10,
                value=2,
                help="Tempo de exibição das mensagens de sucesso"
            )

        with col2:
            st.markdown("**Configurações de Dados:**")

            # Configuração de paginação
            items_per_page = st.number_input(
                "📄 Itens por página",
                min_value=10,
                max_value=100,
                value=20,
                step=10,
                help="Número de itens exibidos por página nas listas"
            )

            # Auto-refresh
            auto_refresh = st.checkbox(
                "🔄 Atualização automática",
                value=False,
                help="Atualizar dados automaticamente a cada 30 segundos"
            )

        if st.button("💾 Salvar Configurações do Sistema", type="secondary"):
            # Salvar configurações no session_state
            st.session_state.update({
                'spinner_duration': spinner_duration,
                'toast_duration': toast_duration,
                'items_per_page': items_per_page,
                'auto_refresh': auto_refresh
            })

            st.toast("⚙️ Configurações do sistema salvas com sucesso!")
            time.sleep(1)
