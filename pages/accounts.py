"""
Página de gestão de contas bancárias.

Esta página permite ao usuário visualizar, criar, editar e excluir
contas bancárias integradas com a API ExpenseLit.
"""

import logging
import time
from typing import Dict, Any
import streamlit as st
from pages.router import BasePage
from services.api_client import ApiClientError, ValidationError
from services.accounts_service import accounts_service
from services.permissions_service import permissions_service
from config.settings import db_categories


logger = logging.getLogger(__name__)


class AccountsPage(BasePage):
    """
    Página de gestão de contas bancárias.

    Permite operações CRUD (Create, Read, Update, Delete) em contas,
    com integração completa à API ExpenseLit.
    """

    def __init__(self):
        """Inicializa a página de contas."""
        super().__init__("Gestão de Contas", "🏦")
        self.required_permissions = ['accounts.view_account']

    def main_menu(self, token=None, permissions=None):
        """
        Método principal seguindo padrão CodexDB.

        Parameters
        ----------
        token : str, optional
            Token de autenticação (mantido para compatibilidade)
        permissions : dict, optional
            Permissões do usuário (mantido para compatibilidade)
        """
        st.subheader("🏦 Gestão de Contas")
        self.render()

    def render(self) -> None:
        """
        Renderiza o conteúdo da página de contas.

        Apresenta:
        - Lista de contas existentes
        - Formulário para criar/editar contas
        - Ações de gerenciamento
        """
        # Tabs para organizar funcionalidades
        tab1, tab2 = st.tabs(["📋 Minhas Contas", "➕ Nova Conta"])

        with tab1:
            self._render_accounts_list()

        with tab2:
            self._render_account_form()

    def _render_accounts_list(self) -> None:
        """Renderiza a lista de contas existentes."""
        st.markdown("### 📋 Lista de Contas")

        try:
            with st.spinner("🔄 Carregando contas..."):
                time.sleep(2)
                accounts = accounts_service.get_all_accounts(active_only=False)

            if not accounts:
                st.info("📝 Nenhuma conta cadastrada ainda.")
                st.markdown
                ("""💡 **Dica:** Use a aba 'Nova Conta'
                 para criar sua primeira conta.
                 """)
                return

            # Filtros
            col1, col2 = st.columns([2, 1])
            with col1:
                show_inactive = st.checkbox(
                    "👁️ Mostrar contas inativas",
                    key="show_inactive_accounts",
                    help="Inclui contas inativas na listagem"
                )

            # Filtra contas baseado no filtro
            if not show_inactive:
                accounts = [acc for acc in accounts if acc.get(
                    'is_active', True
                    )
                ]

            # Renderiza contas como cards
            for account in accounts:
                self._render_account_card(account)

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar contas: {e}")
            logger.error(f"Erro ao listar contas: {e}")

    def _render_account_card(self, account: Dict[str, Any]) -> None:
        """
        Renderiza um card para uma conta específica.

        Parameters
        ----------
        account : Dict[str, Any]
            Dados da conta
        """
        account_name = account.get('name', 'Conta sem nome')
        # Traduz a sigla para o nome completo da instituição
        account_display_name = db_categories.INSTITUTIONS.get(
            account_name, account_name
        )
        account_type = account.get('account_type', '')
        account_type_name = db_categories.ACCOUNT_TYPES.get(
            account_type, account_type
        )
        is_active = account.get('is_active', True)
        account_id = account.get('id')

        # Container do card
        with st.container():
            # Header do card
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"### 🏦 {account_display_name}")
                st.caption(f"Tipo: {account_type_name}")

            with col2:
                if is_active:
                    st.success("✅ Conta Ativa")
                else:
                    st.warning("⚠️ Conta Inativa")

            with col3:
                # Menu de ações
                with st.popover("⚙️ Ações"):
                    edit_clicked = st.button(
                        "✏️ Editar",
                        key=f"edit_account_{account_id}",
                        width='stretch',
                        help="Editar dados da conta"
                    )

                    # Toggle ativo/inativo
                    toggle_text = "❌ Inativar" if is_active else "✅ Ativar"
                    if st.button(
                        toggle_text,
                        key=f"toggle_account_{account_id}",
                        width='stretch',
                        help="Ativar/Inativar conta"
                    ):
                        self._toggle_account_status(
                            account_id, not is_active  # type: ignore
                        )

                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_account_{account_id}",
                        width='stretch',
                        help="Excluir conta permanentemente"
                    ):
                        self._delete_account(
                            account_id, account_display_name  # type: ignore
                        )
                        
            # Processa ação de editar fora do contexto do widget
            if edit_clicked:
                st.session_state[f'edit_account_{account_id}'] = account
                st.rerun()

            # Formulário de edição inline se ativo
            if st.session_state.get(f'edit_account_{account_id}'):
                self._render_inline_edit_form(account)

            st.markdown("---")

    def _render_inline_edit_form(self, account: Dict[str, Any]) -> None:
        """
        Renderiza formulário de edição inline para uma conta.

        Parameters
        ----------
        account : Dict[str, Any]
            Dados da conta a editar
        """
        account_id = account.get('id')

        st.markdown("#### ✏️ Editando Conta")

        with st.form(f"edit_form_{account_id}"):
            col1, col2 = st.columns(2)

            with col1:
                current_institution = account.get('name', 'NUB')
                current_institution_display = db_categories.INSTITUTIONS.get(current_institution, current_institution)
                new_name_display = st.selectbox(
                    "🏦 Nome da Instituição",
                    options=list(db_categories.TRANSLATED_INSTITUTIONS.keys()),
                    index=list(
                        db_categories.TRANSLATED_INSTITUTIONS.keys()
                    ).index(current_institution_display),
                    help="Selecione a instituição bancária"
                )
                new_name = db_categories.TRANSLATED_INSTITUTIONS[new_name_display]

            with col2:
                current_type = account.get('account_type', 'CC')
                current_type_display = db_categories.ACCOUNT_TYPES.get(current_type, current_type)
                new_type_display = st.selectbox(
                    "💳 Tipo da Conta",
                    options=list(db_categories.TRANSLATED_ACCOUNT_TYPES.keys()),
                    index=list(
                        db_categories.TRANSLATED_ACCOUNT_TYPES.keys()
                    ).index(current_type_display),
                    help="Tipo de conta bancária"
                )
                new_type = db_categories.TRANSLATED_ACCOUNT_TYPES[new_type_display]

            new_is_active = st.checkbox(
                "✅ Conta Ativa",
                value=account.get('is_active', True),
                help="Marque se a conta está ativa"
            )

            col_submit, col_cancel = st.columns(2)

            with col_submit:
                if st.form_submit_button(
                    "💾 Salvar Alterações",
                    type="primary",
                    width='stretch'
                ):
                    self._update_account(account_id, {  # type: ignore
                        'name': new_name,
                        'account_type': new_type,
                        'is_active': new_is_active
                    })

            with col_cancel:
                if st.form_submit_button(
                    "❌ Cancelar",
                    width='stretch'
                ):
                    st.session_state.pop(f'edit_account_{account_id}', None)
                    st.rerun()

    def _render_account_form(self) -> None:
        """Renderiza formulário para criação de nova conta."""
        st.markdown("### ➕ Criar Nova Conta")

        with st.form("create_account_form", clear_on_submit=True):
            st.markdown("**Preencha os dados da nova conta:**")

            col1, col2 = st.columns(2)

            with col1:
                institution_name_display = st.selectbox(
                    "🏦 Instituição Bancária",
                    options=list(db_categories.TRANSLATED_INSTITUTIONS.keys()),
                    help="Selecione a instituição bancária",
                    key="new_account_institution"
                )
                institution_name = db_categories.TRANSLATED_INSTITUTIONS[institution_name_display]

            with col2:
                account_type_display = st.selectbox(
                    "💳 Tipo da Conta",
                    options=list(db_categories.TRANSLATED_ACCOUNT_TYPES.keys()),
                    help="Selecione o tipo de conta",
                    key="new_account_type"
                )
                account_type = db_categories.TRANSLATED_ACCOUNT_TYPES[account_type_display]

            is_active = st.checkbox(
                "✅ Conta Ativa",
                value=True,
                help="Marque se a conta deve ficar ativa",
                key="new_account_active"
            )

            # Preview da conta
            with st.expander("👁️ Preview da Conta", expanded=True):
                st.info(f"""
                **Instituição:** {institution_name_display}
                **Tipo:** {account_type_display}
                **Status:** {'Ativa' if is_active else 'Inativa'}
                """)

            # Botão de envio
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button(
                    "💾 Criar Conta",
                    type="primary",
                    width='stretch'
                ):
                    account_data = {
                        'name': institution_name,
                        'account_type': account_type,
                        'is_active': is_active
                    }
                    self._create_account(account_data)

    def _create_account(self, account_data: Dict[str, Any]) -> None:
        """
        Cria uma nova conta via API.

        Parameters
        ----------
        account_data : Dict[str, Any]
            Dados da nova conta
        """
        try:
            with st.spinner("💾 Criando conta..."):
                time.sleep(2)
                new_account = accounts_service.create_account(account_data)

            st.toast("✅ Conta criada com sucesso!")
            time.sleep(2)

            # Recarrega a página para mostrar a nova conta
            st.rerun()

        except ValidationError as e:
            st.error(f"❌ Dados inválidos: {e}")
            logger.error(f"Erro de validação ao criar conta: {e}")
        except ApiClientError as e:
            st.error(f"🔧 Erro ao criar conta: {e}")
            logger.error(f"Erro da API ao criar conta: {e}")

    def _update_account(
            self,
            account_id: int,
            account_data: Dict[str, Any]
            ) -> None:
        """
        Atualiza uma conta existente via API.

        Parameters
        ----------
        account_id : int
            ID da conta a atualizar
        account_data : Dict[str, Any]
            Novos dados da conta
        """
        try:
            with st.spinner("💾 Salvando alterações..."):
                updated_account = accounts_service.update_account(
                    account_id,
                    account_data
                )
                print(updated_account)
            st.success("✅ Conta atualizada com sucesso!")

            # Remove o estado de edição e recarrega
            st.session_state.pop(f'edit_account_{account_id}', None)
            st.rerun()

        except ValidationError as e:
            st.error(f"❌ Dados inválidos: {e}")
            logger.error(
                f"Erro de validação ao atualizar conta {account_id}: {e}"
            )
        except ApiClientError as e:
            st.error(f"🔧 Erro ao atualizar conta: {e}")
            logger.error(f"Erro da API ao atualizar conta {account_id}: {e}")

    def _toggle_account_status(
            self,
            account_id: int,
            new_status: bool
            ) -> None:
        """
        Alterna o status ativo/inativo de uma conta.

        Parameters
        ----------
        account_id : int
            ID da conta
        new_status : bool
            Novo status da conta
        """
        try:
            with st.spinner(
                f"{'Ativando' if new_status else 'Inativando'} conta..."
            ):
                accounts_service.update_account(
                    account_id, {'is_active': new_status}
                )

            status_text = "ativada" if new_status else "inativada"
            st.success(f"✅ Conta {status_text} com sucesso!")
            st.rerun()

        except ApiClientError as e:
            st.error(f"🔧 Erro ao alterar status da conta: {e}")
            logger.error(f"Erro ao alterar status da conta {account_id}: {e}")

    def _delete_account(self, account_id: int, account_name: str) -> None:
        """
        Exclui uma conta após confirmação.

        Parameters
        ----------
        account_id : int
            ID da conta a excluir
        account_name : str
            Nome da conta para exibição
        """
        # Confirmação de exclusão
        st.warning(
            f"⚠️ **Tem certeza que deseja excluir a conta '{account_name}'?**"
        )
        st.error("🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🗑️ Sim, Excluir Conta",
                key=f"confirm_delete_{account_id}",
                type="primary",
                width='stretch'
            ):
                try:
                    with st.spinner("🗑️ Excluindo conta..."):
                        accounts_service.delete_account(account_id)

                    st.success(
                        f"✅ Conta '{account_name}' excluída com sucesso!"
                    )
                    st.rerun()

                except ApiClientError as e:
                    st.error(f"🔧 Erro ao excluir conta: {e}")
                    logger.error(f"Erro ao excluir conta {account_id}: {e}")

        with col2:
            if st.button(
                "❌ Cancelar",
                key=f"cancel_delete_{account_id}",
                width='stretch'
            ):
                st.rerun()
