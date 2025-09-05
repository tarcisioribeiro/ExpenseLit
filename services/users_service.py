"""
Serviço para gerenciamento de usuários.

Este módulo implementa operações relacionadas aos
usuários Django disponíveis para vinculação.
"""

import logging
from typing import List, Dict, Any

from services.api_client import api_client, ApiClientError


logger = logging.getLogger(__name__)


class UsersService:
    """
    Serviço para operações com usuários Django.
    """

    def get_available_users(self) -> List[Dict[str, Any]]:
        """
        Obtém usuários disponíveis para vinculação com membros.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de usuários disponíveis (não superusuários e não vinculados)

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            api_response = api_client.get("users/available/")
            # Verifica se é uma lista de usuários
            if isinstance(api_response, list):
                response: List[Dict[str, Any]] = api_response
            else:
                response = api_response.get('results', [])

            # Formata dados para exibição
            formatted_users = []
            for user in response:
                display_name = self._format_user_display_name(user)
                formatted_users.append({
                    'id': user['id'],
                    'username': user['username'],
                    'display_name': display_name,
                    'email': user.get('email', ''),
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', '')
                })

            return formatted_users

        except ApiClientError as e:
            logger.error(f"Erro ao buscar usuários disponíveis: {e}")
            raise

    def _format_user_display_name(self, user: Dict[str, Any]) -> str:
        """
        Formata nome de exibição do usuário.

        Parameters
        ----------
        user : Dict[str, Any]
            Dados do usuário

        Returns
        -------
        str
            Nome formatado para exibição
        """
        first_name = user.get('first_name', '').strip()
        last_name = user.get('last_name', '').strip()
        username = user.get('username', '').strip()

        if first_name or last_name:
            full_name = f"{first_name} {last_name}".strip()
            return f"{full_name} ({username})"
        else:
            return username


# Instância global do serviço de usuários
users_service = UsersService()
