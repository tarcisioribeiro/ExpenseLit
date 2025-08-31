"""
Página de gestão de receitas.

Esta página permite ao usuário visualizar, criar, editar e excluir
receitas integradas com a API ExpenseLit.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any
from utils.date_utils import format_date_for_display, format_date_for_api, format_currency_br

import streamlit as st

from pages.router import BasePage
from services.revenues_service import revenues_service
from services.accounts_service import accounts_service
from services.pdf_generator import pdf_generator
from utils.ui_utils import centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


@st.dialog("⚠️ Recurso Não Encontrado")
def show_missing_resource_dialog(resource_name: str, resource_type: str, redirect_page: str = None):
    """
    Dialog para avisar sobre recursos ausentes.
    
    Parameters
    ----------
    resource_name : str
        Nome do recurso ausente
    resource_type : str  
        Tipo do recurso (conta, cartão, etc.)
    redirect_page : str, optional
        Página para redirecionamento
    """
    st.error(f"🚨 {resource_name} não encontrada!")
    st.markdown(f"""
    **Problema:** Nenhuma {resource_type} ativa foi encontrada no sistema.
    
    **Ação necessária:** Você precisa criar uma {resource_type} antes de continuar.
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button(
            f"➕ Cadastrar {resource_type.title()}", 
            type="primary", 
            width='stretch'
        ):
            if redirect_page:
                st.session_state['redirect_to'] = redirect_page
            st.rerun()
    
    with col2:
        if st.button("❌ Fechar", width='stretch'):
            st.rerun()


