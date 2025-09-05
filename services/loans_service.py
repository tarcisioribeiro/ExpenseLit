"""
Serviço para gerenciamento de empréstimos.

Este módulo implementa todas as operações relacionadas ao
gerenciamento de empréstimos na expenselit-api.
"""

import logging
# from datetime import date  # Não usado
from typing import List, Dict, Any, Optional

from services.api_client import api_client, ApiClientError
from utils.date_utils import format_date_for_api


logger = logging.getLogger(__name__)


class LoansService:
    """
    Serviço para operações com empréstimos.

    Esta classe implementa todas as operações CRUD e consultas
    específicas relacionadas aos empréstimos.
    """

    ENDPOINT = "loans/"

    def get_all_loans(
        self,
        category: Optional[str] = None,
        payed: Optional[bool] = None,
        account_id: Optional[int] = None,
        creditor_id: Optional[int] = None,
        benefited_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém todos os empréstimos com filtros opcionais.

        Parameters
        ----------
        category : str, optional
            Filtrar por categoria
        payed : bool, optional
            Filtrar por status de pagamento
        account_id : int, optional
            Filtrar por ID da conta
        creditor_id : int, optional
            Filtrar por ID do credor
        benefited_id : int, optional
            Filtrar por ID do beneficiário
        date_from : str, optional
            Data inicial no formato YYYY-MM-DD
        date_to : str, optional
            Data final no formato YYYY-MM-DD

        Returns
        -------
        List[Dict[str, Any]]
            Lista de empréstimos

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
                params['account'] = str(account_id)
            if creditor_id:
                params['creditor'] = str(creditor_id)
            if benefited_id:
                params['benefited'] = str(benefited_id)
            if date_from:
                params['date_from'] = date_from
            if date_to:
                params['date_to'] = date_to

            response = api_client.get(self.ENDPOINT, params=params)

            # A API pode retornar uma lista direta ou um objeto com 'results'
            if isinstance(response, dict) and 'results' in response:
                return response['results']
            elif isinstance(response, list):
                return response
            else:
                return []

        except ApiClientError as e:
            logger.error(f"Erro ao buscar empréstimos: {e}")
            raise

    def get_loan_by_id(self, loan_id: int) -> Dict[str, Any]:
        """
        Obtém um empréstimo específico pelo ID.

        Parameters
        ----------
        loan_id : int
            ID do empréstimo

        Returns
        -------
        Dict[str, Any]
            Dados do empréstimo

        Raises
        ------
        ApiClientError
            Se o empréstimo não for encontrado ou houver erro na API
        """
        try:
            endpoint = f"{self.ENDPOINT}{loan_id}/"
            return api_client.get(endpoint)
        except ApiClientError as e:
            logger.error(f"Erro ao buscar empréstimo {loan_id}: {e}")
            raise

    def create_loan(self, loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo empréstimo.

        Parameters
        ----------
        loan_data : Dict[str, Any]
            Dados do empréstimo a ser criado
            Campos obrigatórios:
                description, value, date, horary, category,
                account, creditor, benefited
            Campos opcionais:
                payed_value, payed, interest_rate, installments,
                due_date, payment_frequency, late_fee, notes

        Returns
        -------
        Dict[str, Any]
            Dados do empréstimo criado

        Raises
        ------
        ApiClientError
            Se houver erro na validação ou criação

        Examples
        --------
        >>> loan_data = {
        ...     "description": "Empréstimo para reforma",
        ...     "value": "5000.00",
        ...     "date": "2024-01-10",
        ...     "horary": "09:00:00",
        ...     "category": "personal",
        ...     "account": 1,
        ...     "creditor": 1,
        ...     "benefited": 2
        ... }
        >>> loan = loans_service.create_loan(loan_data)
        """
        try:
            # Processa dados antes do envio
            processed_data = self._process_loan_data(loan_data)
            return api_client.post(self.ENDPOINT, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao criar empréstimo: {e}")
            raise

    def update_loan(
            self,
            loan_id: int,
            loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um empréstimo existente.

        Parameters
        ----------
        loan_id : int
            ID do empréstimo a ser atualizado
        loan_data : Dict[str, Any]
            Novos dados do empréstimo

        Returns
        -------
        Dict[str, Any]
            Dados do empréstimo atualizado

        Raises
        ------
        ApiClientError
            Se o empréstimo não for encontrado ou houver erro na validação
        """
        try:
            processed_data = self._process_loan_data(loan_data)
            endpoint = f"{self.ENDPOINT}{loan_id}/"
            return api_client.put(endpoint, processed_data)
        except ApiClientError as e:
            logger.error(f"Erro ao atualizar empréstimo {loan_id}: {e}")
            raise

    def delete_loan(self, loan_id: int) -> None:
        """
        Exclui um empréstimo.

        Parameters
        ----------
        loan_id : int
            ID do empréstimo a ser excluído

        Raises
        ------
        ApiClientError
            Se o empréstimo não for encontrado ou houver erro na exclusão
        """
        try:
            endpoint = f"{self.ENDPOINT}{loan_id}/"
            api_client.delete(endpoint)
            logger.info(f"Empréstimo {loan_id} excluído com sucesso")
        except ApiClientError as e:
            logger.error(f"Erro ao excluir empréstimo {loan_id}: {e}")
            raise

    def get_loans_as_creditor(self, creditor_id: int) -> List[Dict[str, Any]]:
        """
        Obtém empréstimos onde um membro é credor.

        Parameters
        ----------
        creditor_id : int
            ID do membro credor

        Returns
        -------
        List[Dict[str, Any]]
            Lista de empréstimos como credor
        """
        return self.get_all_loans(creditor_id=creditor_id)

    def get_loans_as_benefited(
            self,
            benefited_id: int) -> List[Dict[str, Any]]:
        """
        Obtém empréstimos onde um membro é beneficiário.

        Parameters
        ----------
        benefited_id : int
            ID do membro beneficiário

        Returns
        -------
        List[Dict[str, Any]]
            Lista de empréstimos como beneficiário
        """
        return self.get_all_loans(benefited_id=benefited_id)

    def get_pending_loans(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os empréstimos não pagos.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de empréstimos não pagos
        """
        return self.get_all_loans(payed=False)

    def get_paid_loans(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os empréstimos pagos.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de empréstimos pagos
        """
        return self.get_all_loans(payed=True)

    def get_loans_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Obtém empréstimos filtrados por categoria.

        Parameters
        ----------
        category : str
            Categoria dos empréstimos

        Returns
        -------
        List[Dict[str, Any]]
            Lista de empréstimos da categoria
        """
        return self.get_all_loans(category=category)

    def _process_loan_data(
            self,
            loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados do empréstimo antes do envio para a API.

        Parameters
        ----------
        loan_data : Dict[str, Any]
            Dados brutos do empréstimo

        Returns
        -------
        Dict[str, Any]
            Dados processados
        """
        processed_data = loan_data.copy()

        # Converte date para string se necessário
        if 'date' in processed_data:
            processed_data['date'] = format_date_for_api(
                processed_data['date']
            )

        # Converte due_date para string se necessário
        if 'due_date' in processed_data and processed_data['due_date']:
            processed_data['due_date'] = format_date_for_api(
                processed_data['due_date']
            )

        # Converte valores monetários para string se necessário
        for field in ['value', 'payed_value', 'interest_rate', 'late_fee']:
            if field in processed_data and isinstance(
                processed_data[field], (int, float)
            ):
                processed_data[field] = str(processed_data[field])

        # Garante que payed seja boolean
        if 'payed' in processed_data:
            processed_data['payed'] = bool(processed_data['payed'])

        # Converte installments para int se necessário
        if 'installments' in processed_data and processed_data['installments']:
            try:
                processed_data['installments'] = int(
                    processed_data['installments']
                )
            except (ValueError, TypeError):
                pass

        return processed_data

    def validate_loan_data(self, loan_data: Dict[str, Any]) -> List[str]:
        """
        Valida os dados de um empréstimo antes do envio para a API.

        Parameters
        ----------
        loan_data : Dict[str, Any]
            Dados do empréstimo para validação

        Returns
        -------
        List[str]
            Lista de mensagens de erro. Lista vazia se válido.
        """
        errors = []

        # Campo obrigatório: description
        if not loan_data.get('description', '').strip():
            errors.append("Descrição é obrigatória")

        # Campo obrigatório: value
        value = loan_data.get('value')
        if not value:
            errors.append("Valor é obrigatório")
        else:
            try:
                float_value = float(value)
                if float_value <= 0:
                    errors.append("Valor deve ser positivo")
            except (ValueError, TypeError):
                errors.append("Valor deve ser um número válido")

        # Validação de payed_value se fornecido
        payed_value = loan_data.get('payed_value')
        if payed_value:
            try:
                payed_float = float(payed_value)
                if payed_float < 0:
                    errors.append("Valor pago não pode ser negativo")

                # Verifica se payed_value não é maior que value
                if value:
                    try:
                        if payed_float > float(value):
                            errors.append(
                                "Valor pago não pode ser maior que "
                                "o valor total do empréstimo"
                            )
                    except (ValueError, TypeError):
                        pass

            except (ValueError, TypeError):
                errors.append("Valor pago deve ser um número válido")

        # Campo obrigatório: date
        if not loan_data.get('date'):
            errors.append("Data é obrigatória")

        # Campo obrigatório: horary
        if not loan_data.get('horary'):
            errors.append("Horário é obrigatório")

        # Campo obrigatório: category
        if not loan_data.get('category', '').strip():
            errors.append("Categoria é obrigatória")

        # Campo obrigatório: account
        if not loan_data.get('account'):
            errors.append("Conta é obrigatória")

        # Campo obrigatório: creditor
        if not loan_data.get('creditor'):
            errors.append("Credor é obrigatório")

        # Campo obrigatório: benefited
        if not loan_data.get('benefited'):
            errors.append("Beneficiário é obrigatório")

        # Validação: creditor não pode ser igual ao benefited
        creditor = loan_data.get('creditor')
        benefited = loan_data.get('benefited')
        if creditor and benefited and creditor == benefited:
            errors.append("Credor e beneficiário devem ser diferentes")

        # Validação de interest_rate se fornecido
        interest_rate = loan_data.get('interest_rate')
        if interest_rate:
            try:
                rate_float = float(interest_rate)
                if rate_float < 0:
                    errors.append("Taxa de juros não pode ser negativa")
            except (ValueError, TypeError):
                errors.append("Taxa de juros deve ser um número válido")

        # Validação de installments se fornecido
        installments = loan_data.get('installments')
        if installments:
            try:
                installments_int = int(installments)
                if installments_int <= 0:
                    errors.append("Número de parcelas deve ser positivo")
            except (ValueError, TypeError):
                errors.append("Número de parcelas deve ser um número inteiro")

        # Validação de late_fee se fornecido
        late_fee = loan_data.get('late_fee')
        if late_fee:
            try:
                fee_float = float(late_fee)
                if fee_float < 0:
                    errors.append("Taxa de atraso não pode ser negativa")
            except (ValueError, TypeError):
                errors.append("Taxa de atraso deve ser um número válido")

        return errors


# Instância global do serviço de empréstimos
loans_service = LoansService()
