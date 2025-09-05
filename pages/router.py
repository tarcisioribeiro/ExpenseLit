"""
Router simplificado para compatibilidade com as classes existentes.

Este módulo mantém apenas as classes base necessárias para
compatibilidade com o código existente.
"""

import streamlit as st
from abc import ABC, abstractmethod


class BasePage(ABC):
    """
    Classe base para todas as páginas da aplicação.

    Mantida para compatibilidade com as páginas existentes.
    """

    def __init__(self, title: str, icon: str = "📄"):
        """
        Inicializa a página base.

        Parameters
        ----------
        title : str
            Título da página
        icon : str, optional
            Ícone da página, por padrão "📄"
        """
        self.title = title
        self.icon = icon

    @abstractmethod
    def render(self) -> None:
        """
        Renderiza o conteúdo da página.

        Este método deve ser implementado por cada página específica.
        """
        pass

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
        st.subheader(f"{self.icon} {self.title}")
        self.render()
