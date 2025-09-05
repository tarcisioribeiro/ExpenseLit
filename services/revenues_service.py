"""
Serviço para gerenciamento de receitas.

Este módulo implementa todas as operações relacionadas ao
gerenciamento de receitas na expenselit-api.
"""

import logging
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Union

from services.api_client import api_client, ApiClientError
from utils.date_utils import format_date_for_api


logger = logging.getLogger(__name__)


class RevenuesService:
    """
    Serviço para operações com receitas.

    Esta classe implementa todas as operações CRUD e consultas
    específicas relacionadas às receitas.
    """

    ENDPOINT = "revenues/"

    def get_all_revenues(
        self,
        category: Optional[str] = None,
        received: Optional[bool] = None,
        account_id: Optional[int] = None,
        date_from: Optional[Union[str, date]] = None,
        date_to: Optional[Union[str, date]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém todas as receitas com filtros opcionais.

        Parameters
        ----------
        category : str, optional
            Filtrar por categoria
        received : bool, optional
            Filtrar por status de recebimento
        account_id : int, optional
            Filtrar por ID da conta
        date_from : str or date, optional
            Data inicial no formato YYYY-MM-DD
        date_to : str or date, optional
            Data final no formato YYYY-MM-DD
        limit : int, optional
            Limite de resultados

        Returns
        -------
        List[Dict[str, Any]]
            Lista de receitas

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            params = {}

            if category:
                params['category'] = category
            if received is not None:
                params['received'] = str(received).lower()
            if account_id:
                params['account'] = str(account_id)
            if date_from:
                params['date_from'] = format_date_for_api(date_from)
            if date_to:
                params['date_to'] = format_date_for_api(date_to)
            if limit:
                params['limit'] = str(limit)

            response = api_client.get(self.ENDPOINT, params=params)

            # A API pode retornar uma lista direta ou um objeto com 'results'
            if isinstance(response, dict) and 'results' in response:
                return response['results']
            elif isinstance(response, list):
                return response
            else:
                return []

        except ApiClientError as e:
            logger.error(f"Erro ao buscar receitas: {e}")
            raise

    def get_revenue_by_id(self, revenue_id: int) -> Dict[str, Any]:
        """
        Obtém uma receita específica pelo ID.

        Parameters
        ----------
        revenue_id : int
            ID da receita

        Returns
        -------
        Dict[str, Any]
            Dados da receita

        Raises
        ------
        ApiClientError
            Se a receita não for encontrada ou houver erro na API
        """
        try:
            endpoint = f"{self.ENDPOINT}{revenue_id}/"
            return api_client.get(endpoint)
        except ApiClientError as e:
            logger.error(f"Erro ao buscar receita {revenue_id}: {e}")
            raise

    def create_revenue(self, revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova receita.

        Parameters
        ----------
        revenue_data : Dict[str, Any]
            Dados da receita a ser criada
            Campos obrigatórios:
                description, value, date, horary, category, account
            Campos opcionais: received

        Returns
        -------
        Dict[str, Any]
            Dados da receita criada

        Raises
        ------
        ApiClientError
            Se houver erro na validação ou criação

        Examples
        --------
        >>> revenue_data = {
        ...     "description": "Salário Janeiro",
        ...     "value": "4500.00",
        ...     "date": "2024-01-05",
        ...     "horary": "08:00:00",
        ...     "category": "salary",
        ...     "account": 1,
        ...     "received": True
        ... }
        >>> revenue = revenues_service.create_revenue(revenue_data)
        """
        try:
            # Processa dados antes do envio
            processed_data = self._process_revenue_data(revenue_data)
            return api_client.post(self.ENDPOINT, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao criar receita: {e}")
            raise

    def update_revenue(
            self,
            revenue_id: int,
            revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza uma receita existente.

        Parameters
        ----------
        revenue_id : int
            ID da receita a ser atualizada
        revenue_data : Dict[str, Any]
            Novos dados da receita

        Returns
        -------
        Dict[str, Any]
            Dados da receita atualizada

        Raises
        ------
        ApiClientError
            Se a receita não for encontrada ou houver erro na validação
        """
        try:
            processed_data = self._process_revenue_data(revenue_data)
            endpoint = f"{self.ENDPOINT}{revenue_id}/"
            return api_client.put(endpoint, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao atualizar receita {revenue_id}: {e}")
            raise

    def delete_revenue(self, revenue_id: int) -> None:
        """
        Exclui uma receita.

        Parameters
        ----------
        revenue_id : int
            ID da receita a ser excluída

        Raises
        ------
        ApiClientError
            Se a receita não for encontrada ou houver erro na exclusão
        """
        try:
            endpoint = f"{self.ENDPOINT}{revenue_id}/"
            api_client.delete(endpoint)
            logger.info(f"Receita {revenue_id} excluída com sucesso")
        except ApiClientError as e:
            logger.error(f"Erro ao excluir receita {revenue_id}: {e}")
            raise

    def get_revenues_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Obtém receitas filtradas por categoria.

        Parameters
        ----------
        category : str
            Categoria das receitas

        Returns
        -------
        List[Dict[str, Any]]
            Lista de receitas da categoria
        """
        return self.get_all_revenues(category=category)

    def get_pending_revenues(self) -> List[Dict[str, Any]]:
        """
        Obtém todas as receitas não recebidas.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de receitas não recebidas
        """
        return self.get_all_revenues(received=False)

    def get_revenues_by_date_range(
        self,
        start_date: Union[str, date],
        end_date: Union[str, date]
    ) -> List[Dict[str, Any]]:
        """
        Obtém receitas em um período específico.

        Parameters
        ----------
        start_date : str or date
            Data inicial
        end_date : str or date
            Data final

        Returns
        -------
        List[Dict[str, Any]]
            Lista de receitas no período
        """
        return self.get_all_revenues(date_from=start_date, date_to=end_date)

    def get_monthly_revenues(
            self,
            year: int,
            month: int) -> List[Dict[str, Any]]:
        """
        Obtém receitas de um mês específico.

        Parameters
        ----------
        year : int
            Ano
        month : int
            Mês (1-12)

        Returns
        -------
        List[Dict[str, Any]]
            Lista de receitas do mês
        """
        start_date = date(year, month, 1)

        # Último dia do mês
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        return self.get_revenues_by_date_range(start_date, end_date)

    def calculate_total_revenues(
        self,
        revenues: Optional[List[Dict[str, Any]]] = None,
        received_only: bool = False
    ) -> float:
        """
        Calcula o total das receitas.

        Parameters
        ----------
        revenues : List[Dict[str, Any]], optional
            Lista de receitas. Se None, busca todas as receitas
        received_only : bool, optional
            Se deve considerar apenas receitas recebidas, por padrão False

        Returns
        -------
        float
            Valor total das receitas
        """
        if revenues is None:
            revenues = self.get_all_revenues(
                received=received_only if received_only else None
            )

        total = 0.0
        for revenue in revenues:
            if not received_only or revenue.get('received', False):
                try:
                    value = float(revenue.get('value', 0))
                    total += value
                except (ValueError, TypeError):
                    continue

        return total

    def get_salary_revenues(self) -> List[Dict[str, Any]]:
        """
        Obtém receitas de salário.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de receitas de salário
        """
        return self.get_revenues_by_category("salary")

    def get_cashback_revenues(self) -> List[Dict[str, Any]]:
        """
        Obtém receitas de cashback.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de receitas de cashback
        """
        return self.get_revenues_by_category("cashback")

    def _process_revenue_data(
            self,
            revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados da receita antes do envio para a API.

        Parameters
        ----------
        revenue_data : Dict[str, Any]
            Dados brutos da receita

        Returns
        -------
        Dict[str, Any]
            Dados processados
        """
        processed_data = revenue_data.copy()

        # Converte date para string se necessário
        if 'date' in processed_data:
            processed_data['date'] = format_date_for_api(
                processed_data['date']
            )

        # Converte value para string se necessário
        if 'value' in processed_data and isinstance(
            processed_data['value'], (int, float)
        ):
            processed_data['value'] = str(processed_data['value'])

        # Garante que received seja boolean
        if 'received' in processed_data:
            processed_data['received'] = bool(processed_data['received'])

        return processed_data

    def validate_revenue_data(self, revenue_data: Dict[str, Any]) -> List[str]:
        """
        Valida os dados de uma receita antes do envio para a API.

        Parameters
        ----------
        revenue_data : Dict[str, Any]
            Dados da receita para validação

        Returns
        -------
        List[str]
            Lista de mensagens de erro. Lista vazia se válido.
        """
        errors = []

        # Campo obrigatório: description
        if not revenue_data.get('description', '').strip():
            errors.append("Descrição é obrigatória")

        # Campo obrigatório: value
        value = revenue_data.get('value')
        if not value:
            errors.append("Valor é obrigatório")
        else:
            try:
                float_value = float(value)
                if float_value <= 0:
                    errors.append("Valor deve ser positivo")
            except (ValueError, TypeError):
                errors.append("Valor deve ser um número válido")

        # Campo obrigatório: date
        if not revenue_data.get('date'):
            errors.append("Data é obrigatória")

        # Campo obrigatório: horary
        if not revenue_data.get('horary'):
            errors.append("Horário é obrigatório")

        # Campo obrigatório: category
        if not revenue_data.get('category', '').strip():
            errors.append("Categoria é obrigatória")

        # Campo obrigatório: account
        if not revenue_data.get('account'):
            errors.append("Conta é obrigatória")

        return errors


# Instância global do serviço de receitas
revenues_service = RevenuesService()
