"""
Módulo de gerenciamento de cartões de crédito.

Este módulo implementa o CRUD completo para cartões de crédito,
seguindo o padrão visual padronizado com tabs centralizadas
e layout de 3 colunas para listagem.
"""

import logging
from datetime import date
from typing import Dict, List, Any, Optional
from time import sleep

import streamlit as st

from components.auth import require_auth
from services.credit_cards_service import credit_cards_service
from services.api_client import api_client, ApiClientError, ValidationError
from utils.ui_utils import ui_components, centered_tabs
from utils.date_utils import format_currency_br
from config.settings import db_categories


logger = logging.getLogger(__name__)


class CreditCardsPage:
    """Página de gerenciamento de cartões de crédito."""

    def __init__(self):
        """Inicializa a página de cartões de crédito."""
        self.auth = require_auth()

    def main_menu(
            self,
            token: str = None,  # type: ignore
            permissions: Dict[str, Any] = None  # type: ignore
    ):
        """Renderiza o menu principal da página de cartões de crédito."""
        self.render()

    def render(self):
        """
        Renderiza a página principal de cartões de crédito.

        Segue o padrão visual estabelecido:
        - Duas tabs centralizadas (listagem + novo registro)
        - Layout de 3 colunas para listagem
        - Popup de ações com CRUD
        """
        # Verifica e exibe erros armazenados de diálogos
        self._check_and_show_stored_errors()

        ui_components.render_page_header(
            "💳 Cartões de Crédito",
            subtitle="Gerenciamento de cartões e faturas"
        )

        # Tabs principais - padrão estabelecido: 2 tabs centralizadas
        tab_list, tab_add = centered_tabs([
            "📋 Listagem de Cartões",
            "➕ Novo Cartão"
        ])

        with tab_list:
            self._render_credit_cards_list_standardized()

        with tab_add:
            self._render_add_credit_card_form_standardized()

    def _check_and_show_stored_errors(self):
        """Verifica e exibe erros armazenados de diálogos."""
        if 'validation_error' in st.session_state:
            error_data = st.session_state.pop('validation_error')
            ui_components.show_persistent_error(
                error_message=error_data['message'],
                error_type="validacao_cartao",
                details=error_data.get('details'),
                suggestions=error_data.get('suggestions', []),
                auto_show=False
            )

    def _render_credit_cards_list_standardized(self):
        """
        Renderiza a lista de cartões seguindo padrão padronizado.

        Padrão estabelecido:
        - Layout de 3 colunas por registro
        - Primeira coluna: nome do cartão + emoji da bandeira
        - Segunda coluna (central): dados como limite, vencimento, conta
        - Terceira coluna (direita): botão de engrenagem com popup de ações
        """
        st.markdown("### 📋 Listagem de Cartões de Crédito")

        # Filtros simplificados em uma linha
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            status_filter = st.selectbox(
                "🔍 Status",
                options=['Todos', 'Ativos', 'Inativos'],
                index=0
            )

        with col_filter2:
            card_flags = list(db_categories.CARD_FLAGS.values())
            flag_filter = st.selectbox(
                "💳 Bandeira",
                options=['Todas'] + card_flags,
                index=0,
                format_func=lambda x: f"🗂️ {x}" if x == 'Todas' else f"💳 {x}"
            )

        # Busca cartões do usuário logado
        try:
            with st.spinner("🔄 Carregando seus cartões..."):
                credit_cards = self._fetch_user_credit_cards(
                    status_filter, flag_filter)

            if not credit_cards:
                st.info("📋 Você ainda não possui cartões cadastrados.")
                return

            st.markdown("---")

            # Lista cartões seguindo padrão de 3 colunas
            for card in credit_cards:
                self._render_credit_card_item_standardized(card)

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar cartões: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao carregar cartões: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")

    def _fetch_user_credit_cards(
            self, status_filter: str, flag_filter: str
    ) -> List[Dict[str, Any]]:
        """
        Busca cartões do usuário aplicando filtros.

        Parameters
        ----------
        status_filter : str
            Filtro de status dos cartões
        flag_filter : str
            Filtro de bandeira dos cartões

        Returns
        -------
        List[Dict[str, Any]]
            Lista de cartões filtrados
        """
        credit_cards = credit_cards_service.list_credit_cards()

        # Aplica filtro de status
        if status_filter == 'Ativos':
            credit_cards = [c for c in credit_cards if c.get('is_active')]
        elif status_filter == 'Inativos':
            credit_cards = [c for c in credit_cards if not c.get('is_active')]

        # Aplica filtro de bandeira
        if flag_filter != 'Todas':
            bandeira_key = db_categories.TRANSLATED_CARD_FLAGS.get(
                flag_filter
            )
            if bandeira_key:
                credit_cards = [
                    c for c in credit_cards
                    if c.get('flag') == bandeira_key
                ]

        return credit_cards

    def _render_credit_card_item_standardized(self, card: Dict[str, Any]):
        """
        Renderiza um item de cartão seguindo padrão de 3 colunas.

        Parameters
        ----------
        card : Dict[str, Any]
            Dados do cartão de crédito
        """
        # Layout de 3 colunas - padrão estabelecido
        col1, col2, col3 = st.columns([3, 4, 1])

        with col1:
            # Primeira coluna: Nome + dados do cartão
            bandeira_emoji = self._get_card_flag_emoji(card.get('flag', ''))
            bandeira_nome = db_categories.CARD_FLAGS.get(
                card.get('flag', 'MSC'), 'Master Card'
            )

            # Status do cartão
            status = "✅ Ativo" if card.get('is_active') else "⏸️ Inativo"

            st.markdown(f"""
            **{bandeira_emoji} Nome: {card.get('name', 'Sem nome')}**

            💳 Bandeira: {bandeira_nome}

            👤 Nome no cartão: {card.get('on_card_name', 'N/A')}

            Status: {status}
            """)

        with col2:
            # Segunda coluna: Dados financeiros e datas
            limite = format_currency_br(card.get('credit_limit', 0))
            limite_max = format_currency_br(card.get('max_limit', 0))
            closing_day = card.get('closing_day', '-')
            due_day = card.get('due_day', '-')

            st.markdown(f"""
            **💰 Limite atual: {limite}**

            🎯 Limite máximo: {limite_max}

            📅 Fechamento: dia {closing_day}

            💸 Vencimento: dia {due_day}
            """)

        with col3:
            # Terceira coluna: Botão de ações
            if st.button("⚙️", key=f"actions_{card['id']}",
                         help="Opções do cartão"):
                self._show_credit_card_actions_popup(card)

        # Popup de ações para este cartão
        self._render_credit_card_action_popup(card)

        # Separador visual entre cartões
        st.markdown("---")

    def _get_card_flag_emoji(self, flag: str) -> str:
        """
        Retorna o emoji correspondente à bandeira do cartão.

        Parameters
        ----------
        flag : str
            Código da bandeira

        Returns
        -------
        str
            Emoji correspondente à bandeira
        """
        emoji_mapping = {
            "MSC": "🔴",  # Mastercard
            "VSA": "🔵",  # Visa
            "ELO": "🟡",  # Elo
            "EXP": "🟢",  # American Express
            "HCD": "🟠"   # Hipercard
        }
        return emoji_mapping.get(flag, "💳")

    def _show_credit_card_actions_popup(self, card: Dict[str, Any]):
        """
        Exibe popup com ações do cartão.

        Parameters
        ----------
        card : Dict[str, Any]
            Dados do cartão
        """
        st.session_state[f'show_actions_{card["id"]}'] = True

    def _render_credit_card_action_popup(self, card: Dict[str, Any]):
        """
        Renderiza popup de ações para um cartão específico.

        Parameters
        ----------
        card : Dict[str, Any]
            Dados do cartão
        """
        popup_key = f'show_actions_{card["id"]}'
        if st.session_state.get(popup_key, False):
            with st.expander(
                f"⚙️ Ações para: {card.get('name', 'N/A')}",
                expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📝 Editar",
                        key=f"edit_{card['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[f'edit_card_{card["id"]}'] = card
                        st.session_state[popup_key] = False
                        st.rerun()

                with col2:
                    action_text = "⏸️ Desativar" if card.get(
                        'is_active', True
                    ) else "✅ Ativar"
                    if st.button(
                        action_text,
                        key=f"toggle_{card['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        self._handle_toggle_card_status(card)
                        st.session_state[popup_key] = False
                        st.rerun()

                with col3:
                    if st.button(
                        "❌ Fechar",
                        key=f"close_{card['id']}",
                        use_container_width=True
                    ):
                        st.session_state[popup_key] = False
                        st.rerun()

        # Renderiza modal de edição
        self._render_edit_card_modal(card)

    def _handle_toggle_card_status(self, card: Dict[str, Any]):
        """
        Alterna o status ativo/inativo de um cartão.

        Parameters
        ----------
        card : Dict[str, Any]
            Dados do cartão
        """
        try:
            new_status = not card.get('is_active', True)
            card_data = {'is_active': new_status}

            with st.spinner("🔄 Atualizando status..."):
                credit_cards_service.update_credit_card(card['id'], card_data)

            status_text = "ativado" if new_status else "desativado"
            st.success(f"✅ Cartão {status_text} com sucesso!")
            sleep(2)
            st.rerun()

        except ApiClientError as e:
            st.error(f"❌ Erro ao atualizar cartão: {str(e)}")
            sleep(3)
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar cartão: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")
            sleep(3)

    def _render_edit_card_modal(self, card: Dict[str, Any]):
        """
        Renderiza modal de edição para um cartão.

        Parameters
        ----------
        card : Dict[str, Any]
            Dados do cartão para editar
        """
        edit_key = f'edit_card_{card["id"]}'

        if st.session_state.get(edit_key):
            st.markdown("### ✏️ Editar Cartão")

            with st.form(f"edit_form_{card['id']}", clear_on_submit=False):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input(
                        "🏷️ Nome do Cartão *",
                        value=card.get('name', ''),
                        help="Nome para identificar o cartão"
                    )

                    on_card_name = st.text_input(
                        "👤 Nome no Cartão *",
                        value=card.get('on_card_name', ''),
                        help="Nome impresso no cartão"
                    )

                with col2:
                    # Bandeira atual
                    current_flag = card.get('flag', 'MSC')
                    flags = list(db_categories.CARD_FLAGS.values())
                    flag_index = 0

                    for idx, flag in enumerate(flags):
                        if db_categories.TRANSLATED_CARD_FLAGS.get(
                                flag) == current_flag:
                            flag_index = idx
                            break

                    flag_display = st.selectbox(
                        "💳 Bandeira *",
                        options=flags,
                        index=flag_index,
                        format_func=lambda x: f"💳 {x}",
                        help="Bandeira do cartão"
                    )

                    credit_limit = st.number_input(
                        "💰 Limite Atual *",
                        min_value=0.0,
                        value=float(card.get('credit_limit', 0)),
                        step=100.0,
                        format="%.2f",
                        help="Limite atual do cartão"
                    )

                # Status
                is_active = st.checkbox(
                    "✅ Cartão Ativo",
                    value=card.get('is_active', True)
                )

                # Botões do formulário
                col_submit, col_cancel = st.columns(2)

                with col_submit:
                    submitted = st.form_submit_button(
                        "💾 Salvar Alterações",
                        type="primary",
                        use_container_width=True
                    )

                with col_cancel:
                    canceled = st.form_submit_button(
                        "❌ Cancelar",
                        use_container_width=True
                    )

                if submitted:
                    self._process_card_edit(
                        card['id'],
                        name=name or '',
                        on_card_name=on_card_name or '',
                        flag_display=flag_display,
                        credit_limit=credit_limit,
                        is_active=is_active
                    )
                    st.session_state[edit_key] = None
                    st.rerun()

                if canceled:
                    st.session_state[edit_key] = None
                    st.rerun()

    def _process_card_edit(
        self,
        card_id: int,
        name: str,
        on_card_name: str,
        flag_display: str,
        credit_limit: float,
        is_active: bool
    ):
        """
        Processa a edição de um cartão.

        Parameters
        ----------
        card_id : int
            ID do cartão a ser editado
        name : str
            Nome do cartão
        on_card_name : str
            Nome impresso no cartão
        flag_display : str
            Bandeira exibida
        credit_limit : float
            Limite atual
        is_active : bool
            Status ativo
        """
        # Validações básicas
        validation_errors = []

        if not name.strip():
            validation_errors.append("Nome do cartão é obrigatório")

        if not on_card_name.strip():
            validation_errors.append("Nome no cartão é obrigatório")

        if credit_limit <= 0:
            validation_errors.append("Limite deve ser maior que zero")

        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            return

        try:
            # Converte bandeira para código da API
            flag_code = db_categories.TRANSLATED_CARD_FLAGS.get(flag_display)
            if not flag_code:
                st.error("❌ Bandeira selecionada inválida")
                return

            # Prepara dados para API
            card_data = {
                "name": name.strip(),
                "on_card_name": on_card_name.strip().upper(),
                "flag": flag_code,
                "credit_limit": str(credit_limit),
                "is_active": is_active
            }

            with st.spinner("💾 Salvando alterações..."):
                result = credit_cards_service.update_credit_card(
                    card_id, card_data)

            if result:
                st.success("✅ Cartão atualizado com sucesso!")
                st.balloons()
                sleep(3)
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar cartão")

        except ValidationError as e:
            st.error(f"❌ Erro de validação: {str(e)}")
            sleep(3)

        except ApiClientError as e:
            st.error(f"❌ Erro na API: {str(e)}")
            sleep(3)

        except Exception as e:
            logger.error(f"Erro inesperado ao editar cartão: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")
            sleep(3)

    def _render_add_credit_card_form_standardized(self):
        """
        Renderiza formulário de adição de cartão seguindo padrão padronizado.

        Padrão estabelecido:
        - Campos obrigatórios realçados
        - Valores traduzidos com emojis
        - Validação em tempo real
        """
        st.markdown("### ➕ Novo Cartão de Crédito")

        with st.form("add_credit_card_form", clear_on_submit=False):
            # Informações básicas do cartão
            st.markdown("#### 💳 Informações do Cartão")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "🏷️ Nome do Cartão *",
                    placeholder="Ex: Cartão Principal",
                    help="Nome para identificar o cartão"
                )

                on_card_name = st.text_input(
                    "👤 Nome no Cartão *",
                    placeholder="Ex: JOÃO DA SILVA",
                    help="Nome impresso no cartão (maiúsculas)"
                )

            with col2:
                # Bandeira com emojis
                flags = list(db_categories.CARD_FLAGS.values())
                flag_display = st.selectbox(
                    "💳 Bandeira *",
                    options=flags,
                    format_func=lambda x: f"💳 {x}",
                    help="Bandeira do cartão"
                )

                validation_date = st.date_input(
                    "📅 Data de Validade *",
                    min_value=date.today(),
                    value=date(date.today().year + 4, 12, 31),
                    format="DD/MM/YYYY",
                    help="Data de vencimento do cartão (deve ser futura)"
                )

                security_code = st.text_input(
                    "Código de segurança *",
                    placeholder="000",
                    type="password"
                )

            # Informações financeiras
            st.markdown("#### 💰 Informações Financeiras")

            col3, col4 = st.columns(2)

            with col3:
                credit_limit = st.number_input(
                    "💰 Limite Atual *",
                    min_value=0.0,
                    value=1000.0,
                    step=100.0,
                    format="%.2f",
                    help="Limite atual do cartão"
                )

                max_limit = st.number_input(
                    "🎯 Limite Máximo *",
                    min_value=credit_limit,
                    value=max(credit_limit * 2, 5000.0),
                    step=100.0,
                    format="%.2f",
                    help="Limite máximo disponível"
                )

            with col4:
                interest_rate = st.number_input(
                    "📊 Taxa de Juros (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=2.5,
                    step=0.1,
                    format="%.2f",
                    help="Taxa de juros mensal"
                )

                annual_fee = st.number_input(
                    "💳 Anuidade",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    format="%.2f",
                    help="Valor da anuidade anual"
                )

            # Configurações de fatura
            st.markdown("#### 📅 Configurações da Fatura")

            col5, col6 = st.columns(2)

            with col5:
                closing_day = st.number_input(
                    "📅 Dia de Fechamento *",
                    min_value=1,
                    max_value=28,
                    value=15,
                    help="Dia do mês que a fatura fecha"
                )

            with col6:
                due_day = st.number_input(
                    "💸 Dia de Vencimento *",
                    min_value=1,
                    max_value=31,
                    value=10,
                    help="Dia do mês para pagamento"
                )

            # Conta associada
            st.markdown("#### 🏦 Conta Associada")

            try:
                accounts = api_client.get("accounts/")
                if accounts:
                    account_options = {}
                    for acc in accounts:
                        name = acc.get(  # type: ignore
                            'name',
                            'Sem nome'
                        )
                        acc_type = acc.get(  # type: ignore
                            'account_type',
                            ''
                        )
                        type_desc = db_categories.ACCOUNT_TYPES.get(
                            acc_type, 'Tipo desconhecido'
                        )
                        key = f"{name} - {type_desc}"
                        account_options[key] = acc[  # type: ignore
                            'id'
                        ]

                    selected_account_name = st.selectbox(
                        "🏦 Conta para Débito *",
                        options=list(account_options.keys()),
                        help="Conta bancária associada para débito automático"
                    )
                    associated_account = account_options.get(
                        selected_account_name
                    )
                else:
                    st.warning(
                        "⚠️ Nenhuma conta encontrada. "
                        "Cadastre uma conta primeiro."
                    )
                    associated_account = None
            except Exception:
                st.error("❌ Erro ao carregar contas")
                associated_account = None

            # Observações
            notes = st.text_area(
                "📝 Observações",
                placeholder="Informações adicionais sobre o cartão...",
                help="Observações opcionais"
            )

            # Status
            is_active = st.checkbox("✅ Cartão Ativo", value=True)

            # Botão de submissão
            submitted = st.form_submit_button(
                "💾 Cadastrar Cartão",
                type="primary",
                use_container_width=True
            )

            if submitted:
                self._process_credit_card_creation(
                    name=name,
                    on_card_name=on_card_name,
                    flag_display=flag_display,
                    validation_date=validation_date,
                    security_code=security_code,
                    credit_limit=credit_limit,
                    max_limit=max_limit,
                    interest_rate=interest_rate,
                    annual_fee=annual_fee,
                    closing_day=closing_day,
                    due_day=due_day,
                    associated_account=associated_account,
                    notes=notes,
                    is_active=is_active
                )

    def _process_credit_card_creation(
            self,
            name: str,
            on_card_name: str,
            flag_display: str,
            validation_date: date,
            security_code: str,
            credit_limit: float,
            max_limit: float,
            interest_rate: float,
            annual_fee: float,
            closing_day: int,
            due_day: int,
            associated_account: Optional[int],
            notes: str,
            is_active: bool
    ):
        """
        Processa a criação de um novo cartão.

        Parameters
        ----------
        name : str
            Nome do cartão
        on_card_name : str
            Nome impresso no cartão
        flag_display : str
            Bandeira exibida
        validation_date : date
            Data de validade
        credit_limit : float
            Limite atual
        max_limit : float
            Limite máximo
        interest_rate : float
            Taxa de juros
        annual_fee : float
            Anuidade
        closing_day : int
            Dia de fechamento
        due_day : int
            Dia de vencimento
        associated_account : Optional[int]
            ID da conta associada
        notes : str
            Observações
        is_active : bool
            Status ativo
        """
        # Validações básicas
        validation_errors = []

        if not name.strip():
            validation_errors.append("Nome do cartão é obrigatório")

        if not on_card_name.strip():
            validation_errors.append("Nome no cartão é obrigatório")

        if credit_limit <= 0:
            validation_errors.append("Limite deve ser maior que zero")

        if max_limit < credit_limit:
            validation_errors.append(
                "Limite máximo deve ser maior ou igual ao atual"
            )

        if not associated_account:
            validation_errors.append("Conta associada é obrigatória")

        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            sleep(10)
            return

        try:
            # Converte bandeira para código da API
            flag_code = db_categories.TRANSLATED_CARD_FLAGS.get(flag_display)
            if not flag_code:
                st.error("❌ Bandeira selecionada inválida")
                sleep(10)
                return

            # Prepara dados para API
            card_data = {
                "name": name.strip(),
                "on_card_name": on_card_name.strip().upper(),
                "flag": flag_code,
                "validation_date": validation_date.isoformat(),
                "security_code": security_code,
                "credit_limit": str(credit_limit),
                "max_limit": str(max_limit),
                "interest_rate": str(interest_rate),
                "annual_fee": str(annual_fee),
                "closing_day": closing_day,
                "due_day": due_day,
                "associated_account": associated_account,
                "is_active": is_active,
                "notes": notes.strip() if notes else ""
            }

            with st.spinner("💾 Cadastrando cartão..."):
                result = credit_cards_service.create_credit_card(card_data)
                sleep(2.5)

            if result:
                st.success("✅ Cartão cadastrado com sucesso!")
                st.balloons()
                sleep(5)

                # Limpa o formulário
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar cartão")
                sleep(2.5)

        except ValidationError as e:
            # Extrai detalhes específicos do erro da API
            error_message = str(e)
            validation_details = []

            # Tenta extrair detalhes específicos da ValidationError
            if "validation_date" in error_message:
                validation_details.append(
                    "📅 Data de validade deve ser posterior à data atual"
                )
            if "credit_limit" in error_message:
                validation_details.append(
                    "💰 Verifique o valor do limite de crédito"
                )
            if "associated_account" in error_message:
                validation_details.append(
                    "🏦 Conta associada é obrigatória"
                )
            if "security_code" in error_message:
                validation_details.append(
                    "🔒 Código de segurança deve ter 3 ou 4 dígitos"
                )

            # Se não encontrou detalhes específicos, usa mensagem genérica
            if not validation_details:
                validation_details = [
                    'Verifique se todos os campos obrigatórios' +
                    ' estão preenchidos',
                    'Confirme se os valores estão no formato correto']

            # Exibe erros imediatamente
            st.error("❌ Erro de validação no cadastro:")
            for detail in validation_details:
                st.error(f"  • {detail}")

            sleep(2)  # Mantém para garantir que o usuário veja o erro

        except ApiClientError as e:
            st.error(f"❌ Erro na API: {str(e)}")
            sleep(5)

        except Exception as e:
            logger.error(f"Erro inesperado ao criar cartão: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")
            sleep(5)
