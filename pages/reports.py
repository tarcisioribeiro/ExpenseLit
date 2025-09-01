"""
Página de relatórios.
"""

import streamlit as st
from pages.router import BasePage


class ReportsPage(BasePage):
    def __init__(self):
        super().__init__("Relatórios", "📈")

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
        st.subheader("📈 Relatórios")
        self.render()

    def render(self) -> None:
        st.info("🚧 Página de relatórios em desenvolvimento...")
