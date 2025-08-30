"""
Serviço para gerenciamento de despesas.

Este módulo implementa todas as operações relacionadas ao
gerenciamento de despesas na expenselit-api.
"""

import logging
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Union

from services.api_client import api_client, ApiClientError
from utils.date_utils import format_date_for_api


logger = logging.getLogger(__name__)


class ExpensesService:
    """
    Serviço para operações com despesas.

    Esta classe implementa todas as operações CRUD e consultas
    específicas relacionadas às despesas.
    """

    ENDPOINT = "expenses/"

    def get_all_expenses(
        self,
        category: Optional[str] = None,
        payed: Optional[bool] = None,
        account_id: Optional[int] = None,
        date_from: Optional[Union[str, date]] = None,
        date_to: Optional[Union[str, date]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém todas as despesas com filtros opcionais.

        Parameters
        ----------
        category : str, optional
            Filtrar por categoria
        payed : bool, optional
            Filtrar por status de pagamento
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
            Lista de despesas

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            params = {}

            if category:
                params['category'] = category
            if payed is not None:
                params['payed'] = str(payed).lower()
            if account_id:
                params['account'] = account_id
            if date_from:
                params['date_from'] = format_date_for_api(date_from)
            if date_to:
                params['date_to'] = format_date_for_api(date_to)
            if limit:
                params['limit'] = limit

            response = api_client.get(self.ENDPOINT, params=params)

            # A API pode retornar uma lista direta ou um objeto com 'results'
            if isinstance(response, dict) and 'results' in response:
                return response['results']
            elif isinstance(response, list):
                return response
            else:
                return []

        except ApiClientError as e:
            logger.error(f"Erro ao buscar despesas: {e}")
            raise

    def get_expense_by_id(self, expense_id: int) -> Dict[str, Any]:
        """
        Obtém uma despesa específica pelo ID.

        Parameters
        ----------
        expense_id : int
            ID da despesa

        Returns
        -------
        Dict[str, Any]
            Dados da despesa

        Raises
        ------
        ApiClientError
            Se a despesa não for encontrada ou houver erro na API
        """
        try:
            endpoint = f"{self.ENDPOINT}{expense_id}/"
            return api_client.get(endpoint)
        except ApiClientError as e:
            logger.error(f"Erro ao buscar despesa {expense_id}: {e}")
            raise

    def create_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova despesa.

        Parameters
        ----------
        expense_data : Dict[str, Any]
            Dados da despesa a ser criada
            Campos obrigatórios:
                description, value, date, horary, category, account
            Campos opcionais: payed

        Returns
        -------
        Dict[str, Any]
            Dados da despesa criada

        Raises
        ------
        ApiClientError
            Se houver erro na validação ou criação

        Examples
        --------
        >>> expense_data = {
        ...     "description": "Supermercado Extra",
        ...     "value": "234.50",
        ...     "date": "2024-01-15",
        ...     "horary": "19:30:00",
        ...     "category": "supermarket",
        ...     "account": 1,
        ...     "payed": True
        ... }
        >>> expense = expenses_service.create_expense(expense_data)
        """
        try:
            # Processa dados antes do envio
            processed_data = self._process_expense_data(expense_data)
            return api_client.post(self.ENDPOINT, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao criar despesa: {e}")
            raise

    def update_expense(
            self,
            expense_id: int,
            expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza uma despesa existente.

        Parameters
        ----------
        expense_id : int
            ID da despesa a ser atualizada
        expense_data : Dict[str, Any]
            Novos dados da despesa

        Returns
        -------
        Dict[str, Any]
            Dados da despesa atualizada

        Raises
        ------
        ApiClientError
            Se a despesa não for encontrada ou houver erro na validação
        """
        try:
            processed_data = self._process_expense_data(expense_data)
            endpoint = f"{self.ENDPOINT}{expense_id}/"
            return api_client.put(endpoint, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao atualizar despesa {expense_id}: {e}")
            raise

    def delete_expense(self, expense_id: int) -> None:
        """
        Exclui uma despesa.

        Parameters
        ----------
        expense_id : int
            ID da despesa a ser excluída

        Raises
        ------
        ApiClientError
            Se a despesa não for encontrada ou houver erro na exclusão
        """
        try:
            endpoint = f"{self.ENDPOINT}{expense_id}/"
            api_client.delete(endpoint)
            logger.info(f"Despesa {expense_id} excluída com sucesso")
        except ApiClientError as e:
            logger.error(f"Erro ao excluir despesa {expense_id}: {e}")
            raise

    def get_expenses_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Obtém despesas filtradas por categoria.

        Parameters
        ----------
        category : str
            Categoria das despesas

        Returns
        -------
        List[Dict[str, Any]]
            Lista de despesas da categoria
        """
        return self.get_all_expenses(category=category)

    def get_unpaid_expenses(self) -> List[Dict[str, Any]]:
        """
        Obtém todas as despesas não pagas.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de despesas não pagas
        """
        return self.get_all_expenses(payed=False)

    def get_expenses_by_date_range(
        self,
        start_date: Union[str, date],
        end_date: Union[str, date]
    ) -> List[Dict[str, Any]]:
        """
        Obtém despesas em um período específico.

        Parameters
        ----------
        start_date : str or date
            Data inicial
        end_date : str or date
            Data final

        Returns
        -------
        List[Dict[str, Any]]
            Lista de despesas no período
        """
        return self.get_all_expenses(date_from=start_date, date_to=end_date)

    def get_monthly_expenses(
            self,
            year: int,
            month: int) -> List[Dict[str, Any]]:
        """
        Obtém despesas de um mês específico.

        Parameters
        ----------
        year : int
            Ano
        month : int
            Mês (1-12)

        Returns
        -------
        List[Dict[str, Any]]
            Lista de despesas do mês
        """
        start_date = date(year, month, 1)

        # Último dia do mês
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        return self.get_expenses_by_date_range(start_date, end_date)

    def calculate_total_expenses(
        self,
        expenses: Optional[List[Dict[str, Any]]] = None,
        payed_only: bool = False
    ) -> float:
        """
        Calcula o total das despesas.

        Parameters
        ----------
        expenses : List[Dict[str, Any]], optional
            Lista de despesas. Se None, busca todas as despesas
        payed_only : bool, optional
            Se deve considerar apenas despesas pagas, por padrão False

        Returns
        -------
        float
            Valor total das despesas
        """
        if expenses is None:
            expenses = self.get_all_expenses(
                payed=payed_only if payed_only else None
            )

        total = 0.0
        for expense in expenses:
            if not payed_only or expense.get('payed', False):
                try:
                    value = float(expense.get('value', 0))
                    total += value
                except (ValueError, TypeError):
                    continue

        return total

    def _process_expense_data(
            self,
            expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados da despesa antes do envio para a API.

        Parameters
        ----------
        expense_data : Dict[str, Any]
            Dados brutos da despesa

        Returns
        -------
        Dict[str, Any]
            Dados processados
        """
        processed_data = expense_data.copy()

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

        # Garante que payed seja boolean
        if 'payed' in processed_data:
            processed_data['payed'] = bool(processed_data['payed'])

        return processed_data

    def validate_expense_data(self, expense_data: Dict[str, Any]) -> List[str]:
        """
        Valida os dados de uma despesa antes do envio para a API.

        Parameters
        ----------
        expense_data : Dict[str, Any]
            Dados da despesa para validação

        Returns
        -------
        List[str]
            Lista de mensagens de erro. Lista vazia se válido.
        """
        errors = []

        # Campo obrigatório: description
        if not expense_data.get('description', '').strip():
            errors.append("Descrição é obrigatória")

        # Campo obrigatório: value
        value = expense_data.get('value')
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
        if not expense_data.get('date'):
            errors.append("Data é obrigatória")

        # Campo obrigatório: horary
        if not expense_data.get('horary'):
            errors.append("Horário é obrigatório")

        # Campo obrigatório: category
        if not expense_data.get('category', '').strip():
            errors.append("Categoria é obrigatória")

        # Campo obrigatório: account
        if not expense_data.get('account'):
            errors.append("Conta é obrigatória")

        return errors


# Instância global do serviço de despesas
expenses_service = ExpensesService()
