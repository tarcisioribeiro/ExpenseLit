"""
Módulo de gerenciamento de despesas.

Este módulo implementa o CRUD completo para despesas,
seguindo o padrão visual padronizado com tabs centralizadas
e layout de 3 colunas para listagem.
"""

import logging
from datetime import date, time, datetime
from typing import Dict, Any, List

import streamlit as st

from components.auth import require_auth
from services.expenses_service import expenses_service
from services.api_client import api_client, ApiClientError, ValidationError
from utils.ui_utils import ui_components, centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


class ExpensesPage:
    """Página de gerenciamento de despesas com padrão visual padronizado."""

    def __init__(self):
        """Inicializa a página de despesas."""
        self.auth = require_auth()

    def main_menu(
            self,
            token: str = None,  # type: ignore
            permissions: Dict[str, Any] = None  # type: ignore
    ):
        """Renderiza o menu principal da página de despesas."""
        self.render()

    def render(self):
        """
        Renderiza a página principal de despesas com padrão padronizado.

        Segue o padrão visual estabelecido:
        - Duas tabs centralizadas (listagem + novo registro)
        - Layout de 3 colunas para listagem
        - Popup de ações com CRUD
        """
        # Verifica e exibe erros armazenados de diálogos
        self._check_and_show_stored_errors()

        ui_components.render_page_header(
            "💸 Despesas",
            subtitle="Controle e gerenciamento de gastos"
        )

        # Tabs principais - padrão estabelecido: 2 tabs centralizadas
        tab_list, tab_add = centered_tabs([
            "📋 Listagem de Despesas",
            "➕ Nova Despesa"
        ])

        with tab_list:
            self._render_expenses_list_standardized()

        with tab_add:
            self._render_add_expense_form_standardized()

    def _check_and_show_stored_errors(self):
        """Verifica e exibe erros armazenados de diálogos."""
        if 'validation_error' in st.session_state:
            error_data = st.session_state.pop('validation_error')
            ui_components.show_persistent_error(
                error_message=error_data['message'],
                error_type="validacao_despesa",
                details=error_data.get('details'),
                suggestions=error_data.get('suggestions', []),
                auto_show=False
            )

    def _render_expenses_list_standardized(self):
        """
        Renderiza a lista de despesas seguindo padrão padronizado.

        Padrão estabelecido:
        - Layout de 3 colunas por registro
        - Primeira coluna: descrição + emoji da categoria
        - Segunda coluna (central): dados como valor, data
        - Terceira coluna (direita): botão de engrenagem com popup de ações
        """
        st.markdown("### 📋 Listagem de Despesas")

        # Filtros simplificados em uma linha
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            date_from = st.date_input(
                "📅 Data Inicial",
                value=datetime.now().replace(day=1),
                format="DD/MM/YYYY",
                help="Filtrar despesas a partir desta data"
            )

        with col_filter2:
            date_to = st.date_input(
                "📅 Data Final",
                value=datetime.now(),
                format="DD/MM/YYYY",
                help="Filtrar despesas até esta data"
            )

        with col_filter3:
            category_options = (
                ['Todas'] + list(db_categories.EXPENSE_CATEGORIES.values())
            )
            category_filter = st.selectbox(
                "🏷️ Categoria",
                options=category_options,
                format_func=lambda x: f"{self._get_category_emoji(x)} {x}"
            )

        # Busca despesas
        try:
            with st.spinner("🔄 Carregando despesas..."):
                filter_params = {}

                if date_from:
                    filter_params['date_from'] = date_from
                if date_to:
                    filter_params['date_to'] = date_to
                if category_filter != 'Todas':
                    # Converte categoria display para API
                    api_category = None
                    for key, value in db_categories.EXPENSE_CATEGORIES.items():
                        if value == category_filter:
                            api_category = key
                            break
                    filter_params['category'] = (
                        api_category if api_category else category_filter
                    )

                expenses = expenses_service.get_all_expenses(**filter_params)

            if not expenses:
                st.info(
                    "📋 Nenhuma despesa encontrada com os filtros aplicados."
                )
                return

            st.markdown("---")

            # Renderiza despesas no padrão de 3 colunas
            self._render_expenses_three_column_layout(expenses)

        except Exception as e:
            ui_components.show_persistent_error(
                error_message=f"Erro ao carregar despesas: {str(e)}",
                error_type="carregar_despesas",
                details=f"Detalhes técnicos: {type(e).__name__}: {str(e)}",
                suggestions=[
                    "Verifique se a API está funcionando",
                    "Confirme sua conexão com a internet",
                    "Tente recarregar a página (F5)"
                ])
            logger.error(f"Erro ao carregar despesas: {e}")

    def _render_expenses_three_column_layout(self, expenses: List[Dict]):
        """
        Renderiza despesas no layout padronizado de 3 colunas.

        Parameters
        ----------
        expenses : List[Dict]
            Lista de despesas para exibir
        """
        for expense in expenses:
            # Container para cada despesa
            with st.container():
                col1, col2, col3 = st.columns([3, 3, 1])

                with col1:
                    # Primeira coluna: descrição + emoji da categoria
                    category = expense.get('category', 'others')
                    category_display = db_categories.EXPENSE_CATEGORIES.get(
                        category, 'Outros'
                    )
                    emoji = self._get_category_emoji(category_display)

                    st.markdown(f"""
                    **Descrição: {emoji} {expense.get('description', 'N/A')}**

                    📂 Categoria: {category_display}
                    """)

                with col2:
                    # Segunda coluna (central): dados principais
                    value = expense.get('value', 0)
                    expense_date = expense.get('date', 'N/A')
                    expense_date_iso = datetime.strptime(
                        expense_date,
                        '%Y-%m-%d'
                    )
                    br_expense_date = expense_date_iso.strftime(
                        '%d/%m/%Y'
                    )
                    payed_status = "✅ Pago" if expense.get(
                        'payed', False
                    ) else "⏳ Pendente"

                    st.markdown(f"""
                    **💰 Valor: R$ {float(value):.2f}**

                    📅 Data: {br_expense_date}

                    Status: {payed_status}
                    """)

                with col3:
                    # Terceira coluna (direita): botão de ações
                    if st.button(
                        "⚙️",
                        key=f"actions_{expense['id']}",
                        help="Opções de ações",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'show_actions_{expense["id"]}'
                        ] = True
                        st.rerun()

                # Popup de ações para esta despesa
                self._render_expense_action_popup(expense)

                st.markdown("---")

    def _render_expense_action_popup(self, expense: Dict):
        """
        Renderiza popup de ações para uma despesa específica.

        Parameters
        ----------
        expense : Dict
            Dados da despesa
        """
        popup_key = f'show_actions_{expense["id"]}'

        if st.session_state.get(popup_key, False):
            with st.expander(
                f"⚙️ Ações para: {expense.get('description', 'N/A')}",
                expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📝 Editar",
                        key=f"edit_{expense['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'edit_expense_{expense["id"]}'
                        ] = expense
                        st.session_state[popup_key] = False
                        st.rerun()

                with col2:
                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_{expense['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'delete_expense_{expense["id"]}'
                        ] = expense
                        st.session_state[popup_key] = False
                        st.rerun()

                with col3:
                    if st.button(
                        "❌ Fechar",
                        key=f"close_{expense['id']}",
                        use_container_width=True
                    ):
                        st.session_state[popup_key] = False
                        st.rerun()

        # Renderiza modals de edição e exclusão
        self._render_edit_expense_modal(expense)
        self._render_delete_expense_modal(expense)

    def _render_edit_expense_modal(self, expense: Dict):
        """
        Renderiza modal de edição para uma despesa.

        Parameters
        ----------
        expense : Dict
            Dados da despesa para editar
        """
        edit_key = f'edit_expense_{expense["id"]}'

        if st.session_state.get(edit_key):
            st.markdown("### ✏️ Editar Despesa")

            with st.form(f"edit_form_{expense['id']}", clear_on_submit=False):
                col1, col2 = st.columns(2)

                with col1:
                    description = st.text_input(
                        "📝 Descrição *",
                        value=expense.get('description', ''),
                        help="Descrição da despesa"
                    )

                    value = st.number_input(
                        "💰 Valor (R$) *",
                        value=float(expense.get('value', 0)),
                        min_value=0.01,
                        max_value=999999.99,
                        step=0.01,
                        format="%.2f"
                    )

                with col2:
                    # Categoria com emoji
                    current_category_api = expense.get('category', 'others')
                    current_category_display = (
                        db_categories.EXPENSE_CATEGORIES.get(
                            current_category_api, 'Outros'
                        )
                    )

                    categories_list = list(
                        db_categories.EXPENSE_CATEGORIES.values()
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

                    payed = st.checkbox(
                        "✅ Despesa paga",
                        value=expense.get('payed', False)
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
                    self._handle_edit_expense_submission(
                        expense['id'],
                        description or "",
                        value,
                        expense['date'],
                        expense['horary'],
                        category,
                        expense['account'],
                        payed,
                        edit_key
                    )

                if cancelled:
                    st.session_state.pop(edit_key, None)
                    st.rerun()

    def _render_delete_expense_modal(self, expense: Dict):
        """
        Renderiza modal de confirmação de exclusão.

        Parameters
        ----------
        expense : Dict
            Dados da despesa para excluir
        """
        delete_key = f'delete_expense_{expense["id"]}'

        if st.session_state.get(delete_key):
            st.markdown("### 🗑️ Confirmar Exclusão")

            st.warning(
                f"**Tem certeza que deseja excluir a despesa "
                f"'{expense.get('description', 'N/A')}'?**\n\n"
                f"💰 Valor: R$ {float(expense.get('value', 0)):.2f}\n"
                f"📅 Data: {expense.get('date', 'N/A')}\n\n"
                f"⚠️ **Esta ação não pode ser desfeita!**"
            )

            col_confirm, col_cancel = st.columns(2)

            with col_confirm:
                if st.button(
                    "🗑️ Confirmar Exclusão",
                    type="primary",
                    key=f"confirm_delete_{expense['id']}",
                    use_container_width=True
                ):
                    self._handle_delete_expense(expense['id'], delete_key)

            with col_cancel:
                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_delete_{expense['id']}",
                    use_container_width=True
                ):
                    st.session_state.pop(delete_key, None)
                    st.rerun()

    def _render_add_expense_form_standardized(self):
        """Renderiza formulário padronizado de adição de despesa."""
        ui_components.render_enhanced_form_container(
            "Cadastrar Nova Despesa", "➕"
        )

        with st.form("add_expense_form_standardized", clear_on_submit=True):
            # Seção de dados principais
            st.markdown("#### 💰 Dados da Despesa")

            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input(
                    "📝 Descrição *",
                    help="Descrição clara da despesa"
                )

                value = st.number_input(
                    "💰 Valor (R$) *",
                    min_value=0.01,
                    max_value=999999.99,
                    step=0.01,
                    format="%.2f"
                )

                expense_date = st.date_input(
                    "📅 Data *",
                    value=date.today(),
                    format='DD/MM/YYYY'
                )

            with col2:
                # Categoria com emoji
                categories_list = list(
                    db_categories.EXPENSE_CATEGORIES.values())
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
                                f"""{account['account_name']}"""
                            )
                            for account in accounts if (
                                account.get(
                                    'is_active',
                                    True
                                )
                            )
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

                payed = st.checkbox("✅ Despesa já paga")

            # Campos opcionais
            with st.expander("📋 Informações Adicionais (Opcional)"):
                col_opt1, col_opt2 = st.columns(2)

                with col_opt1:
                    horary = st.time_input(
                        "🕐 Horário",
                        value=time(12, 0)
                    )

                    merchant = st.text_input(
                        "🏪 Estabelecimento",
                        help="Nome do estabelecimento/fornecedor"
                    )

                with col_opt2:
                    location = st.text_input(
                        "📍 Localização",
                        help="Cidade ou endereço"
                    )

                    payment_method = st.text_input(
                        "💳 Método de Pagamento",
                        help="Ex: Cartão de Crédito, PIX, Dinheiro"
                    )

                notes = st.text_area(
                    "📝 Observações",
                    help="Informações adicionais sobre a despesa"
                )

            col_submit, col_info = st.columns([1, 2])

            with col_submit:
                # Botão de submissão
                submitted = st.form_submit_button(
                    "💾 Salvar Despesa",
                    type="primary",
                    use_container_width=True
                )

            with col_info:
                st.write("* Campos obrigatórios")

            if submitted:
                self._handle_add_expense_submission(
                    description,
                    value,
                    expense_date,
                    category,
                    account_id,  # type: ignore
                    payed,
                    horary,
                    merchant,
                    location,
                    payment_method,
                    notes
                )

    def _get_category_emoji(self, category_display: str) -> str:
        """
        Obtém emoji para categoria de despesa.

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
        for key, value in db_categories.EXPENSE_CATEGORIES.items():
            if value == category_display:
                category_key = key
                break

        return db_categories.EXPENSE_CATEGORY_EMOJIS.get(
            category_key, "💸"
        ) if category_key else "💸"

    def _handle_add_expense_submission(
        self, description: str, value: float, expense_date: date,
        category: str, account_id: int, payed: bool,
        horary: time, merchant: str, location: str,
        payment_method: str, notes: str
    ):
        """
        Processa submissão do formulário de nova despesa.

        Parameters
        ----------
        description : str
            Descrição da despesa
        value : float
            Valor da despesa
        expense_date : date
            Data da despesa
        category : str
            Categoria selecionada
        account_id : int
            ID da conta selecionada
        payed : bool
            Status de pagamento
        horary : time
            Horário da despesa
        merchant : str
            Estabelecimento
        location : str
            Localização
        payment_method : str
            Método de pagamento
        notes : str
            Observações
        """
        if not description or not value or not account_id:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte categoria para código da API
            category_code = None
            for key, val in db_categories.EXPENSE_CATEGORIES.items():
                if val == category:
                    category_code = key
                    break

            expense_data = {
                'description': description,
                'value': str(value),
                'date': expense_date.isoformat(),
                'horary': horary.strftime('%H:%M:%S'),
                'category': category_code or 'others',
                'account': account_id,
                'payed': payed,
                'merchant': merchant or '',
                'location': location or '',
                'payment_method': payment_method or '',
                'notes': notes or ''
            }

            with st.spinner("💾 Salvando despesa..."):
                result = expenses_service.create_expense(expense_data)

            if result:
                st.success(
                    f"✅ Despesa '{description}' cadastrada com sucesso!"
                )
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar despesa!")

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
            logger.error(f"Erro ao criar despesa: {e}")

    def _handle_edit_expense_submission(
        self,
        expense_id: int,
        description: str,
        value: float,
        date: str,
        horary: str,
        category: str,
        account: str,
        payed: bool,
        edit_key: str
    ):
        """
        Processa submissão da edição de despesa.

        Parameters
        ----------
        expense_id : int
            ID da despesa
        description : str
            Nova descrição
        value : float
            Novo valor
        category : str
            Nova categoria
        payed : bool
            Novo status de pagamento
        edit_key : str
            Chave da sessão para limpeza
        """
        if not description or not value:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte categoria para código da API
            category_code = None
            for key, val in db_categories.EXPENSE_CATEGORIES.items():
                if val == category:
                    category_code = key
                    break

            update_data = {
                'description': description,
                'value': str(value),
                'date': date,
                'horary': horary,
                'category': category_code or 'others',
                'account': account,
                'payed': payed
            }

            with st.spinner("💾 Salvando alterações..."):
                result = expenses_service.update_expense(
                    expense_id, update_data)

            if result:
                st.success("✅ Despesa atualizada com sucesso!")
                st.session_state.pop(edit_key, None)
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar despesa!")

        except Exception as e:
            st.error(f"❌ Erro ao atualizar: {str(e)}")
            logger.error(f"Erro ao atualizar despesa {expense_id}: {e}")

    def _handle_delete_expense(self, expense_id: int, delete_key: str):
        """
        Processa exclusão de despesa.

        Parameters
        ----------
        expense_id : int
            ID da despesa para excluir
        delete_key : str
            Chave da sessão para limpeza
        """
        try:
            with st.spinner("🗑️ Excluindo despesa..."):
                expenses_service.delete_expense(expense_id)
            st.success("✅ Despesa excluída com sucesso!")
            st.session_state.pop(delete_key, None)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao excluir: {str(e)}")
            logger.error(f"Erro ao excluir despesa {expense_id}: {e}")


# Função de entrada principal
def show():
    """Função de entrada para a página de despesas."""
    page = ExpensesPage()
    page.render()


# Compatibilidade com estrutura existente
expenses_page = ExpensesPage()
