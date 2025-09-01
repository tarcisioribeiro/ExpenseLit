"""
Página de gestão de despesas.

Esta página permite ao usuário visualizar, criar, editar e excluir
despesas integradas com a API ExpenseLit.
"""
import logging
import time
from datetime import datetime, timedelta
from utils.date_utils import (
    format_date_for_display,
    format_date_for_api,
    # format_datetime_for_display,
    # get_today_for_display,
    format_currency_br
)
from typing import Dict, Any
import streamlit as st
import pandas as pd
from pages.router import BasePage
from services.api_client import ApiClientError, ValidationError, api_client
from services.expenses_service import expenses_service
from services.accounts_service import accounts_service
from services.pdf_generator import pdf_generator
from utils.ui_utils import centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


@st.dialog("⚠️ Recurso Não Encontrado")
def show_missing_resource_dialog(
    resource_name: str,
    resource_type: str,
    redirect_page: str = None  # type: ignore
):
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

**Ação necessária:** Você precisa criar \
     uma {resource_type} antes de continuar.
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


class ExpensesPage(BasePage):
    """
    Página de gestão de despesas.

    Permite operações CRUD (Create, Read, Update, Delete) em despesas,
    com filtros avançados e integração completa à API ExpenseLit.
    """

    def __init__(self):
        """Inicializa a página de despesas."""
        super().__init__("Gestão de Despesas", "💸")
        self.required_permissions = ['expenses.view_expense']

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
        st.subheader("💸 Gestão de Despesas")
        self.render()

    def render(self) -> None:
        """
        Renderiza o conteúdo da página de despesas.

        Nova estrutura:
        - Despesas em Conta Corrente (lista + criar nova)
        - Despesas de Cartão de Crédito (lista + criar nova)
        """
        # Tabs principais para tipos de despesa
        tab1, tab2 = centered_tabs([
            "💰 Despesas em Conta Corrente",
            "💳 Despesas de Cartão de Crédito"
        ])

        with tab1:
            self._render_checking_account_expenses()

        with tab2:
            self._render_credit_card_expenses_section()

    def _render_checking_account_expenses(self) -> None:
        """Renderiza seção de despesas em conta corrente."""
        # Sub-tabs para lista e criação
        subtab1, subtab2, subtab3 = centered_tabs([
            "📋 Lista de Despesas",
            "➕ Nova Despesa",
            "📊 Resumo"
        ])

        with subtab1:
            self._render_expenses_list()

        with subtab2:
            self._render_expense_form()

        with subtab3:
            self._render_checking_expenses_summary()

    def _render_credit_card_expenses_section(self) -> None:
        """Renderiza seção completa de despesas de cartão."""
        # Sub-tabs para lista e criação
        subtab1, subtab2, subtab3 = centered_tabs([
            "📋 Lista de Despesas",
            "➕ Nova Despesa",
            "📊 Resumo"
        ])

        with subtab1:
            self._render_cc_expenses_list()

        with subtab2:
            self._render_cc_expense_form()

        with subtab3:
            self._render_cc_expenses_summary()

    def _render_expenses_list(self) -> None:
        """Renderiza a lista de despesas com filtros."""
        st.markdown("### 💸 Lista de Despesas")

        # Filtros
        self._render_filters()

        try:
            # Carrega despesas com filtros aplicados
            filters = st.session_state.get('expense_filters', {})

            with st.spinner("🔄 Carregando despesas..."):
                time.sleep(1)
                expenses = expenses_service.get_all_expenses(
                    category=filters.get('category'),
                    payed=filters.get('payed'),
                    account_id=filters.get('account'),
                    date_from=filters.get('date_from'),
                    date_to=filters.get('date_to')
                )
                accounts = accounts_service.get_all_accounts()

            # Cria mapeamento de accounts para exibição
            accounts_map = {acc['id']: acc['name'] for acc in accounts}

            if not expenses:
                st.info(
                    """
                    📝 Nenhuma despesa encontrada
                    com os filtros aplicados.
                    """
                    )
                return

            # Estatísticas rápidas
            total_expenses = sum(
                float(exp.get('value', 0)) for exp in expenses
            )
            paid_expenses = sum(
                float(exp.get('value', 0)) for exp in expenses if exp.get(
                    'payed', False)
                )
            pending_expenses = total_expenses - paid_expenses

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total", format_currency_br(total_expenses))
            with col2:
                st.metric("✅ Pagas", format_currency_br(paid_expenses))
            with col3:
                st.metric("⏳ Pendentes", format_currency_br(pending_expenses))

            st.markdown("---")

            # Lista de despesas
            for expense in expenses:
                self._render_expense_card(expense, accounts_map)

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar despesas: {e}")
            logger.error(f"Erro ao listar despesas: {e}")

    def _render_filters(self) -> None:
        """Renderiza os filtros de despesas."""
        with st.expander("🔍 Filtros de Pesquisa", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                # Filtro por categoria
                translated_categories = ['Todas'] + list(
                    db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys()
                )
                selected_category_display = st.selectbox(
                    "📂 Categoria",
                    options=translated_categories,
                    key="filter_category"
                )
                selected_category = (
                        db_categories.TRANSLATED_EXPENSE_CATEGORIES.get(
                            selected_category_display
                        ) if selected_category_display != 'Todas' else None
                )
            with col2:
                # Filtro por status de pagamento
                payment_status = st.selectbox(
                    "💳 Status de Pagamento",
                    options=["Todos", "Pagas", "Pendentes"],
                    key="filter_payment_status"
                )

            with col3:
                # Filtro por conta
                try:
                    accounts = accounts_service.get_all_accounts()
                    # Cria lista de tuplas (id, nome) para facilitar a exibição
                    account_tuples = [(None, 'Todas')] + [
                        (
                            acc['id'],
                            db_categories.INSTITUTIONS.get(acc['name'], acc[
                                'name'
                            ]
                            )
                        )
                        for acc in accounts if acc.get('is_active', True)
                    ]

                    selected_account_tuple = st.selectbox(
                        "🏦 Conta",
                        options=account_tuples,
                        format_func=lambda x: x[1],  # Mostra apenas o nome
                        key="filter_account"
                    )
                    selected_account = selected_account_tuple
                except ApiClientError:
                    selected_account = (None, 'Todas')

            # Filtros de data
            col1, col2 = st.columns(2)
            with col1:
                date_from = st.date_input(
                    "📅 Data Inicial",
                    value=datetime.now().replace(day=1).date(),
                    key="filter_date_from",
                    format="DD/MM/YYYY"
                )

            with col2:
                date_to = st.date_input(
                    "📅 Data Final",
                    value=datetime.now().date(),
                    key="filter_date_to",
                    format="DD/MM/YYYY"
                )

            # Aplica filtros
            if st.button(
                "🔍 Aplicar Filtros",
                type="primary",
                width='stretch'
            ):
                filters = {}

                if selected_category:
                    filters['category'] = selected_category

                if payment_status == "Pagas":
                    filters['payed'] = True
                elif payment_status == "Pendentes":
                    filters['payed'] = False

                if selected_account and selected_account[0] is not None:
                    filters['account'] = selected_account[0]

                if date_from:
                    filters['date_from'] = format_date_for_api(date_from)

                if date_to:
                    filters['date_to'] = format_date_for_api(date_to)

                st.session_state['expense_filters'] = filters
                st.rerun()

    def _render_expense_card(
            self,
            expense: Dict[str, Any],
            accounts_map: Dict[int, str]
            ) -> None:
        """
        Renderiza um card para uma despesa específica.

        Parameters
        ----------
        expense : Dict[str, Any]
            Dados da despesa
        accounts_map : Dict[int, str]
            Mapeamento de IDs de conta para nomes
        """
        expense_id = expense.get('id')
        description = expense.get('description', 'Despesa')
        value = float(expense.get('value', 0))
        date_str = format_date_for_display(expense.get('date', ''))
        time_str = expense.get('horary', '00:00:00')
        category = expense.get('category', 'others')
        category_name = db_categories.EXPENSE_CATEGORIES.get(
            category, category
        )
        account_id = expense.get('account')
        account_name_code = accounts_map.get(
            account_id, f'Conta {account_id}'  # type: ignore
        )
        # Traduz o código da conta para nome completo
        account_name = db_categories.INSTITUTIONS.get(
            account_name_code, account_name_code
        )
        is_paid = expense.get('payed', False)

        # Container do card
        with st.container():
            # Header do card
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                category_emoji = db_categories.EXPENSE_CATEGORY_EMOJIS.get(
                    category, "💸"
                )
                st.markdown(f"### {category_emoji} {description}")
                st.caption(f"📂 {category_name} | 🏦 {account_name}")

            with col2:
                st.markdown(f"**{format_currency_br(value)}**")
                st.caption(f"📅 {date_str} às {time_str}")

            with col3:
                if is_paid:
                    st.success("✅ Paga")
                else:
                    st.warning("⏳ Pendente")

            with col4:
                # Menu de ações
                with st.popover("⚙️ Ações"):
                    if st.button(
                        "✏️ Editar",
                        key=f"edit_btn_expense_{expense_id}",
                        width='stretch'
                    ):
                        st.session_state[
                            f'edit_expense_{expense_id}'
                        ] = expense
                        st.rerun()

                    # Toggle pago/pendente
                    toggle_text = (
                        "⏳ Marcar Pendente" if is_paid else "✅ Marcar Paga"
                    )
                    if st.button(
                        toggle_text,
                        key=f"toggle_btn_expense_{expense_id}",
                        width='stretch'
                    ):
                        self._toggle_expense_payment(
                            expense_id, not is_paid  # type: ignore
                        )

                    if st.button(
                        "📄 Gerar PDF",
                        key=f"pdf_btn_expense_{expense_id}",
                        width='stretch'
                    ):
                        self._generate_expense_pdf(expense)

                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_btn_expense_{expense_id}",
                        width='stretch'
                    ):
                        self._delete_expense(
                            expense_id, description  # type: ignore
                        )

            # Formulário de edição inline se ativo
            if st.session_state.get(f'edit_expense_{expense_id}'):
                self._render_inline_edit_form(expense)

            st.markdown("---")

    def _render_inline_edit_form(self, expense: Dict[str, Any]) -> None:
        """
        Renderiza formulário de edição inline para uma despesa.

        Parameters
        ----------
        expense : Dict[str, Any]
            Dados da despesa a editar
        """
        expense_id = expense.get('id')

        st.markdown("#### ✏️ Editando Despesa")

        with st.form(f"edit_expense_form_{expense_id}"):
            col1, col2 = st.columns(2)

            with col1:
                new_description = st.text_input(
                    "📝 Descrição",
                    value=expense.get('description', ''),
                    help="Descrição da despesa"
                )

                new_value = st.number_input(
                    "💰 Valor",
                    min_value=0.01,
                    value=float(expense.get('value', 0)),
                    step=0.01,
                    format="%.2f",
                    help="Valor da despesa"
                )

                current_category = expense.get('category', 'others')
                current_category_display = (
                    db_categories.EXPENSE_CATEGORIES.get(
                        current_category,
                        current_category
                    )
                )
                new_category_display = st.selectbox(
                    "📂 Categoria",
                    options=list(
                        db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys()
                    ),
                    index=list(
                        db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys()
                    ).index(
                        current_category_display  # type: ignore
                    ),
                    help="Categoria da despesa"
                )
                new_category = db_categories.TRANSLATED_EXPENSE_CATEGORIES[
                       new_category_display
                ]

            with col2:
                # Data e horário atuais da despesa
                # Parse da data atual da despesa
                date_value = expense.get('date', '')
                try:
                    current_date = datetime.strptime(
                        date_value, '%Y-%m-%d'
                    ).date()
                except ValueError:
                    try:
                        current_date = datetime.strptime(
                            date_value, '%d/%m/%Y'
                        ).date()
                    except ValueError:
                        current_date = datetime.now().date()

                current_time = datetime.strptime(
                    expense.get('horary', '00:00:00'), '%H:%M:%S'
                ).time()

                new_date = st.date_input(
                    "📅 Data",
                    value=current_date,
                    help="Data da despesa",
                    format="DD/MM/YYYY"
                )

                new_time = st.time_input(
                    "🕐 Horário",
                    value=current_time,
                    help="Horário da despesa"
                )

                # Conta
                try:
                    accounts = accounts_service.get_all_accounts()
                    account_options = [
                        (
                            acc['id'],
                            db_categories.INSTITUTIONS.get(acc['name'], acc[
                                'name'
                            ]
                            )
                        ) for acc in accounts if acc.get('is_active', True)]
                    current_account_index = (
                        next((i for i, (acc_id, _) in enumerate(
                            account_options
                        ) if acc_id == expense.get('account')), 0)
                    )

                    selected_account = st.selectbox(
                        "🏦 Conta",
                        options=account_options,
                        index=current_account_index,
                        format_func=lambda x: x[1],
                        help="Conta de origem da despesa"
                    )
                    new_account = selected_account[0]
                except ApiClientError:
                    st.error("Erro ao carregar contas")
                    new_account = expense.get('account')

            # Campos adicionais
            new_merchant = st.text_input(
                "🏦 Estabelecimento",
                value=expense.get('merchant', ''),
                help="Nome do estabelecimento"
            )

            new_location = st.text_input(
                "📍 Local",
                value=expense.get('location', ''),
                help="Local da despesa"
            )

            payment_method_options = [
                ('cash', 'Dinheiro'),
                ('debit_card', 'Cartão de Débito'),
                ('credit_card', 'Cartão de Crédito'),
                ('bank_transfer', 'Transferência Bancária'),
                ('pix', 'PIX'),
                ('check', 'Cheque'),
                ('voucher', 'Vale')
            ]
            current_payment_method = expense.get(
                'payment_method',
                'debit_card'
            )
            current_payment_method_index = next(
                (i for i, (method, _) in enumerate(payment_method_options)
                 if method == current_payment_method), 1
            )
            selected_payment_method = st.selectbox(
                "💳 Método de Pagamento",
                options=payment_method_options,
                index=current_payment_method_index,
                format_func=lambda x: x[1],
                help="Método utilizado para pagamento"
            )
            new_payment_method = selected_payment_method[0]

            # Membro responsável
            try:
                members = api_client.get("members/")
                if members:
                    member_options = [(None, "Não informar")] + [
                        (
                            member['id'],  # type: ignore
                            member['name']  # type: ignore
                        )
                        for member in members if member.get(  # type: ignore
                            'active',
                            True
                        )
                    ]
                    current_member_index = (
                        next((i for i, (member_id, _) in enumerate(
                            member_options
                        ) if member_id == expense.get('member')), 0)
                    )
                    selected_member = st.selectbox(
                        "👤 Membro Responsável",
                        options=member_options,
                        index=current_member_index,
                        format_func=lambda x: x[1],
                        help="Membro responsável pela despesa"
                    )
                    new_member = selected_member[0]
                else:
                    new_member = expense.get('member')
            except Exception:
                new_member = expense.get('member')

            # Despesa recorrente
            new_recurring = st.checkbox(
                "🔄 Despesa Recorrente",
                value=expense.get('recurring', False),
                help="Marque se é uma despesa recorrente"
            )

            # Frequência (só aparece se for recorrente)
            frequency_options = [
                ('monthly', 'Mensal'),
                ('quarterly', 'Trimestral'),
                ('semiannually', 'Semestral'),
                ('annually', 'Anual')
            ]
            current_frequency = expense.get('frequency', 'monthly')
            current_frequency_index = next(
                (i for i, (freq, _) in enumerate(frequency_options)
                 if freq == current_frequency), 0
            )

            if new_recurring:
                selected_frequency = st.selectbox(
                    "📅 Frequência",
                    options=frequency_options,
                    index=current_frequency_index,
                    format_func=lambda x: x[1],
                    help="Frequência da despesa recorrente"
                )
                new_frequency = selected_frequency[0]
            else:
                new_frequency = None

            new_notes = st.text_area(
                "📝 Observações",
                value=expense.get('notes', ''),
                help="Observações sobre a despesa"
            )

            new_is_paid = st.checkbox(
                "✅ Despesa Paga",
                value=expense.get('payed', False),
                help="Marque se a despesa foi paga"
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
                        'horary': new_time.strftime('%H:%M:%S'),
                        'category': new_category,
                        'account': new_account,
                        'payed': new_is_paid,
                        'merchant': new_merchant,
                        'location': new_location,
                        'payment_method': new_payment_method,
                        'member': new_member,
                        'recurring': new_recurring,
                        'frequency': new_frequency if new_recurring else None,
                        'notes': new_notes
                    }
                    self._update_expense(
                        expense_id, updated_data  # type: ignore
                    )

            with col_cancel:
                if st.form_submit_button(
                    "❌ Cancelar",
                    width='stretch'
                ):
                    st.session_state.pop(f'edit_expense_{expense_id}', None)
                    st.rerun()

    def _render_expense_form(self) -> None:
        """Renderiza formulário para criação de nova despesa."""
        st.markdown("### ➕ Criar Nova Despesa")

        with st.form("create_expense_form", clear_on_submit=True):
            st.markdown("**Preencha os dados da nova despesa:**")

            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input(
                    "📝 Descrição",
                    placeholder="Ex: Supermercado, Conta de luz...",
                    help="Descrição da despesa"
                )

                value = st.number_input(
                    "💰 Valor",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Valor da despesa em reais"
                )

                category_display = st.selectbox(
                    "📂 Categoria",
                    options=list(
                        db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys()
                    ),
                    help="Categoria da despesa"
                )
                category = db_categories.TRANSLATED_EXPENSE_CATEGORIES[
                       category_display
                ]

            with col2:
                expense_date = st.date_input(
                    "📅 Data da Despesa",
                    value=datetime.now().date(),
                    help="Data em que a despesa foi feita",
                    format="DD/MM/YYYY"
                )

                expense_time = st.time_input(
                    "🕐 Horário",
                    value=datetime.now().time(),
                    help="Horário da despesa"
                )

                # Conta
                try:
                    accounts = accounts_service.get_all_accounts()
                    account_options = [
                        (
                            acc['id'],
                            db_categories.INSTITUTIONS.get(acc['name'], acc[
                                'name'
                                ]
                            )
                        ) for acc in accounts if acc.get('is_active', True)]

                    if account_options:
                        selected_account = st.selectbox(
                            "🏦 Conta",
                            options=account_options,
                            format_func=lambda x: x[1],
                            help="Conta de origem da despesa"
                        )
                        account_id = selected_account[0]
                    else:
                        show_missing_resource_dialog(
                            "Conta", "conta", "accounts"
                        )
                        account_id = None
                except ApiClientError:
                    st.error("Erro ao carregar contas")
                    account_id = None

            is_paid = st.checkbox(
                "✅ Despesa já foi paga",
                value=False,
                help="Marque se a despesa já foi paga"
            )

            # Campos adicionais
            col3, col4 = st.columns(2)

            with col3:
                merchant = st.text_input(
                    "🏦 Estabelecimento",
                    help="Nome do estabelecimento"
                )

                location = st.text_input(
                    "📍 Local",
                    help="Local da despesa"
                )

                payment_method_options = [
                    ('cash', 'Dinheiro'),
                    ('debit_card', 'Cartão de Débito'),
                    ('credit_card', 'Cartão de Crédito'),
                    ('bank_transfer', 'Transferência Bancária'),
                    ('pix', 'PIX'),
                    ('check', 'Cheque'),
                    ('voucher', 'Vale')
                ]
                selected_payment_method = st.selectbox(
                    "💳 Método de Pagamento",
                    options=payment_method_options,
                    index=1,  # debit_card como padrão
                    format_func=lambda x: x[1],
                    help="Método utilizado para pagamento"
                )
                payment_method = selected_payment_method[0]

            with col4:
                # Membro responsável
                try:
                    members = api_client.get("members/")
                    if members:
                        member_options = [(None, "Não informar")] + [
                            (
                                member['id'],  # type: ignore
                                member['name']  # type: ignore
                            )
                            for member in members if (
                                member.get(  # type: ignore
                                    'active',
                                    True
                                )
                            )
                        ]
                        selected_member = st.selectbox(
                            "👤 Membro Responsável",
                            options=member_options,
                            format_func=lambda x: x[1],
                            help="Membro responsável pela despesa"
                        )
                        member_id = selected_member[0]
                    else:
                        member_id = None
                except Exception:
                    member_id = None

                # Despesa recorrente
                recurring = st.checkbox(
                    "🔄 Despesa Recorrente",
                    help="Marque se é uma despesa recorrente"
                )

            # Frequência (só aparece se for recorrente)
            if recurring:
                frequency_options = [
                    ('monthly', 'Mensal'),
                    ('quarterly', 'Trimestral'),
                    ('semiannually', 'Semestral'),
                    ('annually', 'Anual')
                ]
                selected_frequency = st.selectbox(
                    "📅 Frequência",
                    options=frequency_options,
                    format_func=lambda x: x[1],
                    help="Frequência da despesa recorrente"
                )
                frequency = selected_frequency[0]
            else:
                frequency = None

            notes = st.text_area(
                "📝 Observações",
                help="Observações sobre a despesa"
            )

            # Preview da despesa
            if description and value and account_id:
                with st.expander("👁️ Preview da Despesa", expanded=True):
                    category_name = db_categories.EXPENSE_CATEGORIES.get(
                        category, category
                    )
                    account_name_code = next(
                        (opt[1] for opt in account_options if (
                            opt[0] == account_id
                        )), "Conta"
                    )
                    # Traduz o código da conta para nome completo
                    account_name = db_categories.INSTITUTIONS.get(
                        account_name_code,  # type: ignore
                        account_name_code
                    )  # type: ignore

                    st.info(f"""
                    **Descrição:** {description}
                    **Valor:** {format_currency_br(value)}
                    **Data:** {format_date_for_display(expense_date)} às {
                        expense_time.strftime('%H:%M')
                    }
                    **Categoria:** {category_name}
                    **Conta:** {account_name}
                    **Status:** {'Paga' if is_paid else 'Pendente'}
                    """)

            # Botão de envio
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button(
                    "💾 Criar Despesa",
                    type="primary",
                    width='stretch'
                ):
                    if not description:
                        st.error("❌ Descrição é obrigatória")
                    elif not value or value <= 0:
                        st.error("❌ Valor deve ser maior que zero")
                    elif not account_id:
                        st.error("❌ Selecione uma conta")
                    else:
                        expense_data = {
                            'description': description,
                            'value': value,
                            'date': format_date_for_api(expense_date),
                            'horary': expense_time.strftime('%H:%M:%S'),
                            'category': category,
                            'account': account_id,
                            'payed': is_paid,
                            'merchant': merchant,
                            'location': location,
                            'payment_method': payment_method,
                            'member': member_id,
                            'recurring': recurring,
                            'frequency': frequency if recurring else None,
                            'notes': notes
                        }
                        self._create_expense(expense_data)

    def _create_expense(
            self,
            expense_data: Dict[str, Any]
            ) -> None:
        """
        Cria uma nova despesa via API.

        Parameters
        ----------
        expense_data : Dict[str, Any]
            Dados da nova despesa
        """
        try:
            with st.spinner("💾 Criando despesa..."):
                time.sleep(1)
                new_expense = expenses_service.create_expense(expense_data)

            st.toast("✅ Despesa criada com sucesso!")
            time.sleep(1)
            st.info(f"🆔 ID da despesa: {new_expense.get('id')}")

            # Limpa filtros para mostrar a nova despesa
            st.session_state.pop('expense_filters', None)
            st.rerun()

        except ValidationError as e:
            st.error(f"❌ Dados inválidos: {e}")
            logger.error(f"Erro de validação ao criar despesa: {e}")
        except ApiClientError as e:
            st.error(f"🔧 Erro ao criar despesa: {e}")
            logger.error(f"Erro da API ao criar despesa: {e}")

    def _update_expense(
            self,
            expense_id: int,
            expense_data: Dict[str, Any]
            ) -> None:
        """
        Atualiza uma despesa existente via API.

        Parameters
        ----------
        expense_id : int
            ID da despesa a atualizar
        expense_data : Dict[str, Any]
            Novos dados da despesa
        """
        try:
            with st.spinner("💾 Salvando alterações..."):
                updated_expense = expenses_service.update_expense(
                    expense_id, expense_data
                )
                print(updated_expense)

            st.success("✅ Despesa atualizada com sucesso!")

            # Remove o estado de edição e recarrega
            st.session_state.pop(f'edit_expense_{expense_id}', None)
            st.rerun()

        except ValidationError as e:
            st.error(f"❌ Dados inválidos: {e}")
            logger.error(
                f"Erro de validação ao atualizar despesa {expense_id}: {e}"
            )
        except ApiClientError as e:
            st.error(f"🔧 Erro ao atualizar despesa: {e}")
            logger.error(f"Erro da API ao atualizar despesa {expense_id}: {e}")

    def _toggle_expense_payment(self, expense_id: int, is_paid: bool) -> None:
        """
        Alterna o status de pagamento de uma despesa.

        Parameters
        ----------
        expense_id : int
            ID da despesa
        is_paid : bool
            Novo status de pagamento
        """
        try:
            with st.spinner(
                f"""{
                    'Marcando como paga' if (
                        is_paid
                    ) else 'Marcando como pendente'
                }..."""
            ):
                # Primeiro obtém os dados completos da despesa
                expense_data = expenses_service.get_expense_by_id(expense_id)
                update_data = {
                    'description': expense_data.get('description'),
                    'value': expense_data.get('value'),
                    'date': expense_data.get('date'),
                    'horary': expense_data.get('horary'),
                    'category': expense_data.get('category'),
                    'account': expense_data.get('account'),
                    'payed': is_paid
                }

                expenses_service.update_expense(expense_id, update_data)

            status_text = "paga" if is_paid else "pendente"
            st.success(f"✅ Despesa marcada como {status_text}!")
            st.rerun()

        except ApiClientError as e:
            st.error(f"🔧 Erro ao alterar status da despesa: {e}")
            logger.error(
                f"Erro ao alterar status da despesa {expense_id}: {e}"
            )

    def _delete_expense(self, expense_id: int, description: str) -> None:
        """
        Exclui uma despesa após confirmação.

        Parameters
        ----------
        expense_id : int
            ID da despesa a excluir
        description : str
            Descrição da despesa para exibição
        """
        # Define estado da confirmação de exclusão
        confirm_key = f"confirm_delete_{expense_id}"

        # Se não está no modo de confirmação, marca para confirmar
        if not st.session_state.get(confirm_key, False):
            st.session_state[confirm_key] = True
            st.rerun()

        # Mostra modal de confirmação
        st.warning(
            f"""⚠️ **Tem certeza que deseja excluir a despesa '{
                description
            }'?**"""
        )
        st.error("🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🗑️ Sim, Excluir",
                key=f"final_confirm_delete_expense_{expense_id}",
                type="primary",
                width='stretch'
            ):
                try:
                    with st.spinner("🗑️ Excluindo despesa..."):
                        expenses_service.delete_expense(expense_id)

                    st.success(
                        f"✅ Despesa '{description}' excluída com sucesso!"
                    )

                    # Limpa o estado de confirmação
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

                except ApiClientError as e:
                    st.error(f"🔧 Erro ao excluir despesa: {e}")
                    logger.error(f"Erro ao excluir despesa {expense_id}: {e}")
                    # Limpa o estado de confirmação mesmo com erro
                    st.session_state.pop(confirm_key, None)

        with col2:
            if st.button(
                "❌ Cancelar",
                key=f"cancel_delete_expense_{expense_id}",
                width='stretch'
            ):
                # Limpa o estado de confirmação
                st.session_state.pop(confirm_key, None)
                st.rerun()

    def _render_checking_expenses_summary(self) -> None:
        """Renderiza resumo específico das despesas em conta corrente."""
        st.markdown("#### 📊 Resumo - Conta Corrente")

        try:
            with st.spinner("📊 Carregando estatísticas..."):
                # Carrega despesas dos últimos 30 dias
                date_30_days_ago = format_date_for_api(
                    datetime.now() - timedelta(days=30)
                )

                expenses = expenses_service.get_all_expenses(
                    date_from=date_30_days_ago
                )

            if not expenses:
                st.info(
                    """
                    📝 Nenhuma despesa de conta corrente encontrada
                    nos últimos 30 dias.
                    """
                )
                return

            # Estatísticas específicas para despesas de conta corrente
            total_value = sum(float(exp.get('value', 0)) for exp in expenses)
            paid_value = sum(
                   float(
                          exp.get(
                              'value',
                              0
                            )) for exp in expenses if exp.get('payed', False)
                        )
            pending_value = total_value - paid_value

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total de Despesas", len(expenses))
            with col2:
                st.metric("💰 Valor Total", format_currency_br(total_value))
            with col3:
                st.metric("✅ Valor Pago", format_currency_br(paid_value))
            with col4:
                st.metric("⏳ Valor Pendente", format_currency_br(
                    pending_value)
                )

            # Gráfico por categoria específico para conta corrente
            st.markdown("#### 📂 Despesas por Categoria (Conta Corrente)")
            category_data = {}
            for expense in expenses:
                category = expense.get('category', 'others')
                category_name = db_categories.EXPENSE_CATEGORIES.get(
                    category, category
                )
                value = float(expense.get('value', 0))
                category_data[category_name] = category_data.get(
                    category_name, 0
                ) + value

            if category_data:
                df_categories = pd.DataFrame(
                    list(category_data.items()),
                    columns=['Categoria', 'Valor']
                ).sort_values('Valor', ascending=True)

                st.bar_chart(df_categories.set_index('Categoria'))

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar estatísticas: {e}")
            logger.error(
                f"""
                Erro ao carregar resumo de despesas de conta corrente: {e}
                """
            )

    def _render_cc_expenses_summary(self) -> None:
        """Renderiza resumo específico das despesas de cartão de crédito."""
        st.markdown("#### 📊 Resumo - Cartão de Crédito")

        try:
            with st.spinner("📊 Carregando estatísticas..."):
                cc_expenses = api_client.get("credit-cards-expenses/")

            if not cc_expenses:
                st.info("📝 Nenhuma despesa de cartão de crédito encontrada.")
                return

            # Estatísticas específicas para cartão de crédito
            total_cc_expenses = sum(
                   float(
                        exp.get(  # type: ignore
                            'value', 0
                        )
                    ) for exp in cc_expenses
                    )
            paid_cc_expenses = sum(
                   float(
                        exp.get('value', 0)  # type: ignore
                    ) for exp in cc_expenses if exp.get(  # type: ignore
                        'payed', False
                    )
            )
            pending_cc_expenses = total_cc_expenses - paid_cc_expenses

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total de Despesas", len(cc_expenses))
            with col2:
                st.metric(
                    "💰 Valor Total",
                    format_currency_br(total_cc_expenses)
                )
            with col3:
                st.metric("✅ Valor Pago", format_currency_br(paid_cc_expenses))
            with col4:
                st.metric(
                    "⏳ Valor Pendente",
                    format_currency_br(pending_cc_expenses)
                )

            # Análise por cartão
            st.markdown("#### 💳 Despesas por Cartão")
            card_data = {}
            for expense in cc_expenses:
                card_name = expense.get(  # type: ignore
                    'card_name',
                    'Cartão Desconhecido'
                )
                value = float(expense.get('value', 0))  # type: ignore
                card_data[card_name] = card_data.get(card_name, 0) + value

            if card_data:
                df_cards = pd.DataFrame(
                    list(card_data.items()),
                    columns=['Cartão', 'Valor']
                ).sort_values('Valor', ascending=True)

                st.bar_chart(df_cards.set_index('Cartão'))

            # Análise por parcelamento
            st.markdown("#### 🔢 Análise de Parcelamento")
            installment_data = {}
            for expense in cc_expenses:
                installment = expense.get('installment', 1)  # type: ignore
                installment_key = f"{installment}x" if installment > 1 else (
                    "À vista"
                )
                value = float(expense.get('value', 0))  # type: ignore
                installment_data[installment_key] = installment_data.get(
                    installment_key,
                    0
                ) + value

            if installment_data:
                col1, col2 = st.columns(2)

                with col1:
                    for key, value in installment_data.items():
                        st.metric(key, format_currency_br(value))

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar estatísticas de cartão: {e}")
            logger.error(f"Erro ao carregar resumo de despesas de cartão: {e}")

    def _render_cc_expenses_list(self) -> None:
        """Renderiza a lista de despesas de cartão de crédito
        com mensagens melhoradas."""
        st.markdown("#### 💳 Despesas de Cartão de Crédito")

        try:
            with st.spinner("🔄 Carregando despesas de cartão..."):
                time.sleep(1)
                cc_expenses = api_client.get("credit-cards-expenses/")
                # Também carregamos faturas para verificar se existem
                bills = api_client.get("credit-cards-bills/")
                cards = api_client.get("credit-cards/")

            # Mensagens mais informativas quando não há despesas
            if not cc_expenses:
                if not cards:
                    st.warning("⚠️ **Nenhum cartão de crédito cadastrado**")
                    st.info("""
                    💡 **Para começar:**
                    1. Cadastre um cartão de crédito na aba 'Novo Cartão'
                    2. Crie uma fatura para o cartão
                    3. Registre suas despesas de cartão aqui
                    """)
                elif not bills:
                    st.warning("⚠️ **Nenhuma fatura cadastrada**")
                    st.info("""
                    💡 **Próximos passos:**
                    1. Vá para a página de Cartões de Crédito
                    2. Crie uma fatura na aba 'Faturas'
                    3. Volte aqui para registrar despesas na fatura
                    """)
                else:
                    st.info("📝 **Nenhuma despesa de cartão registrada ainda**")
                    st.success("""
                    ✅ **Tudo pronto!** Você já tem \
                    cartões e faturas cadastrados.

                    🛍️ **Registre sua primeira despesa:**
                    - Use a aba 'Nova Despesa' ao lado
                    - Suas compras aparecerão aqui automaticamente
                    """)
                return

            # Estatísticas rápidas
            total_cc_expenses = sum(
                   float(
                       exp.get(  # type: ignore
                           'value', 0
                        )) for exp in cc_expenses)
            paid_cc_expenses = sum(
                   float(
                          exp.get(  # type: ignore
                              'value', 0
                            )
                    ) for exp in cc_expenses if exp.get(  # type: ignore
                        'payed', False
                    )
            )
            pending_cc_expenses = total_cc_expenses - paid_cc_expenses

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total", format_currency_br(total_cc_expenses))
            with col2:
                st.metric("✅ Pagas", format_currency_br(paid_cc_expenses))
            with col3:
                st.metric(
                    "⏳ Pendentes",
                    format_currency_br(pending_cc_expenses)
                )

            st.markdown("---")

            for cc_expense in cc_expenses:
                self._render_cc_expense_card(cc_expense)  # type: ignore

        except ApiClientError as e:
            st.error(f"❌ **Erro ao carregar despesas de cartão:** {str(e)}")
            st.info(
                "💡 **Solução:** Verifique sua conexão e recarregue a página."
            )
            logger.error(f"Erro ao listar despesas de cartão: {e}")

    def _render_cc_expense_card(self, cc_expense: Dict[str, Any]) -> None:
        """Renderiza um card de despesa de cartão de crédito."""
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                description = cc_expense.get('description', 'Despesa')
                category = cc_expense.get('category', 'others')
                category_emoji = db_categories.EXPENSE_CATEGORY_EMOJIS.get(
                    category, "💳")
                category_name = db_categories.EXPENSE_CATEGORIES.get(
                    category,
                    category
                )
                card_name = cc_expense.get('card_name', 'Cartão')

                st.markdown(f"### {category_emoji} {description}")
                st.caption(f"📂 {category_name} | 💳 {card_name}")

            with col2:
                value = float(cc_expense.get('value', 0))
                date_str = format_date_for_display(cc_expense.get('date', ''))
                time_str = cc_expense.get('horary', '00:00:00')
                installment = cc_expense.get('installment', 1)

                st.markdown(f"**{format_currency_br(value)}**")
                st.caption(f"📅 {date_str} às {time_str}")
                if installment > 1:
                    st.caption(f"🔢 {installment}x")

            with col3:
                if cc_expense.get('payed', False):
                    st.success("✅ Paga")
                else:
                    st.warning("⏳ Pendente")

            with col4:
                expense_id = cc_expense.get('id')
                with st.popover("⚙️ Ações"):
                    if st.button(
                        "✏️ Editar",
                        key=f"edit_btn_cc_expense_{expense_id}",
                        width='stretch'
                    ):
                        st.session_state[
                            f'edit_cc_expense_{expense_id}'] = cc_expense
                        st.rerun()

                toggle_text = (
                    "⏳ Marcar Pendente" if cc_expense.get('payed', False)
                    else "✅ Marcar Paga")
                if st.button(
                        toggle_text,
                        key=f"toggle_btn_cc_expense_{expense_id}",
                        width='stretch'
                ):
                    self._toggle_cc_expense_payment(
                        expense_id,  # type: ignore
                        not cc_expense.get('payed', False)
                    )

                    if st.button(
                        "📄 Gerar PDF",
                        key=f"pdf_btn_cc_expense_{expense_id}",
                        width='stretch'
                    ):
                        self._generate_cc_expense_pdf(cc_expense)

                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_btn_cc_expense_{expense_id}",
                        width='stretch'
                    ):
                        self._delete_cc_expense(
                            expense_id, description  # type: ignore
                        )

            st.markdown("---")

    def _render_cc_expense_form(self) -> None:
        """Renderiza formulário para criar despesa de cartão com validações."""
        st.markdown("#### ➕ Nova Despesa de Cartão")

        with st.form("create_cc_expense_form"):
            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input(
                    "📝 Descrição",
                    placeholder="Ex: Compra no supermercado..."
                )

                value = st.number_input(
                    "💰 Valor",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f"
                )

                category_display = st.selectbox(
                    "📂 Categoria",
                    options=list(
                        db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys()
                    )
                )
                category = db_categories.TRANSLATED_EXPENSE_CATEGORIES[
                    category_display
                ]

                # Seleção de cartão com validações
                try:
                    cards = api_client.get("credit-cards/")
                    if not cards:
                        st.error("❌ **Nenhum cartão disponível**")
                        st.info(
                            """
                            💡 **Solução:**
                            Cadastre um cartão primeiro na página
                            de Cartões de Crédito.
                            """
                        )
                        return
                    card_options = [
                        (
                            card['id'],  # type: ignore
                            card['name'],  # type: ignore
                            card
                        ) for card in cards
                    ]
                    selected_card = st.selectbox(
                        "💳 Cartão",
                        options=card_options,
                        format_func=lambda x: x[1],
                        help="Selecione o cartão para a despesa"
                    )
                    card_id = selected_card[0]
                    selected_card_data = selected_card[2]
                    credit_limit = float(
                        selected_card_data.get(  # type: ignore
                            'credit_limit', 0
                        )
                    )
                    st.caption(
                        f"💳 **Limite:** {format_currency_br(credit_limit)}")

                except ApiClientError:
                    st.error("❌ Erro ao carregar cartões")
                    return

            with col2:
                expense_date = st.date_input(
                    "📅 Data da Compra",
                    value=datetime.now().date(),
                    format="DD/MM/YYYY"
                )

                expense_time = st.time_input(
                    "🕐 Horário",
                    value=datetime.now().time()
                )

                installment = st.number_input(
                    "🔢 Parcela Atual",
                    min_value=1,
                    max_value=48,
                    value=1,
                    help="Número da parcela atual"
                )

                total_installments = st.number_input(
                    "📊 Total de Parcelas",
                    min_value=installment,
                    max_value=48,
                    value=max(installment, 1),
                    help="Total de parcelas"
                )

                payed = st.checkbox("✅ Despesa já foi paga")

            # Campos opcionais adicionais
            st.markdown("---")
            st.markdown("**Informações Adicionais (Opcional)**")

            col3, col4 = st.columns(2)

            with col3:
                merchant = st.text_input(
                    "🏪 Estabelecimento",
                    help="Nome do estabelecimento"
                )

                transaction_id = st.text_input(
                    "🔢 ID da Transação",
                    help="Identificador da transação"
                )

                location = st.text_input(
                    "📍 Local",
                    help="Local da compra"
                )

            with col4:
                # Seleção de membro responsável (opcional)
                try:
                    members = api_client.get("members/")
                    if members:
                        member_options = [
                            (
                                None, "Não informar"
                            )] + [
                                (
                                    member['id'],  # type: ignore
                                    member['name']  # type: ignore
                                ) for member in members if (
                                    member.get('active', True)  # type: ignore
                                )
                            ]
                        selected_member = st.selectbox(
                            "👤 Membro Responsável",
                            options=member_options,
                            format_func=lambda x: x[1],
                            help="Membro responsável pela despesa"
                        )
                        member_id = selected_member[0] if (
                            selected_member[0]
                        ) else None
                    else:
                        member_id = None
                except ApiClientError:
                    member_id = None

            notes = st.text_area(
                "📝 Observações",
                help="Observações sobre a despesa"
            )

            # Validações em tempo real
            if value and card_id:
                try:
                    # Verificar limite disponível
                    existing_expenses = api_client.get(
                        "credit-cards-expenses/"
                    )
                    card_expenses = [
                        exp for exp in existing_expenses if (
                            exp.get(  # type: ignore
                                'card'
                            ) == card_id
                        ) and not exp.get('payed', False)  # type: ignore
                    ]
                    used_limit = sum(
                        float(
                            exp.get('value', 0)  # type: ignore
                        ) for exp in card_expenses)
                    available_limit = credit_limit - used_limit
                    remaining_after = available_limit - value

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "💰 Limite Usado",
                            format_currency_br(used_limit)
                        )
                    with col2:
                        st.metric(
                            "🔓 Disponível",
                            format_currency_br(available_limit)
                        )
                    with col3:
                        if remaining_after >= 0:
                            st.metric(
                                "✅ Após Compra",
                                format_currency_br(remaining_after),
                                delta=f"-{format_currency_br(value)}"
                            )
                        else:
                            st.metric(
                                "⚠️ Após Compra",
                                format_currency_br(remaining_after),
                                delta=f"-{format_currency_br(value)}"
                            )
                            st.warning(
                                """
                                ⚠️ **Atenção:**
                                Esta despesa excederá o limite do cartão!
                                """
                            )

                except Exception:
                    st.info("ℹ️ Não foi possível calcular o limite disponível")

            if st.form_submit_button("💾 Criar Despesa", type="primary"):
                # Validações mais robustas
                validation_errors = []

                if not description:
                    validation_errors.append("Descrição é obrigatória")

                if not value or value <= 0:
                    validation_errors.append("Valor deve ser maior que zero")

                if not card_id:
                    validation_errors.append("Selecione um cartão")

                # Verificar se existe fatura para o período da despesa
                matching_bill = None
                try:
                    bills = api_client.get("credit-cards-bills/")
                    expense_month = expense_date.strftime('%b')
                    expense_year = str(expense_date.year)

                    matching_bill = next((
                        bill for bill in bills
                        if (
                            bill.get(  # type: ignore
                                'credit_card'
                            ) == card_id and
                            bill.get(  # type: ignore
                                'month'
                            ) == expense_month and  # type: ignore
                            bill.get('year') == expense_year)  # type: ignore
                    ), None)

                    if not matching_bill:
                        validation_errors.append(
                            f"""
                            Não há fatura cadastrada para {
                                expense_date.strftime('%B/%Y')
                            } neste cartão"""
                            )
                    elif matching_bill.get('closed', False):  # type: ignore
                        validation_errors.append(
                            f"""
                            A fatura de {
                                expense_date.strftime('%B/%Y')
                            } já está fechada
                            """
                        )

                except ApiClientError:
                    validation_errors.append(
                        "Não foi possível verificar as faturas")

                # Verificar limite se houver valor
                if value and card_id:
                    try:
                        existing_expenses = api_client.get(
                            "credit-cards-expenses/"
                        )
                        card_expenses = [
                            exp for exp in existing_expenses if (
                                exp.get('card')  # type: ignore
                            ) == card_id and not (
                                exp.get('payed', False)  # type: ignore
                            )
                        ]
                        used_limit = sum(
                            float(
                                exp.get('value', 0)  # type: ignore
                            ) for exp in card_expenses
                        )

                        if (used_limit + value) > credit_limit:
                            validation_errors.append(
                                f"""
                                Despesa excede o limite do cartão em {
                                    format_currency_br(
                                        (used_limit + value) - credit_limit
                                        )
                                    }
                                    """
                                )
                    except ApiClientError:
                        pass  # Não bloqueia se não conseguir verificar

                if validation_errors:
                    st.error("❌ **Erros encontrados:**")
                    for error in validation_errors:
                        st.error(f"• {error}")
                else:
                    cc_expense_data = {
                        'description': description,
                        'value': value,
                        'date': format_date_for_api(expense_date),
                        'horary': expense_time.strftime('%H:%M:%S'),
                        'category': category,
                        'card': card_id,
                        'installment': installment,
                        'total_installments': total_installments,
                        'payed': payed
                    }

                    # Adicionar campos opcionais se preenchidos
                    if merchant:
                        cc_expense_data['merchant'] = merchant
                    if transaction_id:
                        cc_expense_data['transaction_id'] = transaction_id
                    if location:
                        cc_expense_data['location'] = location
                    if member_id:
                        cc_expense_data['member'] = member_id
                    if notes:
                        cc_expense_data['notes'] = notes

                    # Relacionar com a fatura correspondente
                    if matching_bill:
                        cc_expense_data['bill'] = (
                            matching_bill['id']
                        )  # type: ignore

                    # Comprovante será gerado automaticamente

                    self._create_cc_expense(cc_expense_data)

    def _create_cc_expense(self, expense_data: Dict[str, Any]) -> None:
        """Cria uma nova despesa de cartão."""
        try:
            with st.spinner("💾 Criando despesa de cartão..."):
                time.sleep(1)
                new_expense = api_client.post(
                    "credit-cards-expenses/",
                    expense_data
                )
                print(new_expense)

            st.toast("✅ Despesa de cartão criada com sucesso!")
            time.sleep(1)
            st.rerun()

        except ApiClientError as e:
            st.error(f"❌ Erro ao criar despesa de cartão: {e}")
            logger.error(f"Erro ao criar despesa de cartão: {e}")

    def _toggle_cc_expense_payment(
        self,
        expense_id: int,
        is_paid: bool
    ) -> None:
        """Alterna o status de pagamento de uma despesa de cartão."""
        try:
            with st.spinner(
                f"""{'Marcando como paga' if is_paid else (
                    'Marcando como pendente'
                    )}..."""):
                expense_data = api_client.get(
                    f"credit-cards-expenses/{expense_id}/"
                )
                update_data = {
                    'description': expense_data.get('description'),
                    'value': expense_data.get('value'),
                    'date': expense_data.get('date'),
                    'horary': expense_data.get('horary'),
                    'category': expense_data.get('category'),
                    'card': expense_data.get('card'),
                    'installment': expense_data.get('installment'),
                    'payed': is_paid
                }
                api_client.put(
                    f"credit-cards-expenses/{expense_id}/", update_data
                )
                status_text = "paga" if is_paid else "pendente"
                st.success(f"✅ Despesa marcada como {status_text}!")
                st.rerun()

        except ApiClientError as e:
            st.error(f"❌ Erro ao alterar status: {e}")
            logger.error(
                f"""
                Erro ao alterar status da despesa de cartão {expense_id}: {e}
                """
            )

    def _delete_cc_expense(self, expense_id: int, description: str) -> None:
        """Exclui uma despesa de cartão após confirmação."""
        confirm_key = f"confirm_delete_cc_{expense_id}"

        if not st.session_state.get(confirm_key, False):
            st.session_state[confirm_key] = True
            st.rerun()

        st.warning(
            f"⚠️ **Tem certeza que deseja excluir a despesa '{description}'?**"
        )
        st.error("🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🗑️ Sim, Excluir",
                key=f"final_confirm_delete_cc_expense_{expense_id}",
                type="primary",
                width='stretch'
            ):
                try:
                    with st.spinner("🗑️ Excluindo despesa..."):
                        api_client.delete(
                            f"credit-cards-expenses/{expense_id}/"
                        )
                        st.success(
                            f"✅ Despesa '{description}' excluída com sucesso!"
                        )
                        st.session_state.pop(confirm_key, None)
                        st.rerun()

                except ApiClientError as e:
                    st.error(f"❌ Erro ao excluir despesa: {e}")
                    logger.error(
                        f"Erro ao excluir despesa de cartão {expense_id}: {e}"
                    )
                    st.session_state.pop(confirm_key, None)

            with col2:
                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_delete_cc_expense_{expense_id}",
                    width='stretch'
                ):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

    def _generate_expense_pdf(self, expense: Dict[str, Any]) -> None:
        """Gera e oferece download do PDF da despesa."""
        if pdf_generator is None:
            st.error(
                """
                Gerador de PDF não disponível.
                Instale o ReportLab: pip install reportlab
                """
            )
            return
        try:
            with st.spinner("📄 Gerando comprovante..."):
                # Buscar dados da conta
                account_data = None
                account_id = expense.get('account')
                if account_id:
                    try:
                        accounts = accounts_service.get_all_accounts()
                        account_data = next(
                            (
                                acc for acc in accounts if acc[
                                    'id'
                                ] == account_id
                            ),
                            None
                        )
                    except ApiClientError:
                        pass

                # Gerar PDF
                pdf_buffer = pdf_generator.generate_expense_receipt(
                    expense,
                    account_data
                )
                # Nome do arquivo
                description = expense.get('description', 'despesa')
                date_str = expense.get('date', '').replace('-', '_')
                filename = (
                    f"comprovante_despesa_{description}_{date_str}.pdf"
                )

                # Oferecer download
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_expense_{expense.get('id')}"
                )

                # Preview do PDF
                st.success("✅ Comprovante gerado com sucesso!")
                try:
                    pdf_buffer.seek(0)
                    if hasattr(st, 'pdf'):
                        st.pdf(pdf_buffer.getvalue())
                    else:
                        st.info(
                            """
                            📄 PDF gerado.
                            Use o botão de download para visualizar.
                            """
                        )
                except Exception as e:
                    logger.warning(f"Erro ao exibir preview do PDF: {e}")
                    st.info(
                        """
                        📄 PDF gerado.
                        Use o botão de download para visualizar.
                        """
                    )

        except Exception as e:
            st.error(f"❌ Erro ao gerar comprovante: {e}")
            logger.error(
                f"Erro ao gerar PDF da despesa {expense.get('id')}: {e}"
            )

    def _generate_cc_expense_pdf(self, expense: Dict[str, Any]) -> None:
        """Gera e oferece download do PDF da despesa de cartão."""
        if pdf_generator is None:
            st.error(
                """
                Gerador de PDF não disponível.
                Instale o ReportLab: pip install reportlab
                """
            )
            return

        try:
            with st.spinner("📄 Gerando comprovante..."):
                # Buscar dados do cartão e fatura
                card_data = None
                bill_data = None

                try:
                    cards = api_client.get("credit-cards/")
                    card_data = next(
                        (
                            card for card in cards if card[
                                'id'  # type: ignore
                            ] == expense.get('card')), None)

                    bills = api_client.get("credit-cards-bills/")
                    bill_data = next(
                        (
                            bill for bill in bills if (
                                bill[
                                    'id'
                                ] == expense.get('bill'))  # type: ignore
                            ), None
                    )
                except ApiClientError:
                    pass

                # Gerar PDF
                pdf_buffer = pdf_generator.generate_credit_card_receipt(
                    expense,
                    card_data,  # type: ignore
                    bill_data  # type: ignore
                )

                # Nome do arquivo
                description = expense.get('description', 'despesa_cartao')
                date_str = expense.get('date', '').replace('-', '_')
                filename = f"""
                comprovante_cartao_{description}_{date_str}.pdf
                """

                # Oferecer download
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_cc_expense_{expense.get('id')}"
                )

                # Preview do PDF
                st.success("✅ Comprovante gerado com sucesso!")
                try:
                    pdf_buffer.seek(0)
                    if hasattr(st, 'pdf'):
                        st.pdf(pdf_buffer.getvalue())
                    else:
                        st.info(
                            """
                            📄 PDF gerado.
                            Use o botão de download para visualizar.
                            """
                        )
                except Exception as e:
                    logger.warning(f"Erro ao exibir preview do PDF: {e}")
                    st.info(
                        """
                        📄 PDF gerado.
                        Use o botão de download para visualizar.
                        """
                    )

        except Exception as e:
            st.error(f"❌ Erro ao gerar comprovante: {e}")
            logger.error(
                f"""
                Erro ao gerar PDF da despesa de cartão {
                    expense.get('id')
                }: {e}
                """
            )
