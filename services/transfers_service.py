"""
Serviço para gerenciamento de transferências.

Este módulo implementa todas as operações relacionadas ao
gerenciamento de transferências na expenselit-api.
"""

import logging
from datetime import date
from typing import List, Dict, Any, Optional, Union

from services.api_client import api_client, ApiClientError
from utils.date_utils import format_date_for_api

logger = logging.getLogger(__name__)


class TransfersService:
    """
    Serviço para operações com transferências.

    Esta classe implementa todas as operações CRUD e consultas
    específicas relacionadas às transferências entre contas.
    """

    ENDPOINT = "transfers/"

    def get_all_transfers(
        self,
        category: Optional[str] = None,
        transfered: Optional[bool] = None,
        origin_account_id: Optional[int] = None,
        destiny_account_id: Optional[int] = None,
        date_from: Optional[Union[str, date]] = None,
        date_to: Optional[Union[str, date]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém todas as transferências com filtros opcionais.

        Parameters
        ----------
        category : str, optional
            Filtrar por categoria (doc, ted, pix)
        transfered : bool, optional
            Filtrar por status de transferência
        origin_account_id : int, optional
            Filtrar por ID da conta de origem
        destiny_account_id : int, optional
            Filtrar por ID da conta de destino
        date_from : str or date, optional
            Data inicial no formato YYYY-MM-DD
        date_to : str or date, optional
            Data final no formato YYYY-MM-DD
        limit : int, optional
            Limite de resultados

        Returns
        -------
        List[Dict[str, Any]]
            Lista de transferências

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            params = {}

            if category:
                params['category'] = category
            if transfered is not None:
                params['transfered'] = str(transfered).lower()
            if origin_account_id:
                params['origin_account'] = str(origin_account_id)
            if destiny_account_id:
                params['destiny_account'] = str(destiny_account_id)
            if date_from:
                params['date_from'] = format_date_for_api(date_from)
            if date_to:
                params['date_to'] = format_date_for_api(date_to)
            if limit:
                params['limit'] = str(limit)

            logger.info(f"Buscando transferências com parâmetros: {params}")
            response = api_client.get(self.ENDPOINT, params=params)

            # Garantir que o retorno seja uma lista
            if isinstance(response, dict):
                # Se a resposta é um dict, pode conter 'results' ou ser um único item
                if 'results' in response:
                    result = response['results']
                else:
                    result = [response]
            else:
                result = response if isinstance(response, list) else []

            logger.info(f"Encontradas {len(result)} transferências")
            return result

        except ApiClientError as e:
            logger.error(f"Erro ao buscar transferências: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar transferências: {e}")
            raise ApiClientError(f"Erro inesperado: {str(e)}")

    def get_transfer_by_id(self, transfer_id: int) -> Dict[str, Any]:
        """
        Obtém uma transferência específica pelo ID.

        Parameters
        ----------
        transfer_id : int
            ID da transferência

        Returns
        -------
        Dict[str, Any]
            Dados da transferência

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            logger.info(f"Buscando transferência com ID: {transfer_id}")
            response = api_client.get(f"{self.ENDPOINT}{transfer_id}/")
            logger.info(f"Transferência encontrada: {response.get('id')}")
            return response

        except ApiClientError as e:
            logger.error(f"Erro ao buscar transferência {transfer_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar transferência: {e}")
            raise ApiClientError(f"Erro inesperado: {str(e)}")

    def create_transfer(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova transferência.

        Parameters
        ----------
        transfer_data : Dict[str, Any]
            Dados da transferência a ser criada

        Returns
        -------
        Dict[str, Any]
            Dados da transferência criada

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            logger.info(
                f"Criando nova transferência: "
                f"{transfer_data.get('description')}"
            )
            response = api_client.post(self.ENDPOINT, data=transfer_data)
            logger.info(f"Transferência criada com ID: {response.get('id')}")
            return response

        except ApiClientError as e:
            logger.error(f"Erro ao criar transferência: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar transferência: {e}")
            raise ApiClientError(f"Erro inesperado: {str(e)}")

    def update_transfer(
        self,
        transfer_id: int,
        transfer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza uma transferência existente.

        Parameters
        ----------
        transfer_id : int
            ID da transferência a ser atualizada
        transfer_data : Dict[str, Any]
            Dados atualizados da transferência

        Returns
        -------
        Dict[str, Any]
            Dados da transferência atualizada

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            logger.info(f"Atualizando transferência ID: {transfer_id}")
            response = api_client.put(
                f"{self.ENDPOINT}{transfer_id}/",
                data=transfer_data
            )
            logger.info(f"Transferência {transfer_id} atualizada com sucesso")
            return response

        except ApiClientError as e:
            logger.error(f"Erro ao atualizar transferência {transfer_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar transferência: {e}")
            raise ApiClientError(f"Erro inesperado: {str(e)}")

    def delete_transfer(self, transfer_id: int) -> bool:
        """
        Exclui uma transferência.

        Parameters
        ----------
        transfer_id : int
            ID da transferência a ser excluída

        Returns
        -------
        bool
            True se a exclusão foi bem-sucedida

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            logger.info(f"Excluindo transferência ID: {transfer_id}")
            api_client.delete(f"{self.ENDPOINT}{transfer_id}/")
            logger.info(f"Transferência {transfer_id} excluída com sucesso")
            return True

        except ApiClientError as e:
            logger.error(f"Erro ao excluir transferência {transfer_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao excluir transferência: {e}")
            raise ApiClientError(f"Erro inesperado: {str(e)}")

    def validate_transfer_data(
            self, transfer_data: Dict[str, Any]) -> List[str]:
        """
        Valida os dados de uma transferência.

        Parameters
        ----------
        transfer_data : Dict[str, Any]
            Dados da transferência a serem validados

        Returns
        -------
        List[str]
            Lista de erros de validação (vazia se válidos)
        """
        errors = []

        # Validações obrigatórias
        required_fields = [
            'description', 'value', 'date', 'horary',
            'category', 'origin_account', 'destiny_account'
        ]

        for field in required_fields:
            if not transfer_data.get(field):
                field_names = {
                    'description': 'Descrição',
                    'value': 'Valor',
                    'date': 'Data',
                    'horary': 'Horário',
                    'category': 'Categoria',
                    'origin_account': 'Conta de origem',
                    'destiny_account': 'Conta de destino'
                }
                errors.append(f"{field_names.get(field, field)} é obrigatório")

        # Validação de valor
        try:
            value = float(transfer_data.get('value', 0))
            if value <= 0:
                errors.append("Valor deve ser maior que zero")
        except (ValueError, TypeError):
            errors.append("Valor deve ser um número válido")

        # Validação de contas diferentes
        origin = transfer_data.get('origin_account')
        destiny = transfer_data.get('destiny_account')
        if origin and destiny and origin == destiny:
            errors.append(
                "Conta de origem deve ser diferente da conta de destino")

        return errors


# Instância global do serviço
transfers_service = TransfersService()
