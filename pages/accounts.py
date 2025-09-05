"""
Módulo de gerenciamento de contas bancárias.

Este módulo implementa o CRUD completo para contas bancárias,
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


class AccountsPage:
    """Página de gerenciamento de contas bancárias,
    com padrão visual padronizado."""

    def __init__(self):
        """Inicializa a página de contas."""
        self.auth = require_auth()

    def render(self):
        """
        Renderiza a página principal de contas com padrão padronizado.

        Segue o padrão visual estabelecido:
        - Duas tabs centralizadas (listagem + novo registro)
        - Layout de 3 colunas para listagem
        - Popup de ações com CRUD
        """
        ui_components.render_page_header(
            "🏦 Contas Bancárias",
            subtitle="Gerenciamento de contas e saldos"
        )

        # Tabs principais - padrão estabelecido: 2 tabs centralizadas
        tab_list, tab_add = centered_tabs([
            "📋 Listagem de Contas",
            "➕ Nova Conta"
        ])

        with tab_list:
            self._render_accounts_list_standardized()

        with tab_add:
            self._render_add_account_form_standardized()

    def _render_accounts_list_standardized(self):
        """
        Renderiza a lista de contas seguindo padrão padronizado.

        Padrão estabelecido:
        - Layout de 3 colunas por registro
        - Primeira coluna: nome da conta + emoji do tipo
        - Segunda coluna (central): dados como saldo, tipo, banco
        - Terceira coluna (direita): botão de engrenagem com popup de ações
        """
        st.markdown("### 📋 Listagem de Contas")

        # Filtros simplificados em uma linha
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            status_filter = st.selectbox(
                "🔍 Status",
                options=['Todas', 'Ativas', 'Inativas'],
                index=0
            )

        with col_filter2:
            account_types = list(db_categories.ACCOUNT_TYPES.values())
            tipo_filter = st.selectbox(
                "🏦 Tipo",
                options=['Todos'] + account_types,
                index=0,
                format_func=lambda x: f"🗂️ {x}" if x == 'Todos' else f"🏦 {x}"
            )

        # Busca contas do usuário logado
        try:
            with st.spinner("🔄 Carregando suas contas..."):
                accounts = self._fetch_user_accounts(
                    status_filter, tipo_filter)

            if not accounts:
                st.info("📋 Você ainda não possui contas cadastradas.")
                return

            st.markdown("---")

            # Renderiza contas no padrão de 3 colunas
            self._render_accounts_three_column_layout(accounts)

        except Exception as e:
            ui_components.show_persistent_error(
                error_message=f"Erro ao carregar contas: {str(e)}",
                error_type="carregar_contas",
                details=f"Detalhes técnicos: {type(e).__name__}: {str(e)}",
                suggestions=[
                    "Verifique se a API está funcionando",
                    "Confirme sua conexão com a internet",
                    "Tente recarregar a página (F5)"
                ])
            logger.error(f"Erro ao carregar contas: {e}")

    def _render_accounts_three_column_layout(self, accounts: List[Dict]):
        """
        Renderiza contas no layout padronizado de 3 colunas.

        Parameters
        ----------
        accounts : List[Dict]
            Lista de contas para exibir
        """
        for account in accounts:
            # Container para cada conta
            with st.container():
                col1, col2, col3 = st.columns([3, 3, 1])

                with col1:
                    # Primeira coluna: nome + emoji do tipo
                    account_type = account.get('account_type', '')
                    account_type_display = db_categories.ACCOUNT_TYPES.get(
                        account_type, account_type or 'N/A'
                    )
                    emoji = self._get_account_type_emoji(account_type_display)

                    # Banco/Instituição
                    bank_code = account.get('bank_code', '')
                    institution_display = db_categories.INSTITUTIONS.get(
                        bank_code, bank_code or 'N/A'
                    )

                    st.markdown(f"""
                    **{emoji} Nome: {account.get('account_name', 'N/A')}**

                    🏛️ Instituição: {institution_display}

                    📂 Tipo: {account_type_display}
                    """)

                with col2:
                    # Segunda coluna (central): dados principais
                    balance = str(
                        round(
                            (
                                float(
                                    account.get(
                                        'current_balance',
                                        0
                                    )
                                )
                            ),
                            2
                        )
                    )
                    opening_date = account.get('opening_date', 'N/A')
                    opening_date_iso = datetime.strptime(
                        opening_date, '%Y-%m-%d'
                    )
                    br_date = opening_date_iso.strftime('%d/%m/%Y')
                    status = "✅ Ativa" if account.get(
                        'is_active', True
                    ) else "⏸️ Inativa"

                    st.markdown(f"""
                    **💰 Saldo: R$ {balance}**

                    📅 Abertura: {br_date}

                    {status}
                    """)

                with col3:
                    # Terceira coluna (direita): botão de ações
                    if st.button(
                        "⚙️",
                        key=f"actions_{account['id']}",
                        help="Opções de ações",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'show_actions_{account["id"]}'
                        ] = True
                        st.rerun()

                # Popup de ações para esta conta
                self._render_account_action_popup(account)

                st.markdown("---")

    def _render_account_action_popup(self, account: Dict):
        """
        Renderiza popup de ações para uma conta específica.

        Parameters
        ----------
        account : Dict
            Dados da conta
        """
        popup_key = f'show_actions_{account["id"]}'

        if st.session_state.get(popup_key, False):
            with st.expander(
                f"⚙️ Ações para: {account.get('account_name', 'N/A')}",
                expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📝 Editar",
                        key=f"edit_{account['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'edit_account_{account["id"]}'
                        ] = account
                        st.session_state[popup_key] = False
                        st.rerun()

                with col2:
                    action_text = "⏸️ Desativar" if account.get(
                        'is_active', True
                    ) else "✅ Ativar"
                    if st.button(
                        action_text,
                        key=f"toggle_{account['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        self._handle_toggle_account_status(account)
                        st.session_state[popup_key] = False
                        st.rerun()

                with col3:
                    if st.button(
                        "❌ Fechar",
                        key=f"close_{account['id']}",
                        use_container_width=True
                    ):
                        st.session_state[popup_key] = False
                        st.rerun()

        # Renderiza modal de edição
        self._render_edit_account_modal(account)

    def _render_edit_account_modal(self, account: Dict):
        """
        Renderiza modal de edição para uma conta.

        Parameters
        ----------
        account : Dict
            Dados da conta para editar
        """
        edit_key = f'edit_account_{account["id"]}'

        if st.session_state.get(edit_key):
            st.markdown("### ✏️ Editar Conta")

            with st.form(f"edit_form_{account['id']}", clear_on_submit=False):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input(
                        "📝 Nome da Conta *",
                        value=account.get('name', ''),
                        help="Nome identificador da conta"
                    )

                    # Tipo de conta com emoji
                    current_type = account.get('account_type', 'CC')
                    account_types_list = list(
                        db_categories.ACCOUNT_TYPES.values())
                    type_index = 0

                    for idx, (key, value) in enumerate(
                            db_categories.ACCOUNT_TYPES.items()):
                        if key == current_type:
                            type_index = idx
                            break

                    account_type = st.selectbox(
                        "🏦 Tipo de Conta *",
                        options=account_types_list,
                        index=type_index,
                        format_func=(
                            lambda x: f"{self._get_account_type_emoji(x)} {x}"
                        )
                    )

                with col2:
                    # Instituição/Banco
                    current_bank = account.get('bank_code', 'NUB')
                    institutions_list = list(
                        db_categories.INSTITUTIONS.values())
                    bank_index = 0

                    for idx, (key, value) in enumerate(
                            db_categories.INSTITUTIONS.items()):
                        if key == current_bank:
                            bank_index = idx
                            break

                    institution = st.selectbox(
                        "🏛️ Instituição *",
                        options=institutions_list,
                        index=bank_index,
                        format_func=lambda x: f"🏛️ {x}"
                    )

                    current_balance = st.number_input(
                        "💰 Saldo Atual (R$)",
                        value=float(account.get('current_balance', 0)),
                        step=0.01,
                        format="%.2f"
                    )

                # Campos opcionais
                with st.expander("📋 Informações Adicionais"):
                    col_opt1, col_opt2 = st.columns(2)

                    with col_opt1:
                        agency = st.text_input(
                            "🏢 Agência",
                            value=account.get('agency', '')
                        )

                        opening_date = st.date_input(
                            "📅 Data de Abertura",
                            value=datetime.fromisoformat(
                                account.get('opening_date', str(date.today()))
                            ).date() if account.get(
                                'opening_date'
                            ) else date.today()
                        )

                    with col_opt2:
                        minimum_balance = st.number_input(
                            "💳 Saldo Mínimo (R$)",
                            value=float(account.get('minimum_balance', 0)),
                            step=0.01,
                            format="%.2f"
                        )

                    description = st.text_area(
                        "📝 Descrição",
                        value=account.get('description', ''),
                        help="Informações adicionais sobre a conta"
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
                    self._handle_edit_account_submission(
                        account['id'],
                        name,  # type: ignore
                        account_type,
                        institution,
                        current_balance,
                        agency,  # type: ignore
                        opening_date,
                        minimum_balance,
                        description,  # type: ignore
                        edit_key
                    )

                if cancelled:
                    st.session_state.pop(edit_key, None)
                    st.rerun()

    def _render_add_account_form_standardized(self):
        """Renderiza formulário padronizado de adição de conta."""
        ui_components.render_enhanced_form_container(
            "Cadastro de nova conta", "➕"
        )

        with st.form("add_account_form_standardized", clear_on_submit=True):
            # Seção de dados principais
            st.markdown("#### 🏦 Dados da Conta")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "📝 Nome da Conta *",
                    help="Nome identificador para sua conta"
                )

                # Tipo de conta com emoji
                account_types_list = list(db_categories.ACCOUNT_TYPES.values())
                account_type = st.selectbox(
                    "🏦 Tipo de Conta *",
                    options=account_types_list,
                    format_func=(
                        lambda x: f"{self._get_account_type_emoji(x)} {x}"
                    )
                )

            with col2:
                # Instituição/Banco
                institutions_list = list(db_categories.INSTITUTIONS.values())
                institution = st.selectbox(
                    "🏛️ Instituição *",
                    options=institutions_list,
                    format_func=lambda x: f"🏛️ {x}"
                )

                current_balance = st.number_input(
                    "💰 Saldo Atual (R$) *",
                    min_value=0.00,
                    step=0.01,
                    format="%.2f",
                    help="Saldo atual da conta"
                )

            # Campos opcionais
            with st.expander("📋 Informações Adicionais (Opcional)"):
                col_opt1, col_opt2 = st.columns(2)

                with col_opt1:
                    agency = st.text_input(
                        "🏢 Agência",
                        help="Número da agência bancária"
                    )

                    account_number = st.text_input(
                        "🔢 Número da Conta",
                        help="Número da conta bancária"
                    )

                with col_opt2:
                    opening_date = st.date_input(
                        "📅 Data de Abertura",
                        value=date.today(),
                        format="DD/MM/YYYY"
                    )

                    minimum_balance = st.number_input(
                        "💳 Saldo Mínimo (R$)",
                        value=0.00,
                        step=0.01,
                        format="%.2f",
                        help="Saldo mínimo permitido na conta"
                    )

                description = st.text_area(
                    "📝 Descrição",
                    help="Informações adicionais sobre a conta"
                )

            # Botão de submissão
            submitted = st.form_submit_button(
                "💾 Salvar Conta",
                type="primary",
                use_container_width=True
            )

            if submitted:
                self._handle_add_account_submission(
                    name,
                    account_type,
                    institution,
                    current_balance,
                    agency,
                    account_number,
                    opening_date,
                    minimum_balance,
                    description
                )

    def _get_account_type_emoji(self, account_type_display: str) -> str:
        """
        Obtém emoji para tipo de conta.

        Parameters
        ----------
        account_type_display : str
            Nome do tipo da conta em português

        Returns
        -------
        str
            Emoji correspondente ao tipo de conta
        """
        emoji_mapping = {
            "Conta Corrente": "🏦",
            "Conta Salário": "💵",
            "Fundo de Garantia": "🛡️",
            "Vale Alimentação": "🍽️"
        }

        return emoji_mapping.get(account_type_display, "🏦")

    def _fetch_user_accounts(
        self, status_filter: str, tipo_filter: str
    ) -> List[Dict]:
        """
        Busca contas do usuário com filtros aplicados.

        Parameters
        ----------
        status_filter : str
            Filtro de status (Todas, Ativas, Inativas)
        tipo_filter : str
            Filtro de tipo de conta

        Returns
        -------
        List[Dict]
            Lista de contas filtradas
        """
        try:
            accounts_response = api_client.get("accounts/")
            accounts = (
                accounts_response.get('results', accounts_response)
                if isinstance(accounts_response, dict)
                else accounts_response
            )

            if not accounts:
                return []

            # Aplica filtros
            filtered_accounts = accounts

            # Filtro por status
            if status_filter == 'Ativas':
                filtered_accounts = [
                    acc for acc in filtered_accounts
                    if acc.get('is_active', True)
                ]
            elif status_filter == 'Inativas':
                filtered_accounts = [
                    acc for acc in filtered_accounts
                    if not acc.get('is_active', True)
                ]

            # Filtro por tipo
            if tipo_filter != 'Todos':
                # Converte tipo display para código API
                type_code = None
                for key, value in db_categories.ACCOUNT_TYPES.items():
                    if value == tipo_filter:
                        type_code = key
                        break

                if type_code:
                    filtered_accounts = [
                        acc for acc in filtered_accounts
                        if acc.get('account_type') == type_code
                    ]

            return filtered_accounts

        except Exception as e:
            logger.error(f"Erro ao buscar contas: {e}")
            raise

    def _handle_add_account_submission(
        self,
        account_name: str,
        account_type: str,
        institution: str,
        current_balance: float,
        agency: str,
        account_number: str,
        opening_date: date,
        minimum_balance: float,
        description: str
    ):
        """
        Processa submissão do formulário de nova conta.

        Parameters
        ----------
        name : str
            Nome da conta
        account_type : str
            Tipo da conta
        institution : str
            Instituição/Banco
        current_balance : float
            Saldo atual
        agency : str
            Agência
        account_number : str
            Número da conta
        opening_date : date
            Data de abertura
        minimum_balance : float
            Saldo mínimo
        description : str
            Descrição
        """
        if not account_name or not account_type or not institution:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte tipo para código da API
            type_code = None
            for key, val in db_categories.ACCOUNT_TYPES.items():
                if val == account_type:
                    type_code = key
                    break

            # Converte instituição para código da API
            bank_code = None
            for key, val in db_categories.INSTITUTIONS.items():
                if val == institution:
                    bank_code = key
                    break

            account_data = {
                'account_name': account_name,
                'institution_name': db_categories.TRANSLATED_INSTITUTIONS[
                    institution
                ],
                'account_type': type_code or 'CC',
                'bank_code': bank_code or 'NUB',
                'current_balance': str(current_balance),
                'minimum_balance': str(minimum_balance),
                'opening_date': opening_date.isoformat(),
                'agency': agency or '',
                'account_number': account_number or '',
                'description': description or '',
                'is_active': True
            }

            with st.spinner("💾 Salvando conta..."):
                result = api_client.post("accounts/", data=account_data)

            if result:
                st.success(f"✅ Conta '{account_name}' cadastrada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar conta!")

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
            logger.error(f"Erro ao criar conta: {e}")

    def _handle_edit_account_submission(
        self,
        account_id: int,
        name: str,
        account_type: str,
        institution: str,
        current_balance: float,
        agency: str,
        opening_date: date,
        minimum_balance: float,
        description: str,
        edit_key: str
    ):
        """
        Processa submissão da edição de conta.

        Parameters
        ----------
        account_id : int
            ID da conta
        name : str
            Novo nome
        account_type : str
            Novo tipo
        institution : str
            Nova instituição
        current_balance : float
            Novo saldo
        agency : str
            Nova agência
        opening_date : date
            Nova data de abertura
        minimum_balance : float
            Novo saldo mínimo
        description : str
            Nova descrição
        edit_key : str
            Chave da sessão para limpeza
        """
        if not name or not account_type or not institution:
            st.error("❌ Por favor, preencha todos os campos obrigatórios!")
            return

        try:
            # Converte tipo para código da API
            type_code = None
            for key, val in db_categories.ACCOUNT_TYPES.items():
                if val == account_type:
                    type_code = key
                    break

            # Converte instituição para código da API
            bank_code = None
            for key, val in db_categories.INSTITUTIONS.items():
                if val == institution:
                    bank_code = key
                    break

            update_data = {
                'account_name': name,
                'institution_name': db_categories.TRANSLATED_INSTITUTIONS[
                    institution
                ],
                'account_type': type_code or 'CC',
                'bank_code': bank_code or 'NUB',
                'current_balance': str(current_balance),
                'minimum_balance': str(minimum_balance),
                'opening_date': opening_date.isoformat(),
                'agency': agency or '',
                'description': description or ''
            }

            with st.spinner("💾 Salvando alterações..."):
                result = api_client.put(  # type: ignore
                    f"accounts/{account_id}/", data=update_data)

            if result:
                st.success("✅ Conta atualizada com sucesso!")
                st.session_state.pop(edit_key, None)
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar conta!")

        except Exception as e:
            st.error(f"❌ Erro ao atualizar: {str(e)}")
            logger.error(f"Erro ao atualizar conta {account_id}: {e}")

    def _handle_toggle_account_status(self, account: Dict):
        """
        Alterna status ativo/inativo da conta.

        Parameters
        ----------
        account : Dict
            Dados da conta
        """
        try:
            new_status = not account.get('is_active', True)
            status_text = "ativada" if new_status else "desativada"

            with st.spinner(
                f"⚙️ {'Ativando' if new_status else 'Desativando'} conta..."
            ):
                result = api_client.patch(  # type: ignore
                    f"accounts/{account['id']}/",
                    data={'is_active': new_status}
                )

            if result:
                st.success(f"✅ Conta {status_text} com sucesso!")
                st.rerun()
            else:
                st.error(
                    f"""❌ Erro ao {
                        'ativar' if new_status else 'desativar'} conta!"""
                )

        except Exception as e:
            st.error(f"❌ Erro ao alterar status: {str(e)}")
            logger.error(
                f"Erro ao alterar status da conta {account['id']}: {e}")


# Função de entrada principal
def show():
    """Função de entrada para a página de contas."""
    page = AccountsPage()
    page.render()


# Compatibilidade com estrutura existente
accounts_page = AccountsPage()
