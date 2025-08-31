"""
Página de gestão de membros.

Esta página permite ao usuário visualizar, criar, editar e excluir
membros integrados com a API ExpenseLit.
"""

import logging
import time
import re
from typing import Dict, Any

import streamlit as st

from pages.router import BasePage
from services.api_client import api_client
from services.users_service import users_service
from services.api_client import ApiClientError
from services.permissions_service import permissions_service
from utils.ui_utils import messages, ui_components, validation, centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


class MembersPage(BasePage):
    """
    Página de gestão de membros.
    
    Permite operações CRUD em membros com integração à API.
    """
    
    def __init__(self):
        super().__init__("Membros", "👥")
        # self.required_permissions = ['members.view_member']  # Desabilitado - superusuários têm acesso total
    
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
        st.subheader("👥 Membros")
        self.render()
    
    def render(self) -> None:
        """Renderiza o conteúdo da página de membros."""
        # Verifica permissão de leitura
        if not permissions_service.has_permission('members', 'read'):
            permissions_service.check_permission('members', 'read')
            return
        
        tabs = ["📋 Membros"]
        
        # Adiciona aba de criação se tiver permissão
        if permissions_service.has_permission('members', 'create'):
            tabs.append("➕ Novo Membro")
        
        tabs.append("📊 Resumo")
        
        tab_objects = centered_tabs(tabs)
        
        # Tab Membros (sempre presente se tem permissão de read)
        with tab_objects[0]:
            self._render_members_list()
        
        # Tab Novo Membro (apenas se tem permissão de create)
        tab_index = 1
        if permissions_service.has_permission('members', 'create'):
            with tab_objects[tab_index]:
                self._render_member_form()
            tab_index += 1
        
        # Tab Resumo
        with tab_objects[tab_index]:
            self._render_members_summary()

    def _render_members_list(self) -> None:
        """Renderiza a lista de membros."""
        st.markdown("### 👥 Lista de Membros")
        
        try:
            with st.spinner("🔄 Carregando membros..."):
                time.sleep(1)
                members = api_client.get("members/")
            
            if not members:
                st.info(messages.info('empty_list', item='membro'))
                return
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_status = st.selectbox(
                    "📊 Status",
                    options=["Todos", "Ativos", "Inativos"]
                )
            
            with col2:
                filter_user = st.selectbox(
                    "👤 Tipo de Usuário",
                    options=["Todos", "Usuários", "Não Usuários"]
                )
            
            with col3:
                filter_sex = st.selectbox(
                    "🚻 Sexo",
                    options=["Todos", "Masculino", "Feminino"]
                )
            
            # Aplica filtros
            filtered_members = members
            
            if filter_status == "Ativos":
                filtered_members = [m for m in filtered_members if m.get('active', True)]
            elif filter_status == "Inativos":
                filtered_members = [m for m in filtered_members if not m.get('active', True)]
            
            if filter_user == "Usuários":
                filtered_members = [m for m in filtered_members if m.get('is_user', False)]
            elif filter_user == "Não Usuários":
                filtered_members = [m for m in filtered_members if not m.get('is_user', False)]
            
            if filter_sex == "Masculino":
                filtered_members = [m for m in filtered_members if m.get('sex') == 'M']
            elif filter_sex == "Feminino":
                filtered_members = [m for m in filtered_members if m.get('sex') == 'F']
            
            # Estatísticas rápidas
            total_members = len(filtered_members)
            active_members = sum(1 for m in filtered_members if m.get('active', True))
            users = sum(1 for m in filtered_members if m.get('is_user', False))
            creditors = sum(1 for m in filtered_members if m.get('is_creditor', False))
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total", total_members)
            with col2:
                st.metric("✅ Ativos", active_members)
            with col3:
                st.metric("👤 Usuários", users)
            with col4:
                st.metric("💼 Credores", creditors)
            
            st.markdown("---")
            
            for member in filtered_members:
                self._render_member_card(member)
                
        except ApiClientError as e:
            st.error(messages.error('api_error', action='carregar membros', details=str(e)))
            logger.error(f"Erro ao listar membros: {e}")

    def _render_member_card(self, member: Dict[str, Any]) -> None:
        """Renderiza um card de membro."""
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                name = member.get('name', 'Membro')
                document = member.get('document', 'N/A')
                phone = member.get('phone', 'N/A')
                email = member.get('email', 'N/A')
                sex_display = "👨 Masculino" if member.get('sex') == 'M' else "👩 Feminino"
                
                st.markdown(f"### 👤 {name}")
                st.caption(f"📄 {document} | 📞 {phone}")
                if email and email != 'N/A':
                    st.caption(f"📧 {email}")
                st.caption(sex_display)
            
            with col2:
                roles = []
                if member.get('is_user', False):
                    roles.append("👤 Usuário")
                if member.get('is_creditor', False):
                    roles.append("💼 Credor")
                if member.get('is_benefited', False):
                    roles.append("🎯 Beneficiário")
                
                st.markdown("**Perfis:**")
                for role in roles if roles else ["Nenhum perfil"]:
                    st.caption(role)
            
            with col3:
                if member.get('active', True):
                    st.success("✅ Ativo")
                else:
                    st.error("❌ Inativo")
            
            with col4:
                member_id = member.get('id')
                with st.popover("⚙️ Ações"):
                    # Botão de Editar - requer permissão de update
                    if permissions_service.has_permission('members', 'update'):
                        if st.button(
                            "✏️ Editar",
                            key=f"edit_member_{member_id}",
                            width='stretch'
                        ):
                            if f'edit_member_{member_id}' not in st.session_state:
                                st.session_state[f'edit_member_{member_id}'] = member
                            st.rerun()
                    
                    # Botão de Ativar/Desativar - requer permissão de update
                    if permissions_service.has_permission('members', 'update'):
                        toggle_text = ("❌ Desativar" if member.get('active', True) 
                                     else "✅ Ativar")
                        if st.button(
                            toggle_text,
                            key=f"toggle_member_{member_id}",
                            width='stretch'
                        ):
                            self._toggle_member_status(member_id, not member.get('active', True))
                    
                    # Botão de Excluir - requer permissão de delete
                    if permissions_service.has_permission('members', 'delete'):
                        if st.button(
                            "🗑️ Excluir",
                            key=f"delete_member_{member_id}",
                            width='stretch'
                        ):
                            self._delete_member(member_id, name)
                    
                    # Informação sobre permissões se não tiver nenhuma ação disponível
                    has_actions = (permissions_service.has_permission('members', 'update') or 
                                 permissions_service.has_permission('members', 'delete'))
                    if not has_actions:
                        st.caption("⚠️ Sem permissões para ações")
            
            # Formulário de edição inline se ativo
            edit_state_key = f'edit_member_{member_id}'
            if edit_state_key in st.session_state and st.session_state[edit_state_key]:
                self._render_edit_form(member)
            
            st.markdown("---")

    def _render_edit_form(self, member: Dict[str, Any]) -> None:
        """Renderiza formulário de edição inline."""
        member_id = member.get('id')
        
        st.markdown("#### ✏️ Editando Membro")
        
        with st.form(f"edit_member_form_{member_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "👤 Nome",
                    value=member.get('name', '')
                )
                
                new_document = st.text_input(
                    "📄 Documento (CPF/CNPJ)",
                    value=member.get('document', '')
                )
                
                new_phone = st.text_input(
                    "📞 Telefone",
                    value=member.get('phone', '')
                )
                
                new_email = st.text_input(
                    "📧 Email",
                    value=member.get('email', '') or ''
                )
            
            with col2:
                new_sex = st.selectbox(
                    "🚻 Sexo",
                    options=[('M', 'Masculino'), ('F', 'Feminino')],
                    index=0 if member.get('sex') == 'M' else 1,
                    format_func=lambda x: x[1]
                )
                
                new_is_user = st.checkbox(
                    "👤 É usuário do sistema",
                    value=member.get('is_user', False)
                )
                
                new_is_creditor = st.checkbox(
                    "💼 Pode ser credor",
                    value=member.get('is_creditor', False)
                )
                
                new_is_benefited = st.checkbox(
                    "🎯 Pode ser beneficiário",
                    value=member.get('is_benefited', False)
                )
                
                new_active = st.checkbox(
                    "✅ Ativo",
                    value=member.get('active', True)
                )
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                    if self._validate_document(new_document):
                        update_data = {
                            'name': new_name,
                            'document': new_document,
                            'phone': new_phone,
                            'email': new_email if new_email else None,
                            'sex': new_sex[0],
                            'is_user': new_is_user,
                            'is_creditor': new_is_creditor,
                            'is_benefited': new_is_benefited,
                            'active': new_active
                        }
                        self._update_member(member_id, update_data)
                    else:
                        st.error("❌ Documento inválido")
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.pop(f'edit_member_{member_id}', None)
                    st.rerun()

    def _render_member_form(self) -> None:
        """Renderiza formulário para criar membro."""
        st.markdown("### ➕ Criar Novo Membro")
        
        with st.form("create_member_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "👤 Nome Completo",
                    placeholder="Ex: João Silva Santos"
                )
                
                document = st.text_input(
                    "📄 Documento (CPF/CNPJ)",
                    placeholder="000.000.000-00",
                    help="CPF ou CNPJ do membro"
                )
                
                phone = st.text_input(
                    "📞 Telefone",
                    placeholder="(11) 99999-9999"
                )
                
                email = st.text_input(
                    "📧 Email (opcional)",
                    placeholder="joao@email.com"
                )
            
            with col2:
                sex = st.selectbox(
                    "🚻 Sexo",
                    options=[('M', 'Masculino'), ('F', 'Feminino')],
                    format_func=lambda x: x[1]
                )
                
                st.markdown("**Perfis do Membro:**")
                
                # Campo de usuário removido - membros não são vinculados a usuários pelo cadastro manual
                
                is_creditor = st.checkbox(
                    "💼 Pode ser credor",
                    value=True,
                    help="Pode emprestar dinheiro"
                )
                
                is_benefited = st.checkbox(
                    "🎯 Pode ser beneficiário",
                    value=True,
                    help="Pode receber empréstimos"
                )
                
                active = st.checkbox(
                    "✅ Ativo",
                    value=True,
                    help="Membro ativo no sistema"
                )
            
            if st.form_submit_button("💾 Criar Membro", type="primary"):
                # Validação usando utilitários padronizados
                required_data = {'name': name, 'document': document, 'phone': phone}
                required_error = validation.validate_required_fields(required_data, ['name', 'document', 'phone'])
                
                if required_error:
                    st.error(required_error)
                    return
                
                # Validação removida - não há mais campo de usuário
                
                document_error = validation.validate_document(document)
                if document_error:
                    st.error(document_error)
                    return
                
                email_error = validation.validate_email(email)
                if email_error:
                    st.error(email_error)
                    return
                
                member_data = {
                    'name': name,
                    'document': document,
                    'phone': phone,
                    'email': email if email else None,
                    'sex': sex[0],
                    'user': None,  # Membros não são vinculados a usuários pelo cadastro manual
                    'is_creditor': is_creditor,
                    'is_benefited': is_benefited,
                    'active': active
                }
                self._create_member(member_data)

    def _render_members_summary(self) -> None:
        """Renderiza resumo dos membros."""
        st.markdown("### 📊 Resumo de Membros")
        
        try:
            with st.spinner("📊 Carregando estatísticas..."):
                time.sleep(1)
                members = api_client.get("members/")
            
            if not members:
                st.info("📝 Nenhum membro encontrado.")
                return
            
            total_members = len(members)
            active_members = sum(1 for m in members if m.get('active', True))
            inactive_members = total_members - active_members
            male_members = sum(1 for m in members if m.get('sex') == 'M')
            female_members = sum(1 for m in members if m.get('sex') == 'F')
            users = sum(1 for m in members if m.get('is_user', False))
            creditors = sum(1 for m in members if m.get('is_creditor', False))
            beneficiaries = sum(1 for m in members if m.get('is_benefited', False))
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total de Membros", total_members)
            with col2:
                st.metric("✅ Membros Ativos", active_members)
            with col3:
                st.metric("❌ Membros Inativos", inactive_members)
            with col4:
                st.metric("👤 Usuários", users)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👨 Masculino", male_members)
            with col2:
                st.metric("👩 Feminino", female_members)
            with col3:
                st.metric("💼 Credores", creditors)
            with col4:
                st.metric("🎯 Beneficiários", beneficiaries)
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar estatísticas: {e}")
            logger.error(f"Erro ao carregar resumo de membros: {e}")

    def _validate_document(self, document: str) -> bool:
        """Valida se o documento está no formato correto (CPF ou CNPJ)."""
        if not document:
            return False
        
        # Remove caracteres não numéricos
        doc = re.sub(r'[^0-9]', '', document)
        
        # Verifica se é CPF (11 dígitos) ou CNPJ (14 dígitos)
        return len(doc) == 11 or len(doc) == 14

    def _create_member(self, member_data: Dict[str, Any]) -> None:
        """Cria um novo membro."""
        # Verifica permissão de criação
        if not permissions_service.check_permission('members', 'create'):
            return
            
        try:
            with st.spinner("💾 Criando membro..."):
                time.sleep(1)
                new_member = api_client.post("members/", member_data)
            
            st.toast(messages.success('created', item='Membro'))
            time.sleep(1)
            st.rerun()
            
        except ApiClientError as e:
            st.error(messages.error('api_error', action='criar membro', details=str(e)))
            logger.error(f"Erro ao criar membro: {e}")

    def _update_member(self, member_id: int, member_data: Dict[str, Any]) -> None:
        """Atualiza um membro."""
        # Verifica permissão de atualização
        if not permissions_service.check_permission('members', 'update'):
            return
            
        try:
            with st.spinner("💾 Atualizando membro..."):
                time.sleep(1)
                updated_member = api_client.put(f"members/{member_id}/", member_data)
            
            st.success("✅ Membro atualizado com sucesso!")
            st.session_state.pop(f'edit_member_{member_id}', None)
            st.rerun()
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao atualizar membro: {e}")
            logger.error(f"Erro ao atualizar membro {member_id}: {e}")

    def _toggle_member_status(self, member_id: int, is_active: bool) -> None:
        """Alterna o status de ativo/inativo de um membro."""
        # Verifica permissão de atualização
        if not permissions_service.check_permission('members', 'update'):
            return
            
        try:
            with st.spinner(f"{'Ativando' if is_active else 'Desativando'} membro..."):
                member_data = api_client.get(f"members/{member_id}/")
                
                update_data = {
                    'name': member_data.get('name'),
                    'document': member_data.get('document'),
                    'phone': member_data.get('phone'),
                    'email': member_data.get('email'),
                    'sex': member_data.get('sex'),
                    'is_user': member_data.get('is_user'),
                    'is_creditor': member_data.get('is_creditor'),
                    'is_benefited': member_data.get('is_benefited'),
                    'active': is_active
                }
                
                api_client.put(f"members/{member_id}/", update_data)
            
            status_text = "ativado" if is_active else "desativado"
            st.success(f"✅ Membro {status_text} com sucesso!")
            st.rerun()
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao alterar status: {e}")
            logger.error(f"Erro ao alterar status do membro {member_id}: {e}")

    def _delete_member(self, member_id: int, name: str) -> None:
        """Exclui um membro após confirmação."""
        # Verifica permissão de exclusão
        if not permissions_service.check_permission('members', 'delete'):
            return
            
        confirm_key = f"confirm_delete_member_{member_id}"
        
        if not st.session_state.get(confirm_key, False):
            st.session_state[confirm_key] = True
            st.rerun()
        
        st.warning(f"⚠️ **Tem certeza que deseja excluir o membro '{name}'?**")
        st.error("🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "🗑️ Sim, Excluir",
                key=f"final_confirm_delete_member_{member_id}",
                type="primary",
                width='stretch'
            ):
                try:
                    with st.spinner("🗑️ Excluindo membro..."):
                        api_client.delete(f"members/{member_id}/")
                    
                    st.success(f"✅ Membro '{name}' excluído com sucesso!")
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
                    
                except ApiClientError as e:
                    st.error(f"❌ Erro ao excluir membro: {e}")
                    logger.error(f"Erro ao excluir membro {member_id}: {e}")
                    st.session_state.pop(confirm_key, None)
        
        with col2:
            if st.button(
                "❌ Cancelar",
                key=f"cancel_delete_member_{member_id}",
                width='stretch'
            ):
                st.session_state.pop(confirm_key, None)
                st.rerun()