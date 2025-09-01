"""
Sistema de autenticação com streamlit-cookies-controller.

Este módulo implementa autenticação JWT usando cookies reais
através do streamlit-cookies-controller para persistir tokens entre sessões.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import base64

import streamlit as st
from streamlit_cookies_controller import CookieController

logger = logging.getLogger(__name__)


class CookieAuth:
    """Sistema de autenticação com cookies reais."""
    def __init__(self):
        self.cookie_controller = CookieController()
        self.cookie_name = 'expenselit_auth_token'
        self.token_expiry_days = 1

    def save_auth_data(
        self,
        username: str,
        access_token: str,
        refresh_token: str
    ) -> None:
        """
        Salva dados de autenticação em cookie.

        Parameters
        ----------
        username : str
            Nome do usuário
        access_token : str
            Token de acesso
        refresh_token : str
            Token de refresh
        """
        try:
            auth_data = {
                'username': username,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': (
                       datetime.now() + timedelta(
                              days=self.token_expiry_days
                            )
                        ).isoformat(),
                'saved_at': datetime.now().isoformat()
            }

            # Codifica dados em base64
            encoded_data = base64.b64encode(
                json.dumps(auth_data).encode()
            ).decode()

            # Salva no cookie
            self.cookie_controller.set(
                self.cookie_name,
                encoded_data,
                max_age=self.token_expiry_days * 24 * 60 * 60  # em segundos
            )

            logger.info(
                f"Dados de autenticação salvos em cookie para usuário {username}"
            )

        except Exception as e:
            logger.warning(f"Erro ao salvar dados de autenticação: {e}")

    def load_auth_data(self) -> Optional[Dict[str, Any]]:
        """
        Carrega dados de autenticação do cookie.

        Returns
        -------
        Optional[Dict[str, Any]]
            Dados de autenticação ou None se não encontrados/expirados
        """
        try:
            encoded_data = self.cookie_controller.get(self.cookie_name)
            if not encoded_data:
                return None

            # Decodifica dados
            auth_data = json.loads(base64.b64decode(
                encoded_data.encode()
            ).decode())

            # Verifica se não expirou
            expires_at = datetime.fromisoformat(
                auth_data.get('expires_at', '')
            )
            if datetime.now() >= expires_at:
                logger.info("Dados de autenticação expirados")
                self.clear_auth_data()
                return None

            logger.info(
                f"Dados de autenticação carregados do cookie para usuário {auth_data.get('username')}"
            )
            return auth_data

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Erro ao carregar dados de autenticação: {e}")
            self.clear_auth_data()
            return None

    def clear_auth_data(self) -> None:
        """Remove dados de autenticação do cookie."""
        try:
            self.cookie_controller.remove(self.cookie_name)
            logger.info("Dados de autenticação removidos do cookie")
        except Exception as e:
            logger.warning(f"Erro ao remover dados de autenticação: {e}")

    def restore_session(self) -> bool:
        """
        Restaura sessão de autenticação se dados válidos
        estiverem salvos em cookie.

        Returns
        -------
        bool
            True se sessão foi restaurada com sucesso
        """
        # Se já está autenticado, não precisa fazer nada
        if st.session_state.get('is_authenticated'):
            return True

        # Tenta carregar dados salvos do cookie
        auth_data = self.load_auth_data()
        if not auth_data:
            return False

        try:
            # Restaura sessão
            st.session_state['access_token'] = auth_data.get('access_token')
            st.session_state['refresh_token'] = auth_data.get('refresh_token')
            st.session_state['username'] = auth_data.get('username')
            st.session_state['is_authenticated'] = True
            st.session_state['token_expires_at'] = (
                 datetime.now() + timedelta(minutes=30)
            )  # Configurar conforme necessário
            logger.info(
                f"Sessão restaurada do cookie para usuário {auth_data.get('username')}"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao restaurar sessão: {e}")
            self.clear_auth_data()
            return False


# Instância global
cookie_auth = CookieAuth()
