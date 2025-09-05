"""
Serviço para gerenciamento de cartões de crédito.

Este módulo implementa todas as operações relacionadas ao
gerenciamento de cartões de crédito na expenselit-api.
"""

import logging
from datetime import date
from typing import List, Dict, Any, Optional

from services.api_client import api_client, ApiClientError
from utils.date_utils import format_date_for_api


logger = logging.getLogger(__name__)


class CreditCardsService:
    """
    Serviço para operações com cartões de crédito.

    Esta classe implementa todas as operações CRUD e consultas
    específicas relacionadas aos cartões de crédito.
    """

    ENDPOINT = "credit-cards/"

    def list_credit_cards(
        self,
        associated_account: Optional[int] = None,
        is_active: Optional[bool] = None,
        flag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista todos os cartões de crédito (método principal).

        Parameters
        ----------
        associated_account : int, optional
            Filtrar por conta associada
        is_active : bool, optional
            Filtrar por status ativo
        flag : str, optional
            Filtrar por bandeira do cartão

        Returns
        -------
        List[Dict[str, Any]]
            Lista de cartões de crédito

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        return self.get_all_credit_cards(
            associated_account=associated_account,
            is_active=is_active,
            flag=flag
        )

    def get_all_credit_cards(
        self,
        associated_account: Optional[int] = None,
        is_active: Optional[bool] = None,
        flag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém todos os cartões de crédito com filtros opcionais.

        Parameters
        ----------
        associated_account : int, optional
            Filtrar por conta associada
        is_active : bool, optional
            Filtrar por status ativo
        flag : str, optional
            Filtrar por bandeira do cartão

        Returns
        -------
        List[Dict[str, Any]]
            Lista de cartões de crédito

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            params = {}

            if associated_account:
                params['associated_account'] = str(associated_account)
            if is_active is not None:
                params['is_active'] = str(is_active).lower()
            if flag:
                params['flag'] = flag

            response = api_client.get(self.ENDPOINT, params=params)

            # A API pode retornar uma lista direta ou um objeto com 'results'
            if isinstance(response, dict) and 'results' in response:
                return response['results']
            elif isinstance(response, list):
                return response
            else:
                return []

        except ApiClientError as e:
            logger.error(f"Erro ao buscar cartões de crédito: {e}")
            raise

    def get_credit_card_by_id(self, card_id: int) -> Dict[str, Any]:
        """
        Obtém um cartão de crédito específico pelo ID.

        Parameters
        ----------
        card_id : int
            ID do cartão de crédito

        Returns
        -------
        Dict[str, Any]
            Dados do cartão de crédito

        Raises
        ------
        ApiClientError
            Se o cartão não for encontrado ou houver erro na API
        """
        try:
            endpoint = f"{self.ENDPOINT}{card_id}/"
            return api_client.get(endpoint)
        except ApiClientError as e:
            logger.error(f"Erro ao buscar cartão {card_id}: {e}")
            raise

    def create_credit_card(
            self,
            card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo cartão de crédito.

        Parameters
        ----------
        card_data : Dict[str, Any]
            Dados do cartão a ser criado
            Campos obrigatórios:
                name, on_card_name, flag, validation_date,
                security_code, associated_account
            Campos opcionais:
                credit_limit, max_limit, is_active

        Returns
        -------
        Dict[str, Any]
            Dados do cartão criado

        Raises
        ------
        ApiClientError
            Se houver erro na validação ou criação

        Examples
        --------
        >>> card_data = {
        ...     "name": "Cartão Principal",
        ...     "on_card_name": "JOAO DA SILVA",
        ...     "flag": "MSC",
        ...     "validation_date": "2028-12-31",
        ...     "security_code": "123",
        ...     "credit_limit": "5000.00",
        ...     "max_limit": "10000.00",
        ...     "associated_account": 1
        ... }
        >>> card = credit_cards_service.create_credit_card(card_data)
        """
        try:
            # Processa dados antes do envio
            processed_data = self._process_card_data(card_data)
            return api_client.post(self.ENDPOINT, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao criar cartão de crédito: {e}")
            raise

    def update_credit_card(
            self,
            card_id: int,
            card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um cartão de crédito existente.

        Parameters
        ----------
        card_id : int
            ID do cartão a ser atualizado
        card_data : Dict[str, Any]
            Novos dados do cartão

        Returns
        -------
        Dict[str, Any]
            Dados do cartão atualizado

        Raises
        ------
        ApiClientError
            Se o cartão não for encontrado ou houver erro na validação
        """
        try:
            processed_data = self._process_card_data(card_data)
            endpoint = f"{self.ENDPOINT}{card_id}/"
            return api_client.put(endpoint, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao atualizar cartão {card_id}: {e}")
            raise

    def delete_credit_card(self, card_id: int) -> None:
        """
        Exclui um cartão de crédito.

        Parameters
        ----------
        card_id : int
            ID do cartão a ser excluído

        Raises
        ------
        ApiClientError
            Se o cartão não for encontrado ou houver erro na exclusão
        """
        try:
            endpoint = f"{self.ENDPOINT}{card_id}/"
            api_client.delete(endpoint)
            logger.info(f"Cartão {card_id} excluído com sucesso")
        except ApiClientError as e:
            logger.error(f"Erro ao excluir cartão {card_id}: {e}")
            raise

    def get_cards_by_account(self, account_id: int) -> List[Dict[str, Any]]:
        """
        Obtém cartões filtrados por conta associada.

        Parameters
        ----------
        account_id : int
            ID da conta associada

        Returns
        -------
        List[Dict[str, Any]]
            Lista de cartões da conta
        """
        return self.get_all_credit_cards(associated_account=account_id)

    def get_active_cards(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os cartões ativos.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de cartões ativos
        """
        return self.get_all_credit_cards(is_active=True)

    def get_cards_by_flag(self, flag: str) -> List[Dict[str, Any]]:
        """
        Obtém cartões filtrados por bandeira.

        Parameters
        ----------
        flag : str
            Bandeira do cartão (MSC, VSA, ELO, etc.)

        Returns
        -------
        List[Dict[str, Any]]
            Lista de cartões da bandeira
        """
        return self.get_all_credit_cards(flag=flag)

    def _process_card_data(
            self,
            card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados do cartão antes do envio para a API.

        Parameters
        ----------
        card_data : Dict[str, Any]
            Dados brutos do cartão

        Returns
        -------
        Dict[str, Any]
            Dados processados
        """
        processed_data = card_data.copy()

        # Converte validation_date para string se necessário
        if 'validation_date' in processed_data:
            processed_data['validation_date'] = format_date_for_api(
                processed_data['validation_date']
            )

        # Converte valores monetários para string se necessário
        for field in ['credit_limit', 'max_limit']:
            if field in processed_data and isinstance(
                processed_data[field], (int, float)
            ):
                processed_data[field] = str(processed_data[field])

        # Garante que is_active seja boolean
        if 'is_active' in processed_data:
            processed_data['is_active'] = bool(processed_data['is_active'])

        return processed_data

    def validate_card_data(self, card_data: Dict[str, Any]) -> List[str]:
        """
        Valida os dados de um cartão antes do envio para a API.

        Parameters
        ----------
        card_data : Dict[str, Any]
            Dados do cartão para validação

        Returns
        -------
        List[str]
            Lista de mensagens de erro. Lista vazia se válido.
        """
        errors = []

        # Campo obrigatório: name
        if not card_data.get('name', '').strip():
            errors.append("Nome do cartão é obrigatório")

        # Campo obrigatório: on_card_name
        if not card_data.get('on_card_name', '').strip():
            errors.append("Nome impresso no cartão é obrigatório")

        # Campo obrigatório: flag
        valid_flags = ['MSC', 'VSA', 'ELO', 'EXP', 'HCD']
        flag = card_data.get('flag', '').strip()
        if not flag:
            errors.append("Bandeira do cartão é obrigatória")
        elif flag not in valid_flags:
            errors.append(
                f"Bandeira inválida. Opções: {', '.join(valid_flags)}"
            )

        # Campo obrigatório: validation_date
        if not card_data.get('validation_date'):
            errors.append("Data de validade é obrigatória")
        else:
            # Verifica se a data é posterior à atual
            try:
                if isinstance(card_data['validation_date'], str):
                    validation_date = date.fromisoformat(
                        card_data['validation_date']
                    )
                else:
                    validation_date = card_data['validation_date']

                if validation_date <= date.today():
                    errors.append(
                        "Data de validade deve ser posterior à data atual"
                    )
            except (ValueError, TypeError):
                errors.append("Data de validade inválida")

        # Campo obrigatório: security_code
        security_code = card_data.get('security_code', '').strip()
        if not security_code:
            errors.append("Código de segurança é obrigatório")
        elif not security_code.isdigit() or len(security_code) not in [3, 4]:
            errors.append("Código de segurança deve ter 3 ou 4 dígitos")

        # Campo obrigatório: associated_account
        if not card_data.get('associated_account'):
            errors.append("Conta associada é obrigatória")

        # Validação de limites
        credit_limit = card_data.get('credit_limit')
        max_limit = card_data.get('max_limit')

        if credit_limit:
            try:
                credit_limit_float = float(credit_limit)
                if credit_limit_float < 0:
                    errors.append("Limite de crédito deve ser positivo")
            except (ValueError, TypeError):
                errors.append("Limite de crédito deve ser um número válido")

        if max_limit:
            try:
                max_limit_float = float(max_limit)
                if max_limit_float < 0:
                    errors.append("Limite máximo deve ser positivo")

                # Verifica se credit_limit não é maior que max_limit
                if credit_limit:
                    try:
                        if float(credit_limit) > max_limit_float:
                            errors.append(
                                "Limite de crédito não pode ser maior que "
                                "o limite máximo"
                            )
                    except (ValueError, TypeError):
                        pass

            except (ValueError, TypeError):
                errors.append("Limite máximo deve ser um número válido")

        return errors


# Instância global do serviço de cartões de crédito
credit_cards_service = CreditCardsService()
