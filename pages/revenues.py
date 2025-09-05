"""
Módulo de gerenciamento de receitas.

Este módulo implementa o CRUD completo para receitas,
seguindo o padrão visual padronizado com tabs centralizadas
e layout de 3 colunas para listagem.
"""

import logging
from datetime import date, time, datetime
from typing import Dict, List

import streamlit as st

from components.auth import require_auth
from services.revenues_service import revenues_service
from services.api_client import api_client, ApiClientError, ValidationError
from utils.ui_utils import ui_components, centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


class RevenuesPage:
    """Página de gerenciamento de receitas com padrão visual padronizado."""

    def __init__(self):
        """Inicializa a página de receitas."""
        self.auth = require_auth()

    def main_menu(self, token=None, permissions=None):
        """
        Renderiza o menu principal da página de receitas.

        Parameters
        ----------
        token : str, optional
            Token de autenticação do usuário
        permissions : Dict[str, Any], optional
            Permissões do usuário
        """
        self.render()

    def render(self):
        """
        Renderiza a página principal de receitas com padrão padronizado.

        Segue o padrão visual estabelecido:
        - Duas tabs centralizadas (listagem + novo registro)
        - Layout de 3 colunas para listagem
        - Popup de ações com CRUD
        """
        ui_components.render_page_header(
            "💰 Receitas",
            subtitle="Controle e gerenciamento de receitas"
        )

        # Tabs principais - padrão estabelecido: 2 tabs centralizadas
        tab_list, tab_add = centered_tabs([
            "📋 Listagem de Receitas",
            "➕ Nova Receita"
        ])

        with tab_list:
            self._render_revenues_list_standardized()

        with tab_add:
            self._render_add_revenue_form_standardized()

    def _render_revenues_list_standardized(self):
        """
        Renderiza a lista de receitas seguindo padrão padronizado.

        Padrão estabelecido:
        - Layout de 3 colunas por registro
        - Primeira coluna: descrição + emoji da categoria
        - Segunda coluna (central): dados como valor, data
        - Terceira coluna (direita): botão de engrenagem com popup de ações
        """
        st.markdown("### 📋 Listagem de Receitas")

        # Filtros simplificados em uma linha
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            date_from = st.date_input(
                "📅 Data Inicial",
                value=datetime.now().replace(day=1),
                format="DD/MM/YYYY",
                help="Filtrar receitas a partir desta data"
            )

        with col_filter2:
            date_to = st.date_input(
                "📅 Data Final",
                value=datetime.now(),
                format="DD/MM/YYYY",
                help="Filtrar receitas até esta data"
            )

        with col_filter3:
            category_options = (
                ['Todas'] + list(db_categories.REVENUE_CATEGORIES.values())
            )
            category_filter = st.selectbox(
                "🏷️ Categoria",
                options=category_options,
                format_func=lambda x: f"{self._get_category_emoji(x)} {x}"
            )

        # Busca receitas
        try:
            with st.spinner("🔄 Carregando receitas..."):
                filter_params = {}

                if date_from:
                    filter_params['date_from'] = date_from
                if date_to:
                    filter_params['date_to'] = date_to
                if category_filter != 'Todas':
                    # Converte categoria display para API
                    api_category = None
                    for key, value in db_categories.REVENUE_CATEGORIES.items():
                        if value == category_filter:
                            api_category = key
                            break
                    filter_params['category'] = (
                        api_category if api_category else category_filter
                    )

                revenues = revenues_service.get_all_revenues(**filter_params)

            if not revenues:
                st.info(
                    "📋 Nenhuma receita encontrada com os filtros aplicados."
                )
                return

            st.markdown("---")

            # Renderiza receitas no padrão de 3 colunas
            self._render_revenues_three_column_layout(revenues)

        except Exception as e:
            ui_components.show_persistent_error(
                error_message=f"Erro ao carregar receitas: {str(e)}",
                error_type="carregar_receitas",
                details=f"Detalhes técnicos: {type(e).__name__}: {str(e)}",
                suggestions=[
                    "Verifique se a API está funcionando",
                    "Confirme sua conexão com a internet",
                    "Tente recarregar a página (F5)"
                ])
            logger.error(f"Erro ao carregar receitas: {e}")

    def _render_revenues_three_column_layout(self, revenues: List[Dict]):
        """
        Renderiza receitas no layout padronizado de 3 colunas.

        Parameters
        ----------
        revenues : List[Dict]
            Lista de receitas para exibir
        """
        for revenue in revenues:
            # Container para cada receita
            with st.container():
                col1, col2, col3 = st.columns([3, 3, 1])

                with col1:
                    # Primeira coluna: descrição + emoji da categoria
                    category = revenue.get('category', 'deposit')
                    category_display = db_categories.REVENUE_CATEGORIES.get(
                        category, 'Depósito'
                    )
                    emoji = self._get_category_emoji(category_display)
                    received_status = "✅ Recebido" if revenue.get(
                        'received', False
                    ) else "⏳ Pendente"

                    # Fonte da receita
                    st.markdown(f"""
                    **Descrição: {
                        emoji
                    } {
                        revenue.get('description', 'N/A')
                    }**

                    📂 Categoria: {
                        db_categories.REVENUE_CATEGORY_EMOJIS.get(
                            category,
                            'deposit'
                        )
                    } {category_display}

                    Status: {received_status}

                    """)

                with col2:
                    # Valor líquido se disponível
                    net_amount = revenue.get('net_amount')
                    net_display = (
                        f"💚 Líquido: R$ {float(net_amount):.2f}" if (
                            net_amount
                        ) else ""
                    )
                    # Segunda coluna (central): dados principais
                    value = revenue.get('value', 0)
                    revenue_date = revenue.get('date', 'N/A')
                    revenue_date_iso = datetime.strptime(
                        revenue_date, '%Y-%m-%d'
                    )
                    br_revenue_date = revenue_date_iso.strftime('%d/%m/%Y')
                    st.markdown(f"""
                    **💰 Valor: R$ {float(value):.2f}**

                    {net_display}

                    Data: 📅 {br_revenue_date}
                    """)

                with col3:
                    # Terceira coluna (direita): botão de ações
                    if st.button(
                        "⚙️",
                        key=f"actions_{revenue['id']}",
                        help="Opções de ações",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'show_actions_{revenue["id"]}'
                        ] = True
                        st.rerun()

                # Popup de ações para esta receita
                self._render_revenue_action_popup(revenue)

                st.markdown("---")

    def _render_revenue_action_popup(self, revenue: Dict):
        """
        Renderiza popup de ações para uma receita específica.

        Parameters
        ----------
        revenue : Dict
            Dados da receita
        """
        popup_key = f'show_actions_{revenue["id"]}'

        if st.session_state.get(popup_key, False):
            with st.expander(
                f"⚙️ Ações para: {revenue.get('description', 'N/A')}",
                expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📝 Editar",
                        key=f"edit_{revenue['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'edit_revenue_{revenue["id"]}'
                        ] = revenue
                        st.session_state[popup_key] = False
                        st.rerun()

                with col2:
                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_{revenue['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'delete_revenue_{revenue["id"]}'
                        ] = revenue
                        st.session_state[popup_key] = False
                        st.rerun()

                with col3:
                    if st.button(
                        "❌ Fechar",
                        key=f"close_{revenue['id']}",
                        use_container_width=True
                    ):
                        st.session_state[popup_key] = False
                        st.rerun()

        # Renderiza modals de edição e exclusão
        self._render_edit_revenue_modal(revenue)
        self._render_delete_revenue_modal(revenue)

    def _render_edit_revenue_modal(self, revenue: Dict):
        """
        Renderiza modal de edição para uma receita.

        Parameters
        ----------
        revenue : Dict
            Dados da receita para editar
        """
        edit_key = f'edit_revenue_{revenue["id"]}'

        if st.session_state.get(edit_key):
            st.markdown("### ✏️ Editar Receita")

            with st.form(f"edit_form_{revenue['id']}", clear_on_submit=False):
                col1, col2 = st.columns(2)

                with col1:
                    description = st.text_input(
                        "📝 Descrição *",
                        value=revenue.get('description', ''),
                        help="Descrição da receita"
                    )

                    value = st.number_input(
                        "💰 Valor (R$) *",
                        value=float(revenue.get('value', 0)),
                        min_value=0.01,
                        max_value=999999.99,
                        step=0.01,
                        format="%.2f"
                    )

                with col2:
                    # Categoria com emoji
                    current_category_api = revenue.get('category', 'deposit')
                    current_category_display = (
                        db_categories.REVENUE_CATEGORIES.get(
                            current_category_api, 'Depósito'
                        )
                    )

                    categories_list = list(
                        db_categories.REVENUE_CATEGORIES.values()
                    )
                    category_index = (
                        categories_list.index(current_category_display)
                        if current_category_display in categories_list else 0
                    )

                    category = st.selectbox(
                        "🏷️ Categoria *",
                        options=categories_list,
                        index=category_index,
                        format_func=(
                            lambda x: f"{self._get_category_emoji(x)} {x}"
                        )
                    )

                    received = st.checkbox(
                        "✅ Receita recebida",
                        value=revenue.get('received', False)
                    )

                # Campos adicionais
                with st.expander("📋 Informações Adicionais"):
                    col_add1, col_add2 = st.columns(2)

                    with col_add1:
                        source = st.text_input(
                            "🏢 Fonte",
                            value=revenue.get('source', ''),
                            help="Origem da receita"
                        )

                        tax_amount = st.number_input(
                            "💸 Impostos (R$)",
                            value=float(revenue.get('tax_amount', 0)),
                            min_value=0.00,
                            step=0.01,
                            format="%.2f"
                        )

                    with col_add2:
                        net_amount = st.number_input(
                            "💚 Valor Líquido (R$)",
                            value=float(revenue.get('net_amount', 0)),
                            min_value=0.00,
                            step=0.01,
                            format="%.2f"
                        )

                    notes = st.text_area(
                        "📝 Observações",
                        value=revenue.get('notes', ''),
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
                    self._handle_edit_revenue_submission(
                        revenue['id'],
                        description or '',
                        value,
                        revenue['date'],
                        revenue['horary'],
                        revenue['account'],
                        category,
                        received,
                        source or '',
                        tax_amount,
                        net_amount,
                        notes or '',
                        edit_key
                    )

                if cancelled:
                    st.session_state.pop(edit_key, None)
                    st.rerun()

    def _render_delete_revenue_modal(self, revenue: Dict):
        """
        Renderiza modal de confirmação de exclusão.

        Parameters
        ----------
        revenue : Dict
            Dados da receita para excluir
        """
        delete_key = f'delete_revenue_{revenue["id"]}'

        if st.session_state.get(delete_key):
            st.markdown("### 🗑️ Confirmar Exclusão")

            st.warning(
                f"**Tem certeza que deseja excluir a receita "
                f"'{revenue.get('description', 'N/A')}'?**\n\n"
                f"💰 Valor: R$ {float(revenue.get('value', 0)):.2f}\n"
                f"📅 Data: {revenue.get('date', 'N/A')}\n\n"
                f"⚠️ **Esta ação não pode ser desfeita!**"
            )

            col_confirm, col_cancel = st.columns(2)

            with col_confirm:
                if st.button(
                    "🗑️ Confirmar Exclusão",
                    type="primary",
                    key=f"confirm_delete_{revenue['id']}",
                    use_container_width=True
                ):
                    self._handle_delete_revenue(revenue['id'], delete_key)

            with col_cancel:
                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_delete_{revenue['id']}",
                    use_container_width=True
                ):
                    st.session_state.pop(delete_key, None)
                    st.rerun()

    def _render_add_revenue_form_standardized(self):
        """Renderiza formulário padronizado de adição de receita."""
        ui_components.render_enhanced_form_container(
            "Cadastrar Nova Receita", "➕"
        )

        with st.form("add_revenue_form_standardized", clear_on_submit=True):
            # Seção de dados principais
            st.markdown("#### 💰 Dados da Receita")

            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input(
                    "📝 Descrição *",
                    help="Descrição clara da receita"
                )

                value = st.number_input(
                    "💰 Valor (R$) *",
                    min_value=0.01,
                    max_value=999999.99,
                    step=0.01,
                    format="%.2f"
                )

                revenue_date = st.date_input(
                    "📅 Data *",
                    value=date.today(),
                    format="DD/MM/YYYY"
                )

            with col2:
                # Categoria com emoji
                categories_list = list(
                    db_categories.REVENUE_CATEGORIES.values())
                category = st.selectbox(
                    "🏷️ Categoria *",
                    options=categories_list,
                    format_func=lambda x: f"{self._get_category_emoji(x)} {x}"
                )

                # Busca contas para seleção
                try:
                    accounts_response = api_client.get("accounts/")
                    accounts = (
                        accounts_response.get('results', accounts_response)
                        if isinstance(accounts_response, dict)
                        else accounts_response
                    )

                    if accounts:
                        account_options = {
                            account['id']: (
                                f"{account['account_name']}"
                            )
                            for account in accounts
                            if account.get('is_active', True)
                        }

                        account_id = st.selectbox(
                            "🏦 Conta *",
                            options=list(account_options.keys()),
                            format_func=lambda x: account_options[x]
                        )
                    else:
                        st.error("❌ Nenhuma conta ativa encontrada!")
                        account_id = None

                except Exception as e:
                    st.error(f"❌ Erro ao carregar contas: {str(e)}")
                    account_id = None

                received = st.checkbox("✅ Receita já recebida")

            # Campos opcionais
            with st.expander("📋 Informações Adicionais (Opcional)"):
                col_opt1, col_opt2 = st.columns(2)

                with col_opt1:
                    horary = st.time_input(
                        "🕐 Horário",
                        value=time(12, 0)
                    )

                    source = st.text_input(
                        "🏢 Fonte",
                        help="Origem da receita (empresa, pessoa, etc.)"
                    )

                with col_opt2:
                    net_amount = st.number_input(
                        "💚 Valor Líquido (R$)",
                        min_value=0.00,
                        step=0.01,
                        format="%.2f",
                        help="Valor recebido após descontos"
                    )

                    tax_amount = st.number_input(
                        "💸 Impostos (R$)",
                        min_value=0.00,
                        step=0.01,
                        format="%.2f",
                        help="Valor dos impostos descontados"
                    )

                recurring = st.checkbox(
                        "🔄 Receita Recorrente",
                        help="Marque se esta receita se repete mensalmente"
                    )

                if recurring:
                    frequency = st.selectbox(
                        "📆 Frequência",
                        options=['monthly', 'quarterly', 'yearly'],
                        format_func=lambda x: {
                            'monthly': 'Mensal',
                            'quarterly': 'Trimestral',
                            'yearly': 'Anual'
                        }.get(x, x) or x
                    )
                else:
                    frequency = None

                notes = st.text_area(
                    "📝 Observações",
                    help="Informações adicionais sobre a receita"
                )

            # Botão de submissão
            submitted = st.form_submit_button(
                "💾 Salvar Receita",
                type="primary",
                use_container_width=True
            )

            if submitted:
                self._handle_add_revenue_submission(
                    description,
                    value,
                    revenue_date,
                    category,
                    account_id,  # type: ignore
                    received,
                    horary,
                    source,
                    tax_amount,
                    net_amount,
                    recurring,
                    frequency,  # type: ignore
                    notes
                )

    def _get_category_emoji(self, category_display: str) -> str:
        """
        Obtém emoji para categoria de receita.

        Parameters
        ----------
        category_display : str
            Nome da categoria em português

        Returns
        -------
        str
            Emoji correspondente à categoria
        """
        if category_display == 'Todas':
            return "🗂️"

        # Busca a chave da categoria
        category_key = None
        for key, value in db_categories.REVENUE_CATEGORIES.items():
            if value == category_display:
                category_key = key
                break

        return db_categories.REVENUE_CATEGORY_EMOJIS.get(
            category_key, "💰"
        ) if category_key else "💰"

    def _handle_add_revenue_submission(
        self, description: str, value: float, revenue_date: date,
        category: str, account_id: int, received: bool,
        horary: time, source: str, tax_amount: float,
        net_amount: float, recurring: bool, frequency: str,
        notes: str
    ):
        """
        Processa submissão do formulário de nova receita.

        Parameters
        ----------
        description : str
            Descrição da receita
        value : float
            Valor da receita
        revenue_date : date
            Data da receita
        category : str
            Categoria selecionada
        account_id : int
            ID da conta selecionada
        received : bool
            Status de recebimento
        horary : time
            Horário da receita
        source : str
            Fonte da receita
        tax_amount : float
            Valor dos impostos
        net_amount : float
            Valor líquido
        recurring : bool
            Se é recorrente
        frequency : str
            Frequência da recorrência
        notes : str
            Observações
        """
        if not description or not value or not account_id:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte categoria para código da API
            category_code = None
            for key, val in db_categories.REVENUE_CATEGORIES.items():
                if val == category:
                    category_code = key
                    break

            revenue_data = {
                'description': description,
                'value': str(value),
                'date': revenue_date.isoformat(),
                'horary': horary.strftime('%H:%M:%S'),
                'category': category_code or 'deposit',
                'account': account_id,
                'received': received,
                'source': source or '',
                'tax_amount': str(tax_amount) if tax_amount else '0.00',
                'net_amount': str(net_amount) if net_amount else '0.00',
                'recurring': recurring,
                'frequency': frequency if recurring else '',
                'notes': notes or ''
            }

            with st.spinner("💾 Salvando receita..."):
                result = revenues_service.create_revenue(revenue_data)

            if result:
                st.success(
                    f"✅ Receita '{description}' cadastrada com sucesso!"
                )
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar receita!")

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
            logger.error(f"Erro ao criar receita: {e}")

    def _handle_edit_revenue_submission(
        self,
        revenue_id: int,
        description: str,
        value: float,
        date: str,
        horary: str,
        account: str,
        category: str,
        received: bool,
        source: str,
        tax_amount: float,
        net_amount: float,
        notes: str,
        edit_key: str
    ):
        """
        Processa submissão da edição de receita.

        Parameters
        ----------
        revenue_id : int
            ID da receita
        description : str
            Nova descrição
        value : float
            Novo valor
        category : str
            Nova categoria
        received : bool
            Novo status de recebimento
        source : str
            Nova fonte
        tax_amount : float
            Novo valor de impostos
        net_amount : float
            Novo valor líquido
        notes : str
            Novas observações
        edit_key : str
            Chave da sessão para limpeza
        """
        if not description or not value:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte categoria para código da API
            category_code = None
            for key, val in db_categories.REVENUE_CATEGORIES.items():
                if val == category:
                    category_code = key
                    break

            update_data = {
                'description': description,
                'value': str(value),
                'date': date,
                'horary': horary,
                'account': account,
                'category': category_code or 'deposit',
                'received': received,
                'source': source or '',
                'tax_amount': str(tax_amount),
                'net_amount': str(net_amount),
                'notes': notes or ''
            }

            with st.spinner("💾 Salvando alterações..."):
                result = revenues_service.update_revenue(
                    revenue_id, update_data)

            if result:
                st.success("✅ Receita atualizada com sucesso!")
                st.session_state.pop(edit_key, None)
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar receita!")

        except Exception as e:
            st.error(f"❌ Erro ao atualizar: {str(e)}")
            logger.error(f"Erro ao atualizar receita {revenue_id}: {e}")

    def _handle_delete_revenue(self, revenue_id: int, delete_key: str):
        """
        Processa exclusão de receita.

        Parameters
        ----------
        revenue_id : int
            ID da receita para excluir
        delete_key : str
            Chave da sessão para limpeza
        """
        try:
            with st.spinner("🗑️ Excluindo receita..."):
                revenues_service.delete_revenue(revenue_id)

            st.success("✅ Receita excluída com sucesso!")
            st.session_state.pop(delete_key, None)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao excluir: {str(e)}")
            logger.error(f"Erro ao excluir receita {revenue_id}: {e}")


# Função de entrada principal
def show():
    """Função de entrada para a página de receitas."""
    page = RevenuesPage()
    page.render()


# Compatibilidade com estrutura existente
revenues_page = RevenuesPage()