class RevenuesPage(BasePage):
    """
    Página de gestão de receitas.

    Permite operações CRUD em receitas com integração à API.
    """

    def __init__(self):
        """Inicializa a página de receitas."""
        super().__init__("Gestão de Receitas", "💰")
        self.required_permissions = ['revenues.view_revenue']

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
        st.subheader("💰 Gestão de Receitas")
        self.render()

    def render(self) -> None:
        """Renderiza o conteúdo da página de receitas."""
        tab1, tab2 = centered_tabs(["📋 Minhas Receitas", "➕ Nova Receita"])

        with tab1:
            self._render_revenues_list()

        with tab2:
            self._render_revenue_form()

    def _render_revenues_list(self) -> None:
        """Renderiza a lista de receitas."""
        st.markdown("### 💰 Lista de Receitas")

        try:
            with st.spinner("🔄 Carregando receitas..."):
                time.sleep(1)
                revenues = revenues_service.get_all_revenues()
                accounts = accounts_service.get_all_accounts()

            # Cria mapeamento de accounts para exibição
            accounts_map = {acc['id']: acc['name'] for acc in accounts}

            if not revenues:
                st.info("📝 Nenhuma receita cadastrada ainda.")
                return

            for revenue in revenues:
                self._render_revenue_card(revenue, accounts_map)

        except Exception as e:
            st.error(f"❌ Erro ao carregar receitas: {e}")
            logger.error(f"Erro ao listar receitas: {e}")

    def _render_revenue_card(self, revenue: Dict[str, Any], accounts_map: Dict[int, str]) -> None:
        """Renderiza um card de receita."""
        revenue_id = revenue.get('id')
        description = revenue.get('description', 'Receita')
        is_received = revenue.get('received', False)
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                category = revenue.get('category', 'deposit')
                category_emoji = db_categories.REVENUE_CATEGORY_EMOJIS.get(
                    category, "💰"
                )
                st.markdown(f"### {category_emoji} {description}")
                category_name = db_categories.REVENUE_CATEGORIES.get(
                    category,
                    revenue.get('category', 'Depósito')
                )
                
                # Traduz o nome da conta usando os dicionários
                account_name_code = accounts_map.get(
                    revenue.get('account'), 'Não informado'
                )
                account_name = db_categories.INSTITUTIONS.get(
                    account_name_code, account_name_code
                )
                
                st.caption(f"📂 {category_name} | 🏦 {account_name}")

            with col2:
                st.markdown(f"**{format_currency_br(revenue.get('value', 0))}**")
                st.caption(f"📅 {format_date_for_display(revenue.get('date', ''))}")

            with col3:
                if is_received:
                    st.success("✅ Recebida")
                else:
                    st.warning("⏳ Pendente")

            with col4:
                # Menu de ações
                with st.popover("⚙️ Ações"):
                    if st.button(
                        "✏️ Editar",
                        key=f"edit_btn_revenue_{revenue_id}",
                        width='stretch'
                    ):
                        st.session_state[
                            f'edit_revenue_{revenue_id}'
                        ] = revenue
                        st.rerun()

                    # Toggle recebido/pendente
                    toggle_text = (
                        "⏳ Marcar Pendente" if is_received else "✅ Confirmar Recebimento"
                    )
                    if st.button(
                        toggle_text,
                        key=f"toggle_btn_revenue_{revenue_id}",
                        width='stretch'
                    ):
                        self._toggle_revenue_received(
                            revenue_id, not is_received
                        )

                    if st.button(
                        "📄 Gerar PDF",
                        key=f"pdf_btn_revenue_{revenue_id}",
                        width='stretch'
                    ):
                        self._generate_revenue_pdf(revenue)
                    
                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_btn_revenue_{revenue_id}",
                        width='stretch'
                    ):
                        self._delete_revenue(
                            revenue_id, description
                        )

            # Formulário de edição inline se ativo
            if st.session_state.get(f'edit_revenue_{revenue_id}'):
                self._render_inline_edit_form_revenue(revenue)

            st.markdown("---")

    def _render_revenue_form(self) -> None:
        """Renderiza formulário para criação de receita."""
        st.markdown("### ➕ Criar Nova Receita")

        with st.form("create_revenue_form"):
            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input("📝 Descrição")
                value = st.number_input(
                    "💰 Valor",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f"
                )

            with col2:
                revenue_date = st.date_input(
                    "📅 Data",
                    value=datetime.now().date(),
                    format="DD/MM/YYYY"
                )
                category_display = st.selectbox(
                    "📂 Categoria",
                    options=list(db_categories.TRANSLATED_REVENUE_CATEGORIES.keys())
                )
                category = db_categories.TRANSLATED_REVENUE_CATEGORIES[category_display]

            try:
                accounts = accounts_service.get_all_accounts()
                if not accounts:
                    self._show_no_accounts_dialog()
                    return
                
                account_options = [(
                    acc['id'],
                    db_categories.INSTITUTIONS.get(acc['name'], acc['name'])
                ) for acc in accounts if acc.get('is_active', True)]

                if account_options:
                    selected_account = st.selectbox(
                        "🏦 Conta",
                        options=account_options,
                        format_func=lambda x: x[1]
                    )
                    account_id = selected_account[0]
                else:
                    self._show_no_accounts_dialog()
                    return
            except Exception as e:
                st.error("❌ Erro ao carregar contas")
                logger.error(f"Erro ao carregar contas: {e}")
                return

            received = st.checkbox("✅ Receita já foi recebida")
            
            # Checkbox de confirmação
            confirm_data = st.checkbox("✅ Confirmo que os dados informados estão corretos")

            if st.form_submit_button("💾 Criar Receita", type="primary"):
                if not confirm_data:
                    st.error("❌ Confirme que os dados estão corretos antes de prosseguir")
                elif description and value and account_id:
                    revenue_data = {
                        'description': description,
                        'value': value,
                        'date': format_date_for_api(revenue_date),
                        'horary': datetime.now().strftime('%H:%M:%S'),
                        'category': category,
                        'account': account_id,
                        'received': received
                    }
                    self._create_revenue(revenue_data)
                else:
                    st.error("Preencha todos os campos obrigatórios")

    def _create_revenue(self, revenue_data: Dict[str, Any]) -> None:
        """Cria uma nova receita."""
        try:
            with st.spinner("💾 Criando receita..."):
                time.sleep(1)
                new_revenue = revenues_service.create_revenue(revenue_data)

            st.toast("✅ Receita criada com sucesso!")
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao criar receita: {e}")
            logger.error(f"Erro ao criar receita: {e}")
            
    def _render_inline_edit_form_revenue(self, revenue: Dict[str, Any]) -> None:
        """
        Renderiza formulário de edição inline para uma receita.
        """
        revenue_id = revenue.get('id')

        st.markdown("#### ✏️ Editando Receita")

        with st.form(f"edit_revenue_form_{revenue_id}"):
            col1, col2 = st.columns(2)

            with col1:
                new_description = st.text_input(
                    "📝 Descrição",
                    value=revenue.get('description', ''),
                    help="Descrição da receita"
                )

                new_value = st.number_input(
                    "💰 Valor",
                    min_value=0.01,
                    value=float(revenue.get('value', 0)),
                    step=0.01,
                    format="%.2f",
                    help="Valor da receita"
                )

                current_category = revenue.get('category', 'deposit')
                current_category_display = db_categories.REVENUE_CATEGORIES.get(current_category, current_category)
                new_category_display = st.selectbox(
                    "📂 Categoria",
                    options=list(db_categories.TRANSLATED_REVENUE_CATEGORIES.keys()),
                    index=list(
                        db_categories.TRANSLATED_REVENUE_CATEGORIES.keys()
                    ).index(current_category_display),
                    help="Categoria da receita"
                )
                new_category = db_categories.TRANSLATED_REVENUE_CATEGORIES[new_category_display]

            with col2:
                # Parse da data atual da receita
                date_value = revenue.get('date', '')
                try:
                    current_date = datetime.strptime(date_value, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        current_date = datetime.strptime(date_value, '%d/%m/%Y').date()
                    except ValueError:
                        current_date = datetime.now().date()

                new_date = st.date_input(
                    "📅 Data",
                    value=current_date,
                    help="Data da receita",
                    format="DD/MM/YYYY"
                )

                # Conta
                try:
                    accounts = accounts_service.get_all_accounts()
                    account_options = [(acc['id'], db_categories.INSTITUTIONS.get(acc['name'], acc['name'])) for acc in accounts if acc.get('is_active', True)]
                    current_account_index = (
                        next((i for i, (acc_id, _) in enumerate(
                            account_options
                        ) if acc_id == revenue.get('account')), 0)
                    )

                    selected_account = st.selectbox(
                        "🏦 Conta",
                        options=account_options,
                        index=current_account_index,
                        format_func=lambda x: x[1],
                        help="Conta de destino da receita"
                    )
                    new_account = selected_account[0]
                except Exception:
                    st.error("Erro ao carregar contas")
                    new_account = revenue.get('account')

            new_is_received = st.checkbox(
                "✅ Receita Recebida",
                value=revenue.get('received', False),
                help="Marque se a receita foi recebida"
            )

            col_submit, col_cancel = st.columns(2)

            with col_submit:
                if st.form_submit_button(
                    "💾 Salvar Alterações",
                    type="primary",
                    width='stretch'
                ):
                    updated_data = {
                        'description': new_description,
                        'value': new_value,
                        'date': format_date_for_api(new_date),
                        'horary': revenue.get('horary', datetime.now().strftime('%H:%M:%S')),
                        'category': new_category,
                        'account': new_account,
                        'received': new_is_received
                    }
                    self._update_revenue(revenue_id, updated_data)

            with col_cancel:
                if st.form_submit_button(
                    "❌ Cancelar",
                    width='stretch'
                ):
                    st.session_state.pop(f'edit_revenue_{revenue_id}', None)
                    st.rerun()

    def _update_revenue(self, revenue_id: int, revenue_data: Dict[str, Any]) -> None:
        """Atualiza uma receita existente."""
        try:
            with st.spinner("💾 Salvando alterações..."):
                updated_revenue = revenues_service.update_revenue(
                    revenue_id, revenue_data
                )

            st.success("✅ Receita atualizada com sucesso!")

            # Remove o estado de edição e recarrega
            st.session_state.pop(f'edit_revenue_{revenue_id}', None)
            st.rerun()

        except Exception as e:
            st.error(f"🔧 Erro ao atualizar receita: {e}")
            logger.error(f"Erro ao atualizar receita {revenue_id}: {e}")

    def _toggle_revenue_received(self, revenue_id: int, is_received: bool) -> None:
        """Alterna o status de recebimento de uma receita."""
        try:
            with st.spinner(
                f"""{"Confirmando recebimento" if is_received else "Marcando como pendente"}..."""
            ):
                # Primeiro obtém os dados completos da receita
                revenue_data = revenues_service.get_revenue_by_id(revenue_id)
                
                # Atualiza apenas o status de recebimento mantendo os outros campos
                update_data = {
                    'description': revenue_data.get('description'),
                    'value': revenue_data.get('value'),
                    'date': revenue_data.get('date'),
                    'horary': revenue_data.get('horary'),
                    'category': revenue_data.get('category'),
                    'account': revenue_data.get('account'),
                    'received': is_received
                }
                
                revenues_service.update_revenue(revenue_id, update_data)

            status_text = "recebida" if is_received else "pendente"
            st.success(f"✅ Receita marcada como {status_text}!")
            st.rerun()

        except Exception as e:
            st.error(f"🔧 Erro ao alterar status da receita: {e}")
            logger.error(f"Erro ao alterar status da receita {revenue_id}: {e}")

    def _delete_revenue(self, revenue_id: int, description: str) -> None:
        """Exclui uma receita após confirmação."""
        # Define estado da confirmação de exclusão
        confirm_key = f"confirm_delete_revenue_{revenue_id}"
        
        # Se não está no modo de confirmação, marca para confirmar
        if not st.session_state.get(confirm_key, False):
            st.session_state[confirm_key] = True
            st.rerun()
        
        # Mostra modal de confirmação
        st.warning(
            f"""⚠️ **Tem certeza que deseja excluir a receita '{description}'?**"""
        )
        st.error("🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🗑️ Sim, Excluir",
                key=f"final_confirm_delete_revenue_{revenue_id}",
                type="primary",
                width='stretch'
            ):
                try:
                    with st.spinner("🗑️ Excluindo receita..."):
                        revenues_service.delete_revenue(revenue_id)

                    st.success(f"✅ Receita '{description}' excluída com sucesso!")
                    
                    # Limpa o estado de confirmação
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

                except Exception as e:
                    st.error(f"🔧 Erro ao excluir receita: {e}")
                    logger.error(f"Erro ao excluir receita {revenue_id}: {e}")
                    # Limpa o estado de confirmação mesmo com erro
                    st.session_state.pop(confirm_key, None)

        with col2:
            if st.button(
                "❌ Cancelar",
                key=f"cancel_delete_revenue_{revenue_id}",
                width='stretch'
            ):
                # Limpa o estado de confirmação
                st.session_state.pop(confirm_key, None)
                st.rerun()

    def _generate_revenue_pdf(self, revenue: Dict[str, Any]) -> None:
        """Gera e oferece download do PDF da receita."""
        if pdf_generator is None:
            st.error("❌ Gerador de PDF não disponível. Instale o ReportLab: pip install reportlab")
            return
        
        try:
            with st.spinner("📄 Gerando comprovante..."):
                # Buscar dados da conta
                account_data = None
                account_id = revenue.get('account')
                if account_id:
                    try:
                        accounts = accounts_service.get_all_accounts()
                        account_data = next((acc for acc in accounts if acc['id'] == account_id), None)
                    except Exception:
                        pass
                
                # Gerar PDF
                pdf_buffer = pdf_generator.generate_revenue_receipt(revenue, account_data)
                
                # Nome do arquivo
                description = revenue.get('description', 'receita')
                date_str = revenue.get('date', '').replace('-', '_')
                filename = f"comprovante_receita_{description}_{date_str}.pdf"
                
                # Oferecer download
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_revenue_{revenue.get('id')}"
                )
                
                # Preview do PDF
                st.success("✅ Comprovante gerado com sucesso!")
                try:
                    pdf_buffer.seek(0)
                    # Usar st.pdf se disponível (versões mais recentes do Streamlit)
                    if hasattr(st, 'pdf'):
                        st.pdf(pdf_buffer.getvalue())
                    else:
                        st.info("📄 PDF gerado. Use o botão de download para visualizar.")
                except Exception as e:
                    logger.warning(f"Erro ao exibir preview do PDF: {e}")
                    st.info("📄 PDF gerado. Use o botão de download para visualizar.")
                
        except Exception as e:
            st.error(f"❌ Erro ao gerar comprovante: {e}")
            logger.error(f"Erro ao gerar PDF da receita {revenue.get('id')}: {e}")
