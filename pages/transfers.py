"""
Módulo de gerenciamento de transferências.

Este módulo implementa o CRUD completo para transferências entre contas,
seguindo o padrão visual padronizado com tabs centralizadas
e layout de 3 colunas para listagem.
"""

import logging
from datetime import date, time
from typing import Dict, Any, List
from time import sleep

import streamlit as st

from components.auth import require_auth
from services.transfers_service import transfers_service
from services.api_client import api_client, ApiClientError, ValidationError
from utils.ui_utils import ui_components, centered_tabs
from utils.date_utils import format_currency_br
from config.settings import db_categories

logger = logging.getLogger(__name__)


class TransfersPage:
    """Página de gerenciamento de transferências."""

    def __init__(self):
        """Inicializa a página de transferências."""
        self.auth = require_auth()

    def main_menu(
            self,
            token: str = None,  # type: ignore
            permissions: Dict[str, Any] = None  # type: ignore
    ):
        """Renderiza o menu principal da página de transferências."""
        self.render()

    def render(self):
        """
        Renderiza a página principal de transferências com padrão padronizado.

        Segue o padrão visual estabelecido:
        - Duas tabs centralizadas (listagem + novo registro)
        - Layout de 3 colunas para listagem
        - Popup de ações com CRUD
        """
        # Verifica e exibe erros armazenados de diálogos
        self._check_and_show_stored_errors()

        ui_components.render_page_header(
            "💸 Transferências",
            subtitle="Controle de transferências entre contas"
        )

        # Tabs principais - padrão estabelecido: 2 tabs centralizadas
        tab_list, tab_add = centered_tabs([
            "📋 Listagem de Transferências",
            "➕ Nova Transferência"
        ])

        with tab_list:
            self._render_transfers_list_standardized()

        with tab_add:
            self._render_add_transfer_form_standardized()

    def _check_and_show_stored_errors(self):
        """Verifica e exibe erros armazenados de diálogos."""
        if 'validation_error' in st.session_state:
            error_data = st.session_state.pop('validation_error')
            ui_components.show_persistent_error(
                error_message=error_data['message'],
                error_type="validacao_transferencia",
                details=error_data.get('details'),
                suggestions=error_data.get('suggestions', []),
                auto_show=False
            )

    def _render_transfers_list_standardized(self):
        """
        Renderiza a lista de transferências seguindo padrão padronizado.

        Padrão estabelecido:
        - Layout de 3 colunas por registro
        - Primeira coluna: descrição + emoji da categoria
        - Segunda coluna (central): dados como valor, contas, data
        - Terceira coluna (direita): botão de engrenagem com popup de ações
        """
        st.markdown("### 📋 Listagem de Transferências")

        # Filtros simplificados em uma linha
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            status_filter = st.selectbox(
                "🔍 Status",
                options=['Todas', 'Transferidas', 'Pendentes'],
                index=0
            )

        with col_filter2:
            category_filter = st.selectbox(
                "📂 Categoria",
                options=['Todas'] +
                list(
                    db_categories.TRANSFER_CATEGORIES.values()),
                index=0)

        with col_filter3:
            limit = st.number_input(
                "📊 Limite",
                min_value=1,
                max_value=1000,
                value=50,
                step=10
            )

        # Buscar transferências com filtros
        try:
            filters = {}
            if status_filter == 'Transferidas':
                filters['transfered'] = True
            elif status_filter == 'Pendentes':
                filters['transfered'] = False

            if category_filter != 'Todas':
                category_code = (
                    db_categories.TRANSLATED_TRANSFER_CATEGORIES.get(
                        category_filter
                    )
                )
                if category_code:
                    filters['category'] = category_code

            filters['limit'] = int(limit)

            transfers = transfers_service.get_all_transfers(**filters)

            if transfers:
                st.markdown(
                    f"**{len(transfers)} transferência(s) encontrada(s)**")
                st.markdown("---")
                self._render_transfers_three_column_layout(transfers)
            else:
                st.info(
                    "🔍 Nenhuma transferência encontrada " +
                    "com os filtros selecionados"
                )

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar transferências: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao carregar transferências: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")
            st.error(e)

    def _render_transfers_three_column_layout(self, transfers: List[Dict]):
        """
        Renderiza transferências no layout de três colunas.

        Parameters
        ----------
        transfers : List[Dict]
            Lista de transferências para exibir
        """
        for transfer in transfers:
            # Container para cada transferência
            with st.container():
                col1, col2, col3 = st.columns([3, 4, 1])

                with col1:
                    # Primeira coluna: descrição + emoji da categoria
                    category = transfer.get('category', '')
                    category_display = db_categories.TRANSFER_CATEGORIES.get(
                        category, category or 'N/A'
                    )
                    emoji = self._get_transfer_category_emoji(category)

                    # Status da transferência
                    status = "✅ Transferida" if transfer.get(
                        'transfered', False
                    ) else "⏳ Pendente"

                    st.markdown(f"""
                    **{emoji} Descrição: {transfer.get('description', 'N/A')}**

                    📂 Tipo: {category_display}

                    {status}
                    """)

                with col2:
                    # Segunda coluna: dados financeiros e contas
                    value = format_currency_br(transfer.get('value', 0))
                    transfer_date = transfer.get('date', 'N/A')
                    horary = transfer.get('horary', 'N/A')

                    # Informações das contas
                    origin_account = transfer.get('origin_account_name', 'N/A')
                    destiny_account = transfer.get(
                        'destiny_account_name', 'N/A')

                    # Taxa se houver
                    fee = transfer.get('fee', 0)
                    try:
                        fee_float = float(fee) if fee else 0.0
                    except (ValueError, TypeError):
                        fee_float = 0.0
                    fee_display = (
                        f" (Taxa: {format_currency_br(fee_float)})"
                        if fee_float > 0 else ""
                    )

                    st.markdown(f"""
                    **💰 Valor: {value}{fee_display}**

                    🏦 De: {origin_account}

                    🎯 Para: {destiny_account}

                    📅 Data: {transfer_date} às {horary}
                    """)

                with col3:
                    # Terceira coluna: botão de ações
                    if st.button(
                        "⚙️",
                        key=f"actions_{transfer['id']}",
                        help="Opções de ações",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'show_actions_{transfer["id"]}'
                        ] = True
                        st.rerun()

                # Popup de ações para esta transferência
                self._render_transfer_action_popup(transfer)
                st.markdown("---")

    def _render_transfer_action_popup(self, transfer: Dict):
        """
        Renderiza popup de ações para uma transferência específica.

        Parameters
        ----------
        transfer : Dict
            Dados da transferência
        """
        popup_key = f'show_actions_{transfer["id"]}'
        if st.session_state.get(popup_key, False):
            with st.expander(
                f"⚙️ Ações para: {transfer.get('description', 'N/A')}",
                expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📝 Editar",
                        key=f"edit_{transfer['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state[
                            f'edit_transfer_{transfer["id"]}'
                        ] = transfer
                        st.session_state[popup_key] = False
                        st.rerun()

                with col2:
                    action_text = "✅ Confirmar" if not transfer.get(
                        'transfered', False
                    ) else "⏳ Pendente"
                    if st.button(
                        action_text,
                        key=f"toggle_{transfer['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        self._handle_toggle_transfer_status(transfer)
                        st.session_state[popup_key] = False
                        st.rerun()

                with col3:
                    if st.button(
                        "❌ Fechar",
                        key=f"close_{transfer['id']}",
                        use_container_width=True
                    ):
                        st.session_state[popup_key] = False
                        st.rerun()

        # Renderiza modal de edição
        self._render_edit_transfer_modal(transfer)

    def _handle_toggle_transfer_status(self, transfer: Dict[str, Any]):
        """
        Alterna o status transferido/pendente de uma transferência.

        Parameters
        ----------
        transfer : Dict[str, Any]
            Dados da transferência
        """
        try:
            new_status = not transfer.get('transfered', False)
            transfer_data = {'transfered': new_status}

            with st.spinner("🔄 Atualizando status..."):
                transfers_service.update_transfer(
                    transfer['id'], transfer_data)

            status_text = (
                "confirmada" if new_status else "marcada como pendente"
            )
            st.success(f"✅ Transferência {status_text} com sucesso!")
            sleep(2)
            st.rerun()

        except ApiClientError as e:
            st.error(f"❌ Erro ao atualizar transferência: {str(e)}")
            sleep(3)
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar transferência: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")
            st.error(e)
            sleep(3)

    def _render_edit_transfer_modal(self, transfer: Dict[str, Any]):
        """
        Renderiza modal de edição para uma transferência.

        Parameters
        ----------
        transfer : Dict[str, Any]
            Dados da transferência para editar
        """
        edit_key = f'edit_transfer_{transfer["id"]}'

        if st.session_state.get(edit_key):
            st.markdown("### ✏️ Editar Transferência")

            with st.form(f"edit_form_{transfer['id']}", clear_on_submit=False):
                col1, col2 = st.columns(2)

                with col1:
                    description = st.text_input(
                        "📝 Descrição *",
                        value=transfer.get('description', ''),
                        help="Descrição da transferência"
                    )

                    value = st.number_input(
                        "💰 Valor *",
                        min_value=0.01,
                        value=float(transfer.get('value', 0)),
                        step=0.01,
                        format="%.2f"
                    )

                with col2:
                    # Categoria atual
                    current_category = transfer.get('category', 'pix')
                    categories = list(
                        db_categories.TRANSFER_CATEGORIES.values())
                    category_index = 0

                    for idx, cat in enumerate(categories):
                        if db_categories.TRANSLATED_TRANSFER_CATEGORIES.get(
                                cat) == current_category:
                            category_index = idx
                            break

                    category_display = st.selectbox(
                        "📂 Categoria *",
                        options=categories,
                        index=category_index,
                        format_func=(
                            lambda x: self._format_category_display(x)
                        )
                    )

                    transfered = st.checkbox(
                        "✅ Transferida",
                        value=transfer.get('transfered', False)
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
                    self._process_transfer_edit(
                        transfer['id'],
                        description=description or '',
                        value=value,
                        category_display=category_display,
                        transfered=transfered
                    )
                    st.session_state[edit_key] = None
                    st.rerun()

                if canceled:
                    st.session_state[edit_key] = None
                    st.rerun()

    def _process_transfer_edit(
        self,
        transfer_id: int,
        description: str,
        value: float,
        category_display: str,
        transfered: bool
    ):
        """
        Processa a edição de uma transferência.

        Parameters
        ----------
        transfer_id : int
            ID da transferência a ser editada
        description : str
            Descrição da transferência
        value : float
            Valor da transferência
        category_display : str
            Categoria exibida
        transfered : bool
            Status da transferência
        """
        # Validações básicas
        validation_errors = []

        if not description.strip():
            validation_errors.append("Descrição é obrigatória")

        if value <= 0:
            validation_errors.append("Valor deve ser maior que zero")

        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            return

        try:
            # Converte categoria para código da API
            category_code = db_categories.TRANSLATED_TRANSFER_CATEGORIES.get(
                category_display
            )
            if not category_code:
                st.error("❌ Categoria selecionada inválida")
                return

            # Prepara dados para API
            transfer_data = {
                "description": description.strip(),
                "value": str(value),
                "category": category_code,
                "transfered": transfered
            }

            with st.spinner("💾 Salvando alterações..."):
                result = transfers_service.update_transfer(
                    transfer_id, transfer_data)

            if result:
                st.success("✅ Transferência atualizada com sucesso!")
                st.balloons()
                sleep(3)
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar transferência")

        except ValidationError as e:
            st.error(f"❌ Erro de validação: {str(e)}")
            sleep(3)

        except ApiClientError as e:
            st.error(f"❌ Erro na API: {str(e)}")
            sleep(3)

        except Exception as e:
            logger.error(f"Erro inesperado ao editar transferência: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")
            st.error(e)
            sleep(3)

    def _get_transfer_category_emoji(self, category: str) -> str:
        """
        Retorna o emoji correspondente à categoria da transferência.

        Parameters
        ----------
        category : str
            Código da categoria

        Returns
        -------
        str
            Emoji correspondente
        """
        return db_categories.TRANSFER_CATEGORY_EMOJIS.get(category, "💰")

    def _format_category_display(self, category_display: str) -> str:
        """
        Formata a exibição da categoria com emoji.

        Parameters
        ----------
        category_display : str
            Nome da categoria para exibição

        Returns
        -------
        str
            Categoria formatada com emoji
        """
        category_code = (
            db_categories.TRANSLATED_TRANSFER_CATEGORIES.get(
                category_display, ""
            )
        )
        emoji = self._get_transfer_category_emoji(category_code)
        return f"{emoji} {category_display}"

    def _render_add_transfer_form_standardized(self):
        """
        Renderiza formulário de adição de transferência.

        Padrão estabelecido:
        - Campos obrigatórios realçados
        - Valores traduzidos com emojis
        - Validação em tempo real
        """
        st.markdown("### ➕ Nova Transferência")

        with st.form("add_transfer_form", clear_on_submit=True):
            # Layout em duas colunas
            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input(
                    "📝 Descrição *",
                    placeholder="Ex: Transferência para conta poupança",
                    help="Descrição da transferência"
                )

                value = st.number_input(
                    "💰 Valor *",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Valor a ser transferido"
                )

                # Categoria
                categories = list(db_categories.TRANSFER_CATEGORIES.values())
                category = st.selectbox(
                    "📂 Categoria *",
                    options=categories,
                    format_func=lambda x: self._format_category_display(x),
                    help="Tipo de transferência")

                transfered = st.checkbox(
                        "✅ Marcar como transferida",
                        value=False,
                        help="Marque se a transferência já foi realizada"
                    )

            with col2:
                # Data e horário
                transfer_date = st.date_input(
                    "📅 Data *",
                    value=date.today(),
                    help="Data da transferência"
                )

                horary = st.time_input(
                    "🕐 Horário *",
                    value=time(12, 0),
                    help="Horário da transferência"
                )

                # Contas - buscar via API
                try:
                    accounts_response = api_client.get(
                        "accounts/", params={"is_active": "true"})

                    if accounts_response:
                        account_options = {
                            account.get(  # type: ignore
                                'account_name',
                                ''
                            ): account.get(  # type: ignore
                                'id',
                                0
                            )
                            for account in accounts_response
                        }
                        account_names = list(account_options.keys())

                        origin_account_name = st.selectbox(
                            "🏦 Conta de Origem *",
                            options=account_names,
                            help="Conta que enviará o dinheiro"
                        )

                        destiny_account_name = st.selectbox(
                            "🎯 Conta de Destino *",
                            options=account_names,
                            help="Conta que receberá o dinheiro"
                        )
                    else:
                        st.error("❌ Nenhuma conta ativa encontrada")
                        account_options = {}
                        origin_account_name = None
                        destiny_account_name = None

                except ApiClientError as e:
                    st.error(f"❌ Erro ao carregar contas: {str(e)}")
                    account_options = {}
                    origin_account_name = None
                    destiny_account_name = None

            # Campos opcionais
            with st.expander("📋 Informações Adicionais (Opcionais)"):
                col_opt1, col_opt2 = st.columns(2)

                with col_opt1:
                    fee = st.number_input(
                        "💸 Taxa",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        help="Taxa cobrada pela transferência"
                    )

                    transaction_id = st.text_input(
                        "🔗 ID da Transação",
                        placeholder="Ex: PIX123456789",
                        help="Identificador único da transação"
                    )

                with col_opt2:
                    confirmation_code = st.text_input(
                        "✅ Código de Confirmação",
                        placeholder="Ex: ABC123",
                        help="Código de confirmação da transferência"
                    )

                notes = st.text_area(
                    "📝 Observações",
                    placeholder="Informações adicionais sobre a transferência",
                    help="Observações sobre a transferência")

            # Botão de submit
            submitted = st.form_submit_button(
                "💾 Cadastrar Transferência",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if origin_account_name and destiny_account_name:
                    self._process_transfer_creation(
                        description=description,
                        value=value,
                        transfer_date=transfer_date,
                        horary=horary,
                        category=category,
                        origin_account_name=origin_account_name,
                        destiny_account_name=destiny_account_name,
                        account_options=account_options,
                        fee=fee,
                        transaction_id=transaction_id,
                        confirmation_code=confirmation_code,
                        transfered=transfered,
                        notes=notes
                    )
                else:
                    st.error("❌ Selecione as contas de origem e destino")

    def _process_transfer_creation(
        self,
        description: str,
        value: float,
        transfer_date: date,
        horary: time,
        category: str,
        origin_account_name: str,
        destiny_account_name: str,
        account_options: Dict[str, int],
        fee: float,
        transaction_id: str,
        confirmation_code: str,
        transfered: bool,
        notes: str
    ):
        """
        Processa a criação de uma nova transferência.

        Parameters
        ----------
        description : str
            Descrição da transferência
        value : float
            Valor da transferência
        transfer_date : date
            Data da transferência
        horary : time
            Horário da transferência
        category : str
            Categoria da transferência
        origin_account_name : str
            Nome da conta de origem
        destiny_account_name : str
            Nome da conta de destino
        account_options : Dict[str, int]
            Mapeamento de nomes para IDs de contas
        fee : float
            Taxa da transferência
        transaction_id : str
            ID da transação
        confirmation_code : str
            Código de confirmação
        transfered : bool
            Status de transferência
        notes : str
            Observações
        """
        # Validação local primeiro
        validation_errors = transfers_service.validate_transfer_data({
            'description': description,
            'value': value,
            'date': transfer_date,
            'horary': horary,
            'category': db_categories.TRANSLATED_TRANSFER_CATEGORIES.get(
                category
            ),
            'origin_account': (
                account_options.get(origin_account_name) if (
                    origin_account_name
                ) else None
            ),
            'destiny_account': (
                account_options.get(destiny_account_name) if (
                    destiny_account_name
                ) else None
            )
        })

        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            sleep(10)
            return

        try:
            # Prepara dados para API
            transfer_data = {
                "description": description.strip(),
                "value": str(value),
                "date": transfer_date.strftime('%Y-%m-%d'),
                "horary": horary.strftime('%H:%M:%S'),
                "category": db_categories.TRANSLATED_TRANSFER_CATEGORIES.get(
                    category
                ),
                "origin_account": account_options.get(origin_account_name),
                "destiny_account": account_options.get(destiny_account_name),
                "transfered": transfered}

            # Adiciona campos opcionais se preenchidos
            try:
                fee_float = float(fee) if fee else 0.0
            except (ValueError, TypeError):
                fee_float = 0.0
            if fee_float > 0:
                transfer_data["fee"] = str(fee_float)
            if transaction_id.strip():
                transfer_data["transaction_id"] = transaction_id.strip()
            if confirmation_code.strip():
                transfer_data["confirmation_code"] = confirmation_code.strip()
            if notes.strip():
                transfer_data["notes"] = notes.strip()

            with st.spinner("💾 Cadastrando transferência..."):
                result = transfers_service.create_transfer(transfer_data)

            if result:
                st.success("✅ Transferência cadastrada com sucesso!")
                st.balloons()
                sleep(3)
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar transferência")
                sleep(2.5)

        except ValidationError as e:
            # Extrai detalhes específicos do erro da API
            error_message = str(e)
            validation_details = []

            # Tenta extrair detalhes específicos da ValidationError
            if "origin_account" in error_message:
                validation_details.append(
                    "🏦 Conta de origem é obrigatória"
                )
            if "destiny_account" in error_message:
                validation_details.append(
                    "🎯 Conta de destino é obrigatória"
                )
            if "value" in error_message:
                validation_details.append(
                    "💰 Verifique o valor da transferência"
                )
            if "date" in error_message:
                validation_details.append(
                    "📅 Verifique a data da transferência"
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
            logger.error(f"Erro inesperado ao criar transferência: {e}")
            st.error("❌ Erro inesperado. Tente novamente.")
            st.error(e)
            sleep(5)
