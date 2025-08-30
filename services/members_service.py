"""
Serviço para gerenciamento de membros.

Este módulo implementa todas as operações relacionadas ao
gerenciamento de membros (usuários, credores, beneficiários) na expenselit-api.
"""

import logging
from typing import List, Dict, Any, Optional

from services.api_client import api_client, ApiClientError


logger = logging.getLogger(__name__)


class MembersService:
    """
    Serviço para operações com membros.

    Esta classe implementa todas as operações CRUD e consultas
    específicas relacionadas aos membros do sistema.
    """

    ENDPOINT = "members/"

    def get_all_members(
        self,
        is_user: Optional[bool] = None,
        is_creditor: Optional[bool] = None,
        is_benefited: Optional[bool] = None,
        active: Optional[bool] = True
    ) -> List[Dict[str, Any]]:
        """
        Obtém todos os membros com filtros opcionais.

        Parameters
        ----------
        is_user : bool, optional
            Filtrar por usuários do sistema
        is_creditor : bool, optional
            Filtrar por credores
        is_benefited : bool, optional
            Filtrar por beneficiários
        active : bool, optional
            Filtrar por status ativo, por padrão True

        Returns
        -------
        List[Dict[str, Any]]
            Lista de membros

        Raises
        ------
        ApiClientError
            Se houver erro na comunicação com a API
        """
        try:
            params = {}

            if is_user is not None:
                params['is_user'] = str(is_user).lower()
            if is_creditor is not None:
                params['is_creditor'] = str(is_creditor).lower()
            if is_benefited is not None:
                params['is_benefited'] = str(is_benefited).lower()
            if active is not None:
                params['active'] = str(active).lower()

            response = api_client.get(self.ENDPOINT, params=params)

            # A API pode retornar uma lista direta ou um objeto com 'results'
            if isinstance(response, dict) and 'results' in response:
                return response['results']
            elif isinstance(response, list):
                return response
            else:
                return []

        except ApiClientError as e:
            logger.error(f"Erro ao buscar membros: {e}")
            raise

    def get_member_by_id(self, member_id: int) -> Dict[str, Any]:
        """
        Obtém um membro específico pelo ID.

        Parameters
        ----------
        member_id : int
            ID do membro

        Returns
        -------
        Dict[str, Any]
            Dados do membro

        Raises
        ------
        ApiClientError
            Se o membro não for encontrado ou houver erro na API
        """
        try:
            endpoint = f"{self.ENDPOINT}{member_id}/"
            return api_client.get(endpoint)
        except ApiClientError as e:
            logger.error(f"Erro ao buscar membro {member_id}: {e}")
            raise

    def create_member(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo membro.

        Parameters
        ----------
        member_data : Dict[str, Any]
            Dados do membro a ser criado
            Campos obrigatórios: name, document, phone, sex
            Campos opcionais: email, is_user, is_creditor, is_benefited, active

        Returns
        -------
        Dict[str, Any]
            Dados do membro criado

        Raises
        ------
        ApiClientError
            Se houver erro na validação ou criação

        Examples
        --------
        >>> member_data = {
        ...     "name": "João da Silva",
        ...     "document": "12345678901",
        ...     "phone": "11999887766",
        ...     "email": "joao.silva@email.com",
        ...     "sex": "M",
        ...     "is_user": True,
        ...     "is_creditor": True,
        ...     "is_benefited": True,
        ...     "active": True
        ... }
        >>> member = members_service.create_member(member_data)
        """
        try:
            return api_client.post(self.ENDPOINT, member_data)
        except ApiClientError as e:
            logger.error(f"Erro ao criar membro: {e}")
            raise

    def update_member(
            self,
            member_id: int,
            member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um membro existente.

        Parameters
        ----------
        member_id : int
            ID do membro a ser atualizado
        member_data : Dict[str, Any]
            Novos dados do membro

        Returns
        -------
        Dict[str, Any]
            Dados do membro atualizado

        Raises
        ------
        ApiClientError
            Se o membro não for encontrado ou houver erro na validação
        """
        try:
            endpoint = f"{self.ENDPOINT}{member_id}/"
            return api_client.put(endpoint, member_data)
        except ApiClientError as e:
            logger.error(f"Erro ao atualizar membro {member_id}: {e}")
            raise

    def delete_member(self, member_id: int) -> None:
        """
        Exclui um membro.

        Parameters
        ----------
        member_id : int
            ID do membro a ser excluído

        Raises
        ------
        ApiClientError
            Se o membro não for encontrado ou houver erro na exclusão
        """
        try:
            endpoint = f"{self.ENDPOINT}{member_id}/"
            api_client.delete(endpoint)
            logger.info(f"Membro {member_id} excluído com sucesso")
        except ApiClientError as e:
            logger.error(f"Erro ao excluir membro {member_id}: {e}")
            raise

    def get_users(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os usuários do sistema.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de usuários
        """
        return self.get_all_members(is_user=True)

    def get_creditors(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os credores.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de credores
        """
        return self.get_all_members(is_creditor=True)

    def get_benefited(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os beneficiários.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de beneficiários
        """
        return self.get_all_members(is_benefited=True)

    def get_creditors_for_select(self) -> Dict[str, int]:
        """
        Obtém credores formatados para componentes de seleção.

        Returns
        -------
        Dict[str, int]
            Dicionário com nome do credor como chave e ID como valor

        Examples
        --------
        >>> creditors = members_service.get_creditors_for_select()
        >>> print(creditors)
        {'João da Silva': 1, 'Maria Santos': 2}
        """
        try:
            creditors = self.get_creditors()
            return {member['name']: member['id'] for member in creditors}
        except ApiClientError as e:
            logger.error(f"Erro ao buscar credores para seleção: {e}")
            return {}

    def get_benefited_for_select(self) -> Dict[str, int]:
        """
        Obtém beneficiários formatados para componentes de seleção.

        Returns
        -------
        Dict[str, int]
            Dicionário com nome do beneficiário como chave e ID como valor
        """
        try:
            benefited = self.get_benefited()
            return {member['name']: member['id'] for member in benefited}
        except ApiClientError as e:
            logger.error(f"Erro ao buscar beneficiários para seleção: {e}")
            return {}

    def search_by_document(self, document: str) -> Optional[Dict[str, Any]]:
        """
        Busca um membro pelo documento.

        Parameters
        ----------
        document : str
            Número do documento (CPF/CNPJ)

        Returns
        -------
        Optional[Dict[str, Any]]
            Dados do membro encontrado ou None se não encontrado
        """
        try:
            members = self.get_all_members()
            for member in members:
                if member.get('document') == document:
                    return member
            return None
        except ApiClientError as e:
            logger.error(f"Erro ao buscar membro por documento: {e}")
            return None

    def validate_member_data(self, member_data: Dict[str, Any]) -> List[str]:
        """
        Valida os dados de um membro antes do envio para a API.

        Parameters
        ----------
        member_data : Dict[str, Any]
            Dados do membro para validação

        Returns
        -------
        List[str]
            Lista de mensagens de erro. Lista vazia se válido.
        """
        errors = []

        # Campo obrigatório: name
        if not member_data.get('name', '').strip():
            errors.append("Nome é obrigatório")

        # Campo obrigatório: document
        document = member_data.get('document', '').strip()
        if not document:
            errors.append("Documento é obrigatório")
        elif not self._validate_document(document):
            errors.append("Documento deve ter 11 ou 14 dígitos numéricos")

        # Campo obrigatório: phone
        phone = member_data.get('phone', '').strip()
        if not phone:
            errors.append("Telefone é obrigatório")
        elif not self._validate_phone(phone):
            errors.append("Telefone deve ter entre 10 e 15 dígitos")

        # Campo obrigatório: sex
        sex = member_data.get('sex', '').strip().upper()
        if not sex:
            errors.append("Sexo é obrigatório")
        elif sex not in ['M', 'F']:
            errors.append("Sexo deve ser 'M' ou 'F'")

        # Validação de email se fornecido
        email = member_data.get('email', '').strip()
        if email and not self._validate_email(email):
            errors.append("Email deve ter formato válido")

        # Validação de pelo menos um flag verdadeiro
        is_user = member_data.get('is_user', False)
        is_creditor = member_data.get('is_creditor', False)
        is_benefited = member_data.get('is_benefited', False)

        if not any([is_user, is_creditor, is_benefited]):
            errors.append(
                "Pelo menos uma função deve ser marcada."
            )

        return errors

    def _validate_document(self, document: str) -> bool:
        """
        Valida formato do documento (CPF/CNPJ).

        Parameters
        ----------
        document : str
            Número do documento

        Returns
        -------
        bool
            True se válido
        """
        # Remove caracteres não numéricos
        clean_document = ''.join(filter(str.isdigit, document))
        # CPF: 11 dígitos, CNPJ: 14 dígitos
        return len(clean_document) in [11, 14]

    def _validate_phone(self, phone: str) -> bool:
        """
        Valida formato do telefone.

        Parameters
        ----------
        phone : str
            Número do telefone

        Returns
        -------
        bool
            True se válido
        """
        # Remove caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))
        # Telefone deve ter entre 10 e 15 dígitos
        return 10 <= len(clean_phone) <= 15

    def _validate_email(self, email: str) -> bool:
        """
        Valida formato do email.

        Parameters
        ----------
        email : str
            Endereço de email

        Returns
        -------
        bool
            True se válido
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# Instância global do serviço de membros
members_service = MembersService()
