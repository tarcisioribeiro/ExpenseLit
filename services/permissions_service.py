"""
Serviço de permissões do ExpenseLit.

Este módulo implementa validações de permissões CRUD seguindo
o padrão do CodexDB para controle de acesso das funcionalidades.
"""

import logging
from typing import List, Dict, Any, Optional
import streamlit as st

logger = logging.getLogger(__name__)


class PermissionsService:
    """
    Serviço de validação de permissões CRUD.

    Segue o padrão do CodexDB para gerenciar permissões de usuário
    em todas as operações do sistema.
    """

    # Mapeamento de permissões Django para operações CRUD
    PERMISSIONS_MAP = {
        # Members
        'members.add_member': 'create',
        'members.view_member': 'read',
        'members.change_member': 'update',
        'members.delete_member': 'delete',

        # Accounts
        'accounts.add_account': 'create',
        'accounts.view_account': 'read',
        'accounts.change_account': 'update',
        'accounts.delete_account': 'delete',

        # Expenses
        'expenses.add_expense': 'create',
        'expenses.view_expense': 'read',
        'expenses.change_expense': 'update',
        'expenses.delete_expense': 'delete',

        # Credit Cards
        'credit_cards.add_creditcard': 'create',
        'credit_cards.view_creditcard': 'read',
        'credit_cards.change_creditcard': 'update',
        'credit_cards.delete_creditcard': 'delete',

        # Loans
        'loans.add_loan': 'create',
        'loans.view_loan': 'read',
        'loans.change_loan': 'update',
        'loans.delete_loan': 'delete',

        # Transfers
        'transfers.add_transfer': 'create',
        'transfers.view_transfer': 'read',
        'transfers.change_transfer': 'update',
        'transfers.delete_transfer': 'delete',

        # Revenues
        'revenues.add_revenue': 'create',
        'revenues.view_revenue': 'read',
        'revenues.change_revenue': 'update',
        'revenues.delete_revenue': 'delete',
    }

    @staticmethod
    def get_user_permissions() -> Optional[Dict[str, Any]]:
        """
        Obtém as permissões do usuário atual do session_state.

        Returns
        -------
        Dict[str, Any] or None
            Dicionário com as permissões do usuário ou None se não encontrado
        """
        return st.session_state.get('user_permissions')

    @staticmethod
    def is_superuser() -> bool:
        """
        Verifica se o usuário atual é superusuário.

        Returns
        -------
        bool
            True se o usuário for superusuário
        """
        user_permissions = PermissionsService.get_user_permissions()
        if not user_permissions:
            return False
        return user_permissions.get('is_superuser', False)

    @staticmethod
    def is_member_group() -> bool:
        """
        Verifica se o usuário pertence ao grupo 'members'.

        Returns
        -------
        bool
            True se o usuário pertence ao grupo 'members'
        """
        user_permissions = PermissionsService.get_user_permissions()
        if not user_permissions:
            return False

        # Verifica diferentes formatos possíveis de grupos na resposta da API
        user_groups = user_permissions.get('groups', [])

        # Verifica se o grupo 'members' está presente
        # Suporta tanto strings quanto dicionários com 'name'
        for group in user_groups:
            if isinstance(group, str):
                if group.lower() in ['members', 'members']:
                    return True
            elif isinstance(group, dict):
                group_name = group.get('name', '')
                if group_name.lower() in ['members', 'members']:
                    return True

        # Fallback: se não encontrou grupos mas tem permissões,
        # assume que está no grupo members (para compatibilidade)
        if user_permissions.get('permissions') and not user_groups:
            return True

        return False

    @staticmethod
    def get_app_permissions(app_name: str) -> List[str]:
        """
        Obtém as permissões do usuário para uma aplicação específica.

        Agora inclui verificação de pertencimento ao grupo 'members'.

        Parameters
        ----------
        app_name : str
            Nome da aplicação (members, accounts, expenses, etc.)

        Returns
        -------
        List[str]
            Lista de permissões CRUD para a aplicação
        """
        user_permissions = PermissionsService.get_user_permissions()
        if not user_permissions:
            return []

        # Superusuários têm acesso total
        if PermissionsService.is_superuser():
            return ['create', 'read', 'update', 'delete']

        # Verifica se o usuário pertence ao grupo 'members'
        if not PermissionsService.is_member_group():
            logger.warning(
                "Usuário não pertence ao grupo 'members'. "
                "Acesso negado às funcionalidades."
            )
            return []

        user_perms_list = user_permissions.get('permissions', [])
        app_permissions = []

        # Se não há permissões específicas mas está no grupo members,
        # concede permissões básicas
        if not user_perms_list:
            # Usuários do grupo members têm permissões básicas
            return ['read', 'create']

        for perm in user_perms_list:
            if perm.startswith(f"{app_name}."):
                crud_operation = PermissionsService.PERMISSIONS_MAP.get(perm)
                if crud_operation and crud_operation not in app_permissions:
                    app_permissions.append(crud_operation)

        # Se não encontrou permissões específicas para esta app mas está no
        # grupo members, concede básicas
        if not app_permissions:
            app_permissions = ['read', 'create']

        return app_permissions

    @staticmethod
    def has_permission(app_name: str, operation: str) -> bool:
        """
        Verifica se o usuário tem permissão para uma operação específica.

        Parameters
        ----------
        app_name : str
            Nome da aplicação (members, accounts, expenses, etc.)
        operation : str
            Operação CRUD (create, read, update, delete)

        Returns
        -------
        bool
            True se o usuário tem a permissão
        """
        app_permissions = PermissionsService.get_app_permissions(app_name)
        return operation in app_permissions

    @staticmethod
    def check_permission(
        app_name: str,
        operation: str,
        show_error: bool = True
    ) -> bool:
        """
        Verifica permissão e opcionalmente mostra erro na interface.

        Parameters
        ----------
        app_name : str
            Nome da aplicação
        operation : str
            Operação CRUD
        show_error : bool, optional
            Se deve mostrar erro na interface, by default True

        Returns
        -------
        bool
            True se tem permissão
        """
        has_perm = PermissionsService.has_permission(app_name, operation)

        if not has_perm and show_error:
            operation_names = {
                'create': 'criar',
                'read': 'visualizar',
                'update': 'editar',
                'delete': 'excluir'
            }

            app_names = {
                'members': 'membros',
                'accounts': 'contas',
                'expenses': 'despesas',
                'credit_cards': 'cartões de crédito',
                'loans': 'empréstimos',
                'transfers': 'transferências',
                'revenues': 'receitas'
            }

            op_name = operation_names.get(operation, operation)
            app_display = app_names.get(app_name, app_name)

            st.error(f"❌ Você não tem permissão para {op_name} {app_display}.")
            st.info("💡 Entre em contato com o administrador do sistema.")

        return has_perm

    @staticmethod
    def require_permission(app_name: str, operation: str):
        """
        Decorator/função para exigir permissão em uma operação.

        Parameters
        ----------
        app_name : str
            Nome da aplicação
        operation : str
            Operação CRUD

        Raises
        ------
        st.stop
            Para a execução se não tiver permissão
        """
        if not PermissionsService.check_permission(app_name, operation):
            st.stop()

    @staticmethod
    def get_permission_summary() -> Dict[str, List[str]]:
        """
        Obtém um resumo de todas as permissões do usuário por app.

        Returns
        -------
        Dict[str, List[str]]
            Dicionário com permissões por aplicação
        """
        apps = [
            'members', 'accounts', 'expenses', 'credit_cards',
            'loans', 'transfers', 'revenues'
        ]

        summary = {}
        for app in apps:
            summary[app] = PermissionsService.get_app_permissions(app)

        return summary

    @staticmethod
    def has_system_access() -> bool:
        """
        Verifica se o usuário tem acesso ao sistema.

        Returns
        -------
        bool
            True se o usuário tem acesso (é superusuário ou está no grupo
            members)
        """
        user_permissions = PermissionsService.get_user_permissions()
        if not user_permissions:
            return False

        # Superusuários sempre têm acesso total
        if PermissionsService.is_superuser():
            return True

        # Verifica se está no grupo members
        if PermissionsService.is_member_group():
            return True

        # Fallback: se tem qualquer permissão específica, assume acesso
        if user_permissions.get('permissions'):
            return True

        return False

    @staticmethod
    def render_permissions_info():
        """Renderiza informações sobre as permissões do usuário atual."""
        user_permissions = PermissionsService.get_user_permissions()
        if not user_permissions:
            st.error("❌ Nenhuma permissão encontrada")
            return

        if not PermissionsService.has_system_access():
            st.error("❌ **Acesso Negado**")
            st.warning(
                "🔒 Você não possui permissões para acessar este sistema. "
                "Entre em contato com o administrador."
            )
            return

        if PermissionsService.is_superuser():
            st.success("🔑 **Superusuário** - Acesso total ao sistema")
            st.info(
                "Você tem permissões completas para todas as funcionalidades."
            )
            return

        if PermissionsService.is_member_group():
            st.success("👥 **Membro** - Acesso às funcionalidades do sistema")

        st.markdown("### 🔐 Suas Permissões")

        summary = PermissionsService.get_permission_summary()

        for app_name, permissions in summary.items():
            if permissions:
                app_names = {
                    'members': '👥 Membros',
                    'accounts': '🏦 Contas',
                    'expenses': '💸 Despesas',
                    'credit_cards': '💳 Cartões',
                    'loans': '💰 Empréstimos',
                    'transfers': '🔄 Transferências',
                    'revenues': '💵 Receitas'
                }

                operation_icons = {
                    'create': '➕',
                    'read': '👁️',
                    'update': '✏️',
                    'delete': '🗑️'
                }

                app_display = app_names.get(app_name, app_name)
                perm_display = ' '.join(
                    [operation_icons.get(p, p) for p in permissions])

                st.caption(f"{app_display}: {perm_display}")


# Instância global do serviço de permissões
permissions_service = PermissionsService()
