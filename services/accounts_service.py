"""
Serviço para gerenciamento de contas.

Este módulo implementa todas as operações relacionadas ao
gerenciamento de contas financeiras na expenselit-api.
"""

import logging
from typing import List, Dict, Any
# Optional

from services.api_client import api_client, ApiClientError


logger = logging.getLogger(__name__)


class AccountsService:
    """
    Serviço para operações com contas financeiras.

    Esta classe implementa todas as operações CRUD e consultas
    específicas relacionadas às contas financeiras.
    """

    ENDPOINT = "accounts/"

    def get_all_accounts(
        self,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtém todas as contas do usuário.

        Parameters
        ----------
        active_only : bool, optional
            Se deve retornar apenas contas ativas, por padrão True

        Returns
        -------
        List[Dict[str, Any]]
            Lista de contas

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            params = {"is_active": "true"} if active_only else {}
            response = api_client.get(self.ENDPOINT, params=params)

            # A API pode retornar uma lista direta ou um objeto com 'results'
            if isinstance(response, dict) and 'results' in response:
                return response['results']
            elif isinstance(response, list):
                return response
            else:
                return []

        except ApiClientError as e:
            logger.error(f"Erro ao buscar contas: {e}")
            raise

    def get_account_by_id(self, account_id: int) -> Dict[str, Any]:
        """
        Obtém uma conta específica pelo ID.

        Parameters
        ----------
        account_id : int
            ID da conta

        Returns
        -------
        Dict[str, Any]
            Dados da conta

        Raises
        ------
        ApiClientError
            Se a conta não for encontrada ou houver erro na API
        """
        try:
            endpoint = f"{self.ENDPOINT}{account_id}/"
            return api_client.get(endpoint)
        except ApiClientError as e:
            logger.error(f"Erro ao buscar conta {account_id}: {e}")
            raise

    def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova conta.

        Parameters
        ----------
        account_data : Dict[str, Any]
            Dados da conta a ser criada
            Campos obrigatórios: name, account_type
            Campos opcionais: account_image, is_active

        Returns
        -------
        Dict[str, Any]
            Dados da conta criada

        Raises
        ------
        ApiClientError
            Se houver erro na validação ou criação

        Examples
        --------
        >>> account_data = {
        ...     "name": "NUB",
        ...     "account_type": "CC",
        ...     "is_active": True
        ... }
        >>> account = accounts_service.create_account(account_data)
        """
        try:
            return api_client.post(self.ENDPOINT, account_data)
        except ApiClientError as e:
            logger.error(f"Erro ao criar conta: {e}")
            raise

    def update_account(
        self,
        account_id: int,
        account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza uma conta existente.

        Parameters
        ----------
        account_id : int
            ID da conta a ser atualizada
        account_data : Dict[str, Any]
            Novos dados da conta

        Returns
        -------
        Dict[str, Any]
            Dados da conta atualizada

        Raises
        ------
        ApiClientError
            Se a conta não for encontrada ou houver erro na validação
        """
        try:
            endpoint = f"{self.ENDPOINT}{account_id}/"
            return api_client.put(endpoint, account_data)
        except ApiClientError as e:
            logger.error(f"Erro ao atualizar conta {account_id}: {e}")
            raise

    def delete_account(self, account_id: int) -> None:
        """
        Exclui uma conta.

        Parameters
        ----------
        account_id : int
            ID da conta a ser excluída

        Raises
        ------
        ApiClientError
            Se a conta não for encontrada ou houver erro na exclusão
        """
        try:
            endpoint = f"{self.ENDPOINT}{account_id}/"
            api_client.delete(endpoint)
            logger.info(f"Conta {account_id} excluída com sucesso")
        except ApiClientError as e:
            logger.error(f"Erro ao excluir conta {account_id}: {e}")
            raise

    def get_accounts_for_select(
        self,
        active_only: bool = True
    ) -> Dict[str, int]:
        """
        Obtém contas formatadas para componentes de seleção.

        Parameters
        ----------
        active_only : bool, optional
            Se deve retornar apenas contas ativas, por padrão True

        Returns
        -------
        Dict[str, int]
            Dicionário com nome da conta como chave e ID como valor

        Examples
        --------
        >>> accounts = accounts_service.get_accounts_for_select()
        >>> print(accounts)
        {'Nubank': 1, 'Sicoob': 2, 'Mercado Pago': 3}
        """
        try:
            accounts = self.get_all_accounts(active_only=active_only)
            return {account['name']: account['id'] for account in accounts}
        except ApiClientError as e:
            logger.error(f"Erro ao buscar contas para seleção: {e}")
            return {}

    def validate_account_data(self, account_data: Dict[str, Any]) -> List[str]:
        """
        Valida os dados de uma conta antes do envio para a API.

        Parameters
        ----------
        account_data : Dict[str, Any]
            Dados da conta para validação

        Returns
        -------
        List[str]
            Lista de mensagens de erro. Lista vazia se válido.
        """
        errors = []

        # Campo obrigatório: name
        if not account_data.get('name', '').strip():
            errors.append("Nome da conta é obrigatório")

        # Campo obrigatório: account_type
        account_type = account_data.get('account_type', '').strip()
        if not account_type:
            errors.append("Tipo de conta é obrigatório")

        # Validação de is_active se fornecido
        is_active = account_data.get('is_active')
        if is_active is not None and not isinstance(is_active, bool):
            errors.append("Status ativo deve ser verdadeiro ou falso")

        return errors

    def get_account_balance(self, account_id: int) -> float:
        """
        Calcula o saldo atual de uma conta.

        Note
        ----
        Esta funcionalidade requer implementação adicional na API
        para cálculo de saldos baseado em receitas e despesas.

        Parameters
        ----------
        account_id : int
            ID da conta

        Returns
        -------
        float
            Saldo atual da conta

        Raises
        ------
        NotImplementedError
            Funcionalidade não implementada na API atual
        """
        raise NotImplementedError(
            "Cálculo de saldo requer implementação adicional na API"
        )


# Instância global do serviço de contas
accounts_service = AccountsService()
