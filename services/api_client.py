"""
Cliente HTTP para comunicação com a expenselit-api.

Este módulo implementa um cliente HTTP robusto para comunicação
com a API, incluindo gerenciamento de autenticação JWT,
tratamento de erros e retry logic.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
import streamlit as st

from config.settings import api_config, auth_config
from .cookie_auth import cookie_auth


logger = logging.getLogger(__name__)


class ApiClientError(Exception):
    """Exceção base para erros do cliente da API."""
    pass


class AuthenticationError(ApiClientError):
    """Exceção para erros de autenticação."""
    pass


class ValidationError(ApiClientError):
    """Exceção para erros de validação."""
    pass


class NotFoundError(ApiClientError):
    """Exceção para recursos não encontrados."""
    pass


class PermissionError(ApiClientError):
    """Exceção para erros de permissão."""
    pass


class ApiClient:
    """
    Cliente HTTP para comunicação com a expenselit-api.

    Esta classe implementa um cliente HTTP completo com suporte a:
    - Autenticação JWT automática
    - Refresh de tokens
    - Tratamento de erros
    - Retry logic
    - Cache de sessão
    """

    def __init__(self):
        """Inicializa o cliente da API."""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Obtém os headers de autenticação com token JWT.

        Returns
        -------
        Dict[str, str]
            Headers de autenticação

        Raises
        ------
        AuthenticationError
            Se o token não estiver disponível ou for inválido
        """
        access_token = st.session_state.get('access_token')
        if not access_token:
            raise AuthenticationError("Token de acesso não encontrado")

        return {'Authorization': f'Bearer {access_token}'}

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Processa a resposta da API e trata erros.

        Parameters
        ----------
        response : requests.Response
            Resposta da requisição HTTP

        Returns
        -------
        Dict[str, Any]
            Dados da resposta em formato JSON

        Raises
        ------
        AuthenticationError
            Para erros 401 (não autorizado)
        PermissionError
            Para erros 403 (sem permissão)
        NotFoundError
            Para erros 404 (não encontrado)
        ValidationError
            Para erros 400 (dados inválidos)
        ApiClientError
            Para outros erros da API
        """
        try:
            if response.status_code == 200:
                return response.json() if response.content else {}
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {}
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise ValidationError(f"Dados inválidos: {error_data}")
            elif response.status_code == 401:
                error_data = response.json() if response.content else {}

                # Verifica se é um token expirado ou inválido
                if isinstance(error_data, dict) and 'code' in error_data:
                    if error_data.get('code') == 'token_not_valid':
                        messages = error_data.get('messages', [])
                        if any(msg.get(
                            'message'
                        ) == 'Token is expired' for msg in messages):
                            # Token expirado - tenta renovar automaticamente
                            logger.info(
                                """
                                Token expirado detectado,
                                tentando renovar...
                                """
                            )
                            if hasattr(
                                self,
                                'refresh_token'
                            ) and self.refresh_token():
                                logger.info(
                                    """Token renovado com sucesso,
                                    reexecutando requisição...
                                    """
                                )
                                # Não relança a exceção,
                                # deixa a requisição original tentar novamente
                                return {}
                            else:
                                raise AuthenticationError(
                                    """Sua sessão expirou.
                                    Por favor,
                                    faça login novamente para continuar.
                                    """
                                )
                        else:
                            raise AuthenticationError(
                                """Token inválido.
                                Por favor, faça login novamente para continuar.
                                """
                            )

                # Erro de autenticação genérico
                raise AuthenticationError(
                    """
                    Erro de autenticação.
                    Verifique suas credenciais e tente novamente.
                    """
                )
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                raise PermissionError(f"Sem permissão: {error_data}")
            elif response.status_code == 404:
                raise NotFoundError("Recurso não encontrado")
            else:
                error_data = response.json() if response.content else {}
                raise ApiClientError(
                    f"Erro da API ({response.status_code}): {error_data}"
                )
        except json.JSONDecodeError:
            # Log do conteúdo da resposta para debug
            logger.error(f"Resposta não-JSON da API: {response.text[:500]}")
            raise ApiClientError(
                f"Resposta inválida da API ({response.status_code})"
            )

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autentica o usuário e obtém tokens JWT.

        Parameters
        ----------
        username : str
            Nome de usuário
        password : str
            Senha do usuário

        Returns
        -------
        Dict[str, Any]
            Dados de autenticação incluindo tokens

        Raises
        ------
        AuthenticationError
            Se as credenciais forem inválidas
        ApiClientError
            Para outros erros da API
        """
        url = api_config.get_full_url(auth_config.TOKEN_ENDPOINT)
        data = {"username": username, "password": password}

        logger.info(f"Tentando autenticar em: {url}")

        try:
            response = self.session.post(url, json=data)
            logger.info(f"Status da resposta: {response.status_code}")
            auth_data = self._handle_response(response)

            # Armazena tokens na sessão
            st.session_state['access_token'] = auth_data['access']
            st.session_state['refresh_token'] = auth_data['refresh']
            st.session_state['token_expires_at'] = (
                datetime.now() + timedelta(
                    minutes=auth_config.ACCESS_TOKEN_LIFETIME
                )
            )
            st.session_state['is_authenticated'] = True
            st.session_state['username'] = username

            # Salva token usando sistema de cookies
            cookie_auth.save_auth_data(
                username,
                auth_data['access'],
                auth_data['refresh']
            )

            logger.info(f"Usuário {username} autenticado com sucesso")
            return auth_data

        except requests.RequestException as e:
            logger.error(f"Erro de conexão na autenticação: {e}")
            raise ApiClientError(f"Erro de conexão: {e}")

    def refresh_token(self) -> bool:
        """
        Renova o token de acesso usando o refresh token.

        Returns
        -------
        bool
            True se o token foi renovado com sucesso

        Raises
        ------
        AuthenticationError
            Se o refresh token for inválido
        """
        refresh_token = st.session_state.get('refresh_token')
        if not refresh_token:
            raise AuthenticationError("Refresh token não encontrado")

        url = api_config.get_full_url(auth_config.REFRESH_ENDPOINT)
        data = {"refresh": refresh_token}

        try:
            response = self.session.post(url, json=data)
            token_data = self._handle_response(response)

            # Atualiza o token de acesso
            st.session_state['access_token'] = token_data['access']
            st.session_state['token_expires_at'] = (
                datetime.now() + timedelta(
                    minutes=auth_config.ACCESS_TOKEN_LIFETIME
                )
            )

            logger.info("Token renovado com sucesso")
            return True

        except requests.RequestException as e:
            logger.error(f"Erro ao renovar token: {e}")
            raise ApiClientError(f"Erro de conexão: {e}")

    def _ensure_authenticated(self) -> None:
        """
        Garante que o usuário está autenticado e o token é válido.

        Raises
        ------
        AuthenticationError
            Se o usuário não estiver autenticado
        """
        if not st.session_state.get('is_authenticated'):
            raise AuthenticationError("Usuário não autenticado")

        # Verifica se o token está próximo do vencimento
        token_expires_at = st.session_state.get('token_expires_at')
        if token_expires_at and datetime.now() >= token_expires_at - timedelta(
            minutes=2
        ):
            try:
                self.refresh_token()
            except AuthenticationError:
                st.session_state['is_authenticated'] = False
                raise AuthenticationError(
                    "Sessão expirada. Faça login novamente."
                )

    def get(
            self,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza uma requisição GET à API.

        Parameters
        ----------
        endpoint : str
            Endpoint da API (sem barra inicial)
        params : Dict[str, Any], optional
            Parâmetros da query string

        Returns
        -------
        Dict[str, Any]
            Resposta da API
        """
        self._ensure_authenticated()
        url = api_config.get_full_url(endpoint)
        headers = self._get_auth_headers()

        try:
            response = self.session.get(url, headers=headers, params=params)
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Erro na requisição GET {endpoint}: {e}")
            raise ApiClientError(f"Erro de conexão: {e}")

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma requisição POST à API.

        Parameters
        ----------
        endpoint : str
            Endpoint da API (sem barra inicial)
        data : Dict[str, Any]
            Dados para enviar no corpo da requisição

        Returns
        -------
        Dict[str, Any]
            Resposta da API
        """
        self._ensure_authenticated()
        url = api_config.get_full_url(endpoint)
        headers = self._get_auth_headers()

        try:
            response = self.session.post(url, headers=headers, json=data)
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Erro na requisição POST {endpoint}: {e}")
            raise ApiClientError(f"Erro de conexão: {e}")

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma requisição PUT à API.

        Parameters
        ----------
        endpoint : str
            Endpoint da API (sem barra inicial)
        data : Dict[str, Any]
            Dados para atualizar

        Returns
        -------
        Dict[str, Any]
            Resposta da API
        """
        self._ensure_authenticated()
        url = api_config.get_full_url(endpoint)
        headers = self._get_auth_headers()

        try:
            response = self.session.put(url, headers=headers, json=data)
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Erro na requisição PUT {endpoint}: {e}")
            raise ApiClientError(f"Erro de conexão: {e}")

    def delete(self, endpoint: str) -> None:
        """
        Realiza uma requisição DELETE à API.

        Parameters
        ----------
        endpoint : str
            Endpoint da API (sem barra inicial)
        """
        self._ensure_authenticated()
        url = api_config.get_full_url(endpoint)
        headers = self._get_auth_headers()

        try:
            response = self.session.delete(url, headers=headers)
            self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Erro na requisição DELETE {endpoint}: {e}")
            raise ApiClientError(f"Erro de conexão: {e}")

    def get_user_permissions(self) -> Dict[str, Any]:
        """
        Obtém as permissões do usuário atual.

        Returns
        -------
        Dict[str, Any]
            Dados de permissões do usuário
        """
        return self.get(auth_config.USER_PERMISSIONS_ENDPOINT)

    def logout(self) -> None:
        """Remove dados de autenticação da sessão e cookie."""
        keys_to_remove = [
            'access_token', 'refresh_token', 'token_expires_at',
            'is_authenticated', 'username', 'user_permissions'
        ]
        for key in keys_to_remove:
            st.session_state.pop(key, None)

        # Remove dados de autenticação persistentes
        cookie_auth.clear_auth_data()

        logger.info("Usuário deslogado")

    def restore_session_if_available(self) -> bool:
        """
        Restaura sessão de autenticação se dados válidos estiverem disponíveis.

        Returns
        -------
        bool
            True se sessão foi restaurada com sucesso
        """
        return cookie_auth.restore_session()


# Instância global do cliente da API
api_client = ApiClient()
