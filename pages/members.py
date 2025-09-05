"""
Módulo de gerenciamento de membros.

Este módulo implementa o CRUD completo para membros,
seguindo o padrão visual padronizado com tabs centralizadas
e layout de 3 colunas para listagem.
"""

import logging
from datetime import date, datetime
from typing import Dict, List

import streamlit as st

from components.auth import require_auth
from services.api_client import api_client, ApiClientError, ValidationError
from utils.ui_utils import ui_components, centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


class MembersPage:
    """Página de gerenciamento de membros com padrão visual padronizado."""

    def __init__(self):
        """Inicializa a página de membros."""
        self.auth = require_auth()

    def render(self):
        """
        Renderiza a página principal de membros com padrão padronizado.

        Segue o padrão visual estabelecido:
        - Duas tabs centralizadas (listagem + novo registro)
        - Layout de 3 colunas para listagem
        - Popup de ações com CRUD
        """
        ui_components.render_page_header(
            "👥 Membros",
            subtitle="Gerenciamento de pessoas e contatos"
        )

        # Tabs principais - padrão estabelecido: 2 tabs centralizadas
        tab_list, tab_add = centered_tabs([
            "📋 Listagem de Membros",
            "➕ Novo Membro"
        ])

        with tab_list:
            self._render_members_list_standardized()

        with tab_add:
            self._render_add_member_form_standardized()

    def _render_members_list_standardized(self):
        """
        Renderiza a lista de membros seguindo padrão padronizado.

        Padrão estabelecido:
        - Layout de 3 colunas por registro
        - Primeira coluna: nome + emoji do tipo
        - Segunda coluna (central): dados como documento, telefone, email
        - Terceira coluna (direita): botão de engrenagem com popup de ações
        """
        st.markdown("### 📋 Listagem de Membros")

        # Filtros simplificados em uma linha
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            status_filter = st.selectbox(
                "🔍 Status",
                options=['Todos', 'Ativos', 'Inativos'],
                index=0
            )

        with col_filter2:
            type_filter = st.selectbox(
                "👤 Tipo",
                options=['Todos', 'Usuários', 'Credores', 'Beneficiários'],
                index=0,
                help="Filtrar por tipo de membro"
            )

        # Busca membros
        try:
            with st.spinner("🔄 Carregando membros..."):
                members = self._fetch_members(status_filter, type_filter)

            if not members:
                st.info("📋 Nenhum membro encontrado com os filtros aplicados.")
                return

            st.markdown("---")

            # Renderiza membros no padrão de 3 colunas
            self._render_members_three_column_layout(members)

        except Exception as e:
            ui_components.show_persistent_error(
                error_message=f"Erro ao carregar membros: {str(e)}",
                error_type="carregar_membros",
                details=f"Detalhes técnicos: {type(e).__name__}: {str(e)}",
                suggestions=[
                    "Verifique se a API está funcionando",
                    "Confirme sua conexão com a internet",
                    "Tente recarregar a página (F5)"
                ])
            logger.error(f"Erro ao carregar membros: {e}")

    def _render_members_three_column_layout(self, members: List[Dict]):
        """
        Renderiza membros no layout padronizado de 3 colunas.

        Parameters
        ----------
        members : List[Dict]
            Lista de membros para exibir
        """
        for member in members:
            # Container para cada membro
            with st.container():
                col1, col2, col3 = st.columns([3, 3, 1])

                with col1:
                    # Primeira coluna: nome + emoji do tipo
                    emoji = self._get_member_type_emoji(member)
                    member_type = self._get_member_type_display(member)

                    st.markdown(f"""
                    **{emoji} {member.get('name', 'N/A')}**

                    📂 {member_type}

                    🆔 {member.get('document', 'N/A')}
                    """)

                with col2:
                    # Segunda coluna (central): dados principais
                    phone = member.get('phone', '')
                    email = member.get('email', '')
                    status = "✅ Ativo" if member.get(
                        'active', True
                    ) else "⏸️ Inativo"

                    # Idade se disponível
                    birth_date = member.get('birth_date')
                    age_display = ""
                    if birth_date:
                        try:
                            birth = datetime.fromisoformat(birth_date).date()
                            today = date.today()
                            age = today.year - birth.year - (
                                (today.month, today.day) < (
                                    birth.month, birth.day)
                            )
                            age_display = f"🎂 {age} anos"
                        except BaseException:
                            age_display = ""

                    st.markdown(f"""
                    **📞 {phone or 'N/A'}**

                    **📧 {email or 'N/A'}**

                    {age_display}

                    {status}
                    """)

                with col3:
                    # Terceira coluna (direita): botão de ações
                    if st.button(
                        "⚙️",
                        key=f"actions_{member['id']}",
                        help="Opções de ações",
                        use_container_width=True
                    ):
                        st.session_state[f'show_actions_{member["id"]}'] = True
                        st.rerun()

                # Popup de ações para este membro
                self._render_member_action_popup(member)

                st.markdown("---")

    def _render_member_action_popup(self, member: Dict):
        """
        Renderiza popup de ações para um membro específico.

        Parameters
        ----------
        member : Dict
            Dados do membro
        """
        popup_key = f'show_actions_{member["id"]}'

        if st.session_state.get(popup_key, False):
            with st.expander(
                f"⚙️ Ações para: {member.get('name', 'N/A')}",
                expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📝 Editar",
                        key=f"edit_{member['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[f'edit_member_{member["id"]}'] = (
                            member
                        )
                        st.session_state[popup_key] = False
                        st.rerun()

                with col2:
                    action_text = "⏸️ Desativar" if member.get(
                        'active', True
                    ) else "✅ Ativar"
                    if st.button(
                        action_text,
                        key=f"toggle_{member['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        self._handle_toggle_member_status(member)
                        st.session_state[popup_key] = False
                        st.rerun()

                with col3:
                    if st.button(
                        "❌ Fechar",
                        key=f"close_{member['id']}",
                        use_container_width=True
                    ):
                        st.session_state[popup_key] = False
                        st.rerun()

        # Renderiza modal de edição
        self._render_edit_member_modal(member)

    def _render_edit_member_modal(self, member: Dict):
        """
        Renderiza modal de edição para um membro.

        Parameters
        ----------
        member : Dict
            Dados do membro para editar
        """
        edit_key = f'edit_member_{member["id"]}'

        if st.session_state.get(edit_key):
            st.markdown("### ✏️ Editar Membro")

            with st.form(f"edit_form_{member['id']}", clear_on_submit=False):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input(
                        "👤 Nome *",
                        value=member.get('name', ''),
                        help="Nome completo do membro"
                    )

                    document = st.text_input(
                        "🆔 Documento *",
                        value=member.get('document', ''),
                        help="CPF ou CNPJ"
                    )

                    phone = st.text_input(
                        "📞 Telefone",
                        value=member.get('phone', ''),
                        help="Número de telefone ou celular"
                    )

                with col2:
                    email = st.text_input(
                        "📧 Email",
                        value=member.get('email', ''),
                        help="Endereço de email"
                    )

                    # Sexo
                    current_sex = member.get('sex', 'M')
                    sex_options = list(db_categories.SEX_CHOICES.values())
                    sex_index = 0

                    for idx, (key, value) in enumerate(
                            db_categories.SEX_CHOICES.items()):
                        if key == current_sex:
                            sex_index = idx
                            break

                    sex = st.selectbox(
                        "⚧️ Sexo",
                        options=sex_options,
                        index=sex_index,
                        format_func=lambda x: f"⚧️ {x}"
                    )

                    # Data de nascimento
                    birth_date = None
                    birth_date_str = member.get('birth_date')
                    if birth_date_str:
                        try:
                            birth_date = datetime.fromisoformat(
                                birth_date_str
                            ).date()
                        except BaseException:
                            birth_date = None

                    birth_date = st.date_input(
                        "🎂 Data de Nascimento",
                        value=birth_date or date.today(),
                        max_value=date.today()
                    )

                # Campos adicionais
                with st.expander("📋 Informações Adicionais"):
                    col_add1, col_add2 = st.columns(2)

                    with col_add1:
                        occupation = st.text_input(
                            "💼 Profissão",
                            value=member.get('occupation', ''),
                            help="Profissão ou ocupação"
                        )

                        monthly_income = st.number_input(
                            "💰 Renda Mensal (R$)",
                            value=float(member.get('monthly_income', 0)),
                            min_value=0.00,
                            step=0.01,
                            format="%.2f"
                        )

                    with col_add2:
                        emergency_contact = st.text_input(
                            "🚨 Contato de Emergência",
                            value=member.get('emergency_contact', ''),
                            help="Nome e telefone para emergências"
                        )

                        # Checkboxes para tipos
                        is_creditor = st.checkbox(
                            "💸 É Credor",
                            value=member.get('is_creditor', False),
                            help="Marca se a pessoa pode emprestar dinheiro"
                        )

                        is_benefited = st.checkbox(
                            "💰 É Beneficiário",
                            value=member.get('is_benefited', False),
                            help="Marca se a pessoa pode receber empréstimos"
                        )

                    address = st.text_area(
                        "📍 Endereço",
                        value=member.get('address', ''),
                        help="Endereço completo"
                    )

                    notes = st.text_area(
                        "📝 Observações",
                        value=member.get('notes', ''),
                        help="Informações adicionais"
                    )

                # Botões de ação
                col_save, col_cancel = st.columns(2)

                with col_save:
                    submitted = st.form_submit_button(
                        "💾 Salvar Alterações",
                        type="primary",
                        use_container_width=True
                    )

                with col_cancel:
                    cancelled = st.form_submit_button(
                        "❌ Cancelar",
                        use_container_width=True
                    )

                if submitted:
                    self._handle_edit_member_submission(
                        member['id'], name, document, phone, email,
                        sex, birth_date, occupation, monthly_income,
                        emergency_contact, is_creditor, is_benefited,
                        address, notes, edit_key
                    )

                if cancelled:
                    st.session_state.pop(edit_key, None)
                    st.rerun()

    def _render_add_member_form_standardized(self):
        """Renderiza formulário padronizado de adição de membro."""
        ui_components.render_enhanced_form_container(
            "Cadastrar Novo Membro", "➕"
        )

        with st.form("add_member_form_standardized", clear_on_submit=True):
            # Seção de dados principais
            st.markdown("#### 👤 Dados Pessoais")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "👤 Nome *",
                    help="Nome completo da pessoa"
                )

                document = st.text_input(
                    "🆔 Documento *",
                    help="CPF ou CNPJ (apenas números)"
                )

                phone = st.text_input(
                    "📞 Telefone",
                    help="Número de telefone ou celular"
                )

            with col2:
                email = st.text_input(
                    "📧 Email",
                    help="Endereço de email válido"
                )

                # Sexo
                sex_options = list(db_categories.SEX_CHOICES.values())
                sex = st.selectbox(
                    "⚧️ Sexo",
                    options=sex_options,
                    format_func=lambda x: f"⚧️ {x}"
                )

                birth_date = st.date_input(
                    "🎂 Data de Nascimento",
                    value=None,
                    max_value=date.today(),
                    help="Data de nascimento"
                )

            # Campos opcionais
            with st.expander("📋 Informações Adicionais (Opcional)"):
                col_opt1, col_opt2 = st.columns(2)

                with col_opt1:
                    occupation = st.text_input(
                        "💼 Profissão",
                        help="Profissão ou ocupação atual"
                    )

                    monthly_income = st.number_input(
                        "💰 Renda Mensal (R$)",
                        min_value=0.00,
                        step=0.01,
                        format="%.2f",
                        help="Renda mensal aproximada"
                    )

                with col_opt2:
                    emergency_contact = st.text_input(
                        "🚨 Contato de Emergência",
                        help="Nome e telefone para emergências"
                    )

                    # Checkboxes para tipos
                    st.markdown("**Tipos de Membro:**")
                    is_creditor = st.checkbox(
                        "💸 É Credor",
                        help="Marca se a pessoa pode emprestar dinheiro"
                    )

                    is_benefited = st.checkbox(
                        "💰 É Beneficiário",
                        help="Marca se a pessoa pode receber empréstimos"
                    )

                address = st.text_area(
                    "📍 Endereço",
                    help="Endereço completo"
                )

                notes = st.text_area(
                    "📝 Observações",
                    help="Informações adicionais sobre o membro"
                )

            # Botão de submissão
            submitted = st.form_submit_button(
                "💾 Salvar Membro",
                type="primary",
                use_container_width=True
            )

            if submitted:
                self._handle_add_member_submission(
                    name, document, phone, email, sex, birth_date,
                    occupation, monthly_income, emergency_contact,
                    is_creditor, is_benefited, address, notes
                )

    def _get_member_type_emoji(self, member: Dict) -> str:
        """
        Obtém emoji para o tipo de membro.

        Parameters
        ----------
        member : Dict
            Dados do membro

        Returns
        -------
        str
            Emoji correspondente ao tipo
        """
        if member.get('user_id'):
            return "👨‍💻"  # Usuário do sistema
        elif member.get('is_creditor') and member.get('is_benefited'):
            return "🤝"  # Credor e beneficiário
        elif member.get('is_creditor'):
            return "💸"  # Credor
        elif member.get('is_benefited'):
            return "💰"  # Beneficiário
        else:
            return "👤"  # Membro comum

    def _get_member_type_display(self, member: Dict) -> str:
        """
        Obtém descrição do tipo de membro.

        Parameters
        ----------
        member : Dict
            Dados do membro

        Returns
        -------
        str
            Descrição do tipo
        """
        types = []

        if member.get('user_id'):
            types.append("Usuário")
        if member.get('is_creditor'):
            types.append("Credor")
        if member.get('is_benefited'):
            types.append("Beneficiário")

        return ", ".join(types) if types else "Membro"

    def _fetch_members(
            self,
            status_filter: str,
            type_filter: str) -> List[Dict]:
        """
        Busca membros com filtros aplicados.

        Parameters
        ----------
        status_filter : str
            Filtro de status
        type_filter : str
            Filtro de tipo

        Returns
        -------
        List[Dict]
            Lista de membros filtrados
        """
        try:
            members_response = api_client.get("members/")
            members = (
                members_response.get('results', members_response)
                if isinstance(members_response, dict)
                else members_response
            )

            if not members:
                return []

            # Aplica filtros
            filtered_members = members

            # Filtro por status
            if status_filter == 'Ativos':
                filtered_members = [
                    m for m in filtered_members
                    if m.get('active', True)
                ]
            elif status_filter == 'Inativos':
                filtered_members = [
                    m for m in filtered_members
                    if not m.get('active', True)
                ]

            # Filtro por tipo
            if type_filter == 'Usuários':
                filtered_members = [
                    m for m in filtered_members
                    if m.get('user_id')
                ]
            elif type_filter == 'Credores':
                filtered_members = [
                    m for m in filtered_members
                    if m.get('is_creditor', False)
                ]
            elif type_filter == 'Beneficiários':
                filtered_members = [
                    m for m in filtered_members
                    if m.get('is_benefited', False)
                ]

            return filtered_members

        except Exception as e:
            logger.error(f"Erro ao buscar membros: {e}")
            raise

    def _handle_add_member_submission(
        self, name: str, document: str, phone: str, email: str,
        sex: str, birth_date: date, occupation: str,
        monthly_income: float, emergency_contact: str,
        is_creditor: bool, is_benefited: bool, address: str,
        notes: str
    ):
        """
        Processa submissão do formulário de novo membro.

        Parameters
        ----------
        name : str
            Nome do membro
        document : str
            Documento
        phone : str
            Telefone
        email : str
            Email
        sex : str
            Sexo
        birth_date : date
            Data de nascimento
        occupation : str
            Profissão
        monthly_income : float
            Renda mensal
        emergency_contact : str
            Contato de emergência
        is_creditor : bool
            Se é credor
        is_benefited : bool
            Se é beneficiário
        address : str
            Endereço
        notes : str
            Observações
        """
        if not name or not document:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte sexo para código da API
            sex_code = None
            for key, val in db_categories.SEX_CHOICES.items():
                if val == sex:
                    sex_code = key
                    break

            member_data = {
                'name': name,
                'document': document,
                'phone': phone or '',
                'email': email or '',
                'sex': sex_code or 'M',
                'birth_date': birth_date.isoformat() if birth_date else None,
                'occupation': occupation or '',
                'monthly_income': (
                    str(monthly_income) if monthly_income else '0.00'
                ),
                'emergency_contact': emergency_contact or '',
                'is_creditor': is_creditor,
                'is_benefited': is_benefited,
                'address': address or '',
                'notes': notes or '',
                'active': True}

            with st.spinner("💾 Salvando membro..."):
                result = api_client.post("members/", data=member_data)

            if result:
                st.success(f"✅ Membro '{name}' cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar membro!")

        except ValidationError as e:
            error_details = getattr(e, 'details', {})
            st.error(f"❌ Dados inválidos: {str(e)}")

            if error_details:
                with st.expander("📋 Detalhes dos Erros"):
                    for field, errors in error_details.items():
                        st.write(f"**{field}:** {', '.join(errors)}")

        except ApiClientError as e:
            st.error(f"❌ Erro de comunicação: {str(e)}")

        except Exception as e:
            st.error(f"❌ Erro inesperado: {str(e)}")
            logger.error(f"Erro ao criar membro: {e}")

    def _handle_edit_member_submission(
        self, member_id: int, name: str, document: str, phone: str,
        email: str, sex: str, birth_date: date, occupation: str,
        monthly_income: float, emergency_contact: str,
        is_creditor: bool, is_benefited: bool, address: str,
        notes: str, edit_key: str
    ):
        """
        Processa submissão da edição de membro.

        Parameters
        ----------
        member_id : int
            ID do membro
        name : str
            Novo nome
        document : str
            Novo documento
        phone : str
            Novo telefone
        email : str
            Novo email
        sex : str
            Novo sexo
        birth_date : date
            Nova data nascimento
        occupation : str
            Nova profissão
        monthly_income : float
            Nova renda
        emergency_contact : str
            Novo contato emergência
        is_creditor : bool
            Novo status credor
        is_benefited : bool
            Novo status beneficiário
        address : str
            Novo endereço
        notes : str
            Novas observações
        edit_key : str
            Chave da sessão
        """
        if not name or not document:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte sexo para código da API
            sex_code = None
            for key, val in db_categories.SEX_CHOICES.items():
                if val == sex:
                    sex_code = key
                    break

            update_data = {
                'name': name,
                'document': document,
                'phone': phone or '',
                'email': email or '',
                'sex': sex_code or 'M',
                'birth_date': birth_date.isoformat() if birth_date else None,
                'occupation': occupation or '',
                'monthly_income': str(monthly_income),
                'emergency_contact': emergency_contact or '',
                'is_creditor': is_creditor,
                'is_benefited': is_benefited,
                'address': address or '',
                'notes': notes or ''
            }

            with st.spinner("💾 Salvando alterações..."):
                result = api_client.put(
                    f"members/{member_id}/", data=update_data)

            if result:
                st.success("✅ Membro atualizado com sucesso!")
                st.session_state.pop(edit_key, None)
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar membro!")

        except Exception as e:
            st.error(f"❌ Erro ao atualizar: {str(e)}")
            logger.error(f"Erro ao atualizar membro {member_id}: {e}")

    def _handle_toggle_member_status(self, member: Dict):
        """
        Alterna status ativo/inativo do membro.

        Parameters
        ----------
        member : Dict
            Dados do membro
        """
        try:
            new_status = not member.get('active', True)
            status_text = "ativado" if new_status else "desativado"

            action = 'Ativando' if new_status else 'Desativando'
            with st.spinner(f"⚙️ {action} membro..."):
                result = api_client.put(
                    f"members/{member['id']}/",
                    data={'active': new_status}
                )

            if result:
                st.success(
                    f"✅ Membro {status_text} com sucesso!"
                )
                st.rerun()
            else:
                st.error(
                    f"❌ Erro ao {'ativar' if new_status else 'desativar'} "
                    "membro!"
                )

        except Exception as e:
            st.error(f"❌ Erro ao alterar status: {str(e)}")
            logger.error(
                f"Erro ao alterar status do membro {member['id']}: {e}")


# Função de entrada principal
def show():
    """Função de entrada para a página de membros."""
    page = MembersPage()
    page.render()


# Compatibilidade com estrutura existente
members_page = MembersPage()
