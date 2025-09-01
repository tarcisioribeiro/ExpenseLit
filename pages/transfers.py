"""
Página de gestão de transferências.

Esta página permite ao usuário visualizar, criar, editar e excluir
transferências integradas com a API ExpenseLit.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any
from utils.date_utils import (
    format_date_for_display,
    format_date_for_api,
    format_currency_br
)

import streamlit as st

from pages.router import BasePage
from services.api_client import api_client, ApiClientError
from services.accounts_service import accounts_service
from services.pdf_generator import pdf_generator
from utils.ui_utils import centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


class TransfersPage(BasePage):
    """
    Página de gestão de transferências.

    Permite operações CRUD em transferências com integração à API.
    """
    def __init__(self):
        super().__init__("Transferências", "🔄")
        self.required_permissions = ['transfers.view_transfer']

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
        st.subheader("🔄 Transferências")
        self.render()

    def render(self) -> None:
        """Renderiza o conteúdo da página de transferências."""
        tab1, tab2, tab3 = centered_tabs(
            [
                "📋 Minhas Transferências",
                "➕ Nova Transferência",
                "📊 Resumo"
            ]
        )

        with tab1:
            self._render_transfers_list()

        with tab2:
            self._render_transfer_form()

        with tab3:
            self._render_transfers_summary()

    def _render_transfers_list(self) -> None:
        """Renderiza a lista de transferências."""
        st.markdown("### 🔄 Lista de Transferências")
        try:
            with st.spinner("🔄 Carregando transferências..."):
                time.sleep(1)
                transfers = api_client.get("transfers/")

            if not transfers:
                st.info("📝 Nenhuma transferência cadastrada ainda.")
                return

            # Filtros
            col1, col2 = st.columns(2)

            with col1:
                transfer_categories = {
                    'doc': 'DOC',
                    'ted': 'TED',
                    'pix': 'PIX'
                }
                filter_category = st.selectbox(
                    "📂 Tipo",
                    options=["Todos"] + list(transfer_categories.values())
                )

            with col2:
                filter_status = st.selectbox(
                    "📊 Status",
                    options=["Todos", "Transferidas", "Pendentes"]
                )

            # Aplica filtros
            filtered_transfers = transfers

            if filter_category != "Todos":
                category_key = next(
                    k for k,
                    v in transfer_categories.items() if v == filter_category
                )
                filtered_transfers = [
                    t for t in filtered_transfers if t.get(  # type: ignore
                        'category'
                    ) == category_key
                ]

            if filter_status == "Transferidas":
                filtered_transfers = [
                    t for t in filtered_transfers if t.get(  # type: ignore
                        'transfered', False
                    )
                ]
            elif filter_status == "Pendentes":
                filtered_transfers = [
                    t for t in filtered_transfers if not t.get(  # type: ignore
                        'transfered', False
                    )
                ]

            # Estatísticas rápidas
            total_transfers = sum(
                float(
                    t.get('value', 0)  # type: ignore
                ) for t in filtered_transfers
            )
            completed_transfers = sum(
                float(
                    t.get('value', 0)  # type: ignore
                ) for t in filtered_transfers if (
                    t.get('transfered', False)  # type: ignore
                )
            )
            pending_transfers = total_transfers - completed_transfers

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total", format_currency_br(total_transfers))
            with col2:
                st.metric(
                    "✅ Transferidas", format_currency_br(completed_transfers))
            with col3:
                st.metric("⏳ Pendentes", format_currency_br(pending_transfers))

            st.markdown("---")

            for transfer in filtered_transfers:
                self._render_transfer_card(transfer)  # type: ignore

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar transferências: {e}")
            logger.error(f"Erro ao listar transferências: {e}")

    def _render_transfer_card(self, transfer: Dict[str, Any]) -> None:
        """Renderiza um card de transferência."""
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                description = transfer.get('description', 'Transferência')
                category = transfer.get('category', 'pix')
                category_emoji = {"doc": "📄", "ted": "🏦", "pix": "⚡"}.get(
                    category, "🔄")
                category_name = {"doc": "DOC", "ted": "TED", "pix": "PIX"}.get(
                    category, category.upper())
                origin_account = transfer.get(
                    'origin_account_name', 'Conta Origem')
                destiny_account = transfer.get(
                    'destiny_account_name', 'Conta Destino')

                st.markdown(f"### {category_emoji} {description}")
                st.caption(f"📂 {category_name}")
                st.caption(
                    f"""🏦 {db_categories.INSTITUTIONS.get(
                        origin_account, origin_account)
                    } → {db_categories.INSTITUTIONS.get(
                        destiny_account, destiny_account)
                    }"""
                )

            with col2:
                value = float(transfer.get('value', 0))
                date_str = format_date_for_display(transfer.get('date', ''))
                time_str = transfer.get('horary', '00:00:00')

                st.markdown(f"**{format_currency_br(value)}**")
                st.caption(f"📅 {date_str} às {time_str}")

            with col3:
                if transfer.get('transfered', False):
                    st.success("✅ Transferida")
                else:
                    st.warning("⏳ Pendente")

            with col4:
                transfer_id = transfer.get('id')
                with st.popover("⚙️ Ações"):
                    if st.button(
                        "✏️ Editar",
                        key=f"edit_transfer_{transfer_id}",
                        width='stretch'
                    ):
                        st.session_state[
                            f'edit_transfer_{transfer_id}'
                        ] = transfer
                        st.rerun()

                        toggle_text = (
                            "⏳ Marcar Pendente" if transfer.get(
                                    'transfered',
                                    False
                                ) else "✅ Marcar Transferida"
                            )
                        if st.button(
                            toggle_text,
                            key=f"toggle_transfer_{transfer_id}",
                            width='stretch'
                        ):
                            self._toggle_transfer_status(
                                transfer_id, not transfer.get(
                                    'transfered',
                                    False
                                )
                            )

                    if st.button(
                        "📄 Gerar PDF",
                        key=f"pdf_btn_transfer_{transfer_id}",
                        width='stretch'
                    ):
                        self._generate_transfer_pdf(transfer)

                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_transfer_{transfer_id}",
                        width='stretch'
                    ):
                        self._delete_transfer(
                            transfer_id, description  # type: ignore
                        )

            # Formulário de edição inline se ativo
            if st.session_state.get(f'edit_transfer_{transfer_id}'):
                self._render_edit_form(transfer)

            st.markdown("---")

    def _render_edit_form(self, transfer: Dict[str, Any]) -> None:
        """Renderiza formulário de edição inline."""
        transfer_id = transfer.get('id')

        st.markdown("#### ✏️ Editando Transferência")

        with st.form(f"edit_transfer_form_{transfer_id}"):
            col1, col2 = st.columns(2)

            with col1:
                new_description = st.text_input(
                    "📝 Descrição",
                    value=transfer.get('description', '')
                )

                new_value = st.number_input(
                    "💰 Valor",
                    min_value=0.01,
                    value=float(transfer.get('value', 0)),
                    step=0.01,
                    format="%.2f"
                )

                categories = [('doc', 'DOC'), ('ted', 'TED'), ('pix', 'PIX')]
                current_category = transfer.get('category', 'pix')
                current_index = next(
                    i for i,
                    (
                        k,
                        v
                    ) in enumerate(categories) if k == current_category
                )

                new_category = st.selectbox(
                    "📂 Tipo de Transferência",
                    options=categories,
                    index=current_index,
                    format_func=lambda x: x[1]
                )

            with col2:
                date_value = transfer.get('date', '')
                try:
                    current_date = datetime.strptime(
                        date_value,  # type: ignore
                        '%Y-%m-%d'
                    ).date()
                except ValueError:
                    current_date = datetime.now().date()

                new_date = st.date_input(
                    "📅 Data",
                    value=current_date,
                    format="DD/MM/YYYY"
                )

                current_time = datetime.strptime(
                    transfer.get('horary', '00:00:00'), '%H:%M:%S'
                ).time()

                new_time = st.time_input(
                    "🕐 Horário",
                    value=current_time
                )

                new_transfered = st.checkbox(
                    "✅ Transferência realizada",
                    value=transfer.get('transfered', False)
                )

                col_submit, col_cancel = st.columns(2)

            with col_submit:
                if st.form_submit_button(
                    "💾 Salvar Alterações",
                    type="primary"
                ):
                    update_data = {
                        'description': new_description,
                        'value': new_value,
                        'date': format_date_for_api(new_date),
                        'horary': new_time.strftime('%H:%M:%S'),
                        'category': new_category[0],
                        'origin_account': transfer.get('origin_account'),
                        'destiny_account': transfer.get('destiny_account'),
                        'transfered': new_transfered
                    }
                    self._update_transfer(
                        transfer_id, update_data  # type: ignore
                    )

            with col_cancel:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.pop(f'edit_transfer_{transfer_id}', None)
                    st.rerun()

    def _render_transfer_form(self) -> None:
        """Renderiza formulário para criar transferência."""
        st.markdown("### ➕ Criar Nova Transferência")

        with st.form("create_transfer_form"):
            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input(
                    "📝 Descrição",
                    placeholder="Ex: Transferência para conta poupança..."
                )

                value = st.number_input(
                    "💰 Valor",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f"
                )

                categories = [('doc', 'DOC'), ('ted', 'TED'), ('pix', 'PIX')]
                selected_category = st.selectbox(
                    "📂 Tipo de Transferência",
                    options=categories,
                    format_func=lambda x: x[1]
                )
                category = selected_category[0]

                # Seleção de conta origem
                try:
                    accounts = accounts_service.get_all_accounts()
                    if not accounts:
                        self._show_no_accounts_dialog()
                        return

                    active_accounts = [acc for acc in accounts if acc.get(
                            'is_active',
                            True
                        )
                    ]
                    if len(active_accounts) < 2:
                        self._show_insufficient_accounts_dialog()
                        return

                    account_options = [
                        (
                            acc['id'],
                            db_categories.INSTITUTIONS.get(
                                acc['name'],
                                acc['name']
                            )
                        ) for acc in active_accounts
                    ]

                    # Selecionar primeira conta como origem
                    selected_origin = st.selectbox(
                        "🏦 Conta de Origem",
                        options=account_options,
                        index=0,
                        format_func=lambda x: x[1],
                        help="Conta de onde sairá o dinheiro"
                    )
                    origin_account_id = selected_origin[0]
                except ApiClientError:
                    st.error("❌ Erro ao carregar contas")
                    return

            with col2:
                transfer_date = st.date_input(
                    "📅 Data da Transferência",
                    value=datetime.now().date(),
                    format="DD/MM/YYYY"
                )

                transfer_time = st.time_input(
                    "🕐 Horário",
                    value=datetime.now().time()
                )

                # Seleção de conta destino
                try:
                    default_destiny_index = len(account_options) - 1 if len(
                        account_options
                    ) > 1 else 0
                    selected_destiny = st.selectbox(
                        "🏦 Conta de Destino",
                        options=account_options,
                        index=default_destiny_index,
                        format_func=lambda x: x[1],
                        help="Conta para onde irá o dinheiro"
                    )
                    destiny_account_id = selected_destiny[0]
                except ApiClientError:
                    st.error("❌ Erro ao carregar contas")
                    return

                transfered = st.checkbox(
                    "✅ Transferência já foi realizada",
                    value=False
                )

            # Checkbox de confirmação
                confirm_data = st.checkbox(
                    "✅ Confirmo que os dados informados estão corretos"
                )

            # Validação de contas diferentes e saldo
                validation_messages = []

            if origin_account_id == destiny_account_id:
                validation_messages.append(
                    "A conta de origem deve ser diferente da conta de destino!"
                )

            # Verificação de saldo em tempo real
            if value and origin_account_id and origin_account_id != (
                destiny_account_id
            ):
                try:
                    # Calcular saldo da conta de origem
                    origin_account_balance = self._calculate_account_balance(
                        origin_account_id
                    )

                    if origin_account_balance is not None:
                        remaining_balance = origin_account_balance - value

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "💰 Saldo Atual",
                                format_currency_br(origin_account_balance)
                            )
                        with col2:
                            st.metric(
                                "📤 Valor Transferência",
                                format_currency_br(value)
                            )
                        with col3:
                            if remaining_balance >= 0:
                                st.metric(
                                    "✅ Saldo Após",
                                    format_currency_br(remaining_balance),
                                    delta=f"-{format_currency_br(value)}"
                                )
                            else:
                                st.metric(
                                    "❌ Saldo Após",
                                    format_currency_br(remaining_balance),
                                    delta=f"-{format_currency_br(value)}"
                                )
                                validation_messages.append(
                                    f"""⚠️ Saldo insuficiente! Faltam {
                                        format_currency_br(
                                            abs(remaining_balance)
                                        )
                                    }"""
                                    )
                    else:
                        st.warning(
                            "⚠️ Não foi possível verificar o saldo"
                            +
                            "da conta de origem"
                        )

                except Exception as e:
                    st.warning("⚠️ Erro ao verificar saldo da conta")
                    logger.warning(f"Erro ao verificar saldo: {e}")

            # Mostrar mensagens de validação
            for msg in validation_messages:
                st.error(msg)

            if st.form_submit_button("💾 Criar Transferência", type="primary"):
                # Validações completas
                errors = []

                if not confirm_data:
                    errors.append(
                        "Antes, confirme que os dados estão corretos.")

                if not description:
                    errors.append("Descrição é obrigatória")

                if not value or value <= 0:
                    errors.append("Valor deve ser maior que zero")

                if origin_account_id == destiny_account_id:
                    errors.append(
                        "Contas de origem e destino devem ser diferentes")

                # Validação de saldo antes de criar
                if value and origin_account_id:
                    try:
                        balance = self._calculate_account_balance(
                            origin_account_id
                        )
                        if balance is not None and balance < value:
                            errors.append(
                                f"""Saldo insuficiente na conta de origem: {
                                    format_currency_br(balance)
                                }""")
                    except Exception:
                        errors.append(
                            "Não foi possível verificar o saldo da conta")

                if errors:
                    st.error("❌ **Erros encontrados:**")
                    for error in errors:
                        st.error(f"• {error}")
                else:
                    transfer_data = {
                        'description': description,
                        'value': value,
                        'date': format_date_for_api(transfer_date),
                        'horary': transfer_time.strftime('%H:%M:%S'),
                        'category': category,
                        'origin_account': origin_account_id,
                        'destiny_account': destiny_account_id,
                        'transfered': transfered
                    }
                    self._create_transfer(transfer_data)

    def _calculate_account_balance(self, account_id: int) -> float:
        """
        Calcula o saldo de uma conta baseado em receitas,
        despesas e transferências.

        Parameters
        ----------
        account_id : int
            ID da conta

        Returns
        -------
        float
            Saldo da conta ou None se erro
        """
        try:
            balance = 0.0

            # Somar receitas da conta
            revenues = api_client.get("revenues/")
            account_revenues = [r for r in revenues if r.get(  # type: ignore
                'account') == account_id
            ]
            balance += sum(
                float(
                    r.get('value', 0)  # type: ignore
                ) for r in account_revenues
            )

            # Subtrair despesas da conta
            expenses = api_client.get("expenses/")
            account_expenses = [e for e in expenses if e.get(  # type: ignore
                'account') == account_id]
            balance -= sum(float(
                e.get('value', 0)  # type: ignore
            ) for e in account_expenses)

            # Transferências onde a conta é origem (subtrai)
            transfers = api_client.get("transfers/")
            outgoing_transfers = [
                t for t in transfers if t.get(  # type: ignore
                    'origin_account'
                ) == account_id and t.get(  # type: ignore
                    'transfered',
                    False
                )
            ]
            balance -= sum(
                float(
                    t.get('value', 0)  # type: ignore
                ) for t in outgoing_transfers
            )

            # Transferências onde a conta é destino (soma)
            incoming_transfers = [
                t for t in transfers if t.get(  # type: ignore
                    'destiny_account'
                ) == account_id and t.get('transfered', False)]  # type: ignore
            balance += sum(float(
                    t.get('value', 0)  # type: ignore
                ) for t in incoming_transfers
            )

            return balance

        except Exception as e:
            logger.error(f"Erro ao calcular saldo da conta {account_id}: {e}")
            return None  # type: ignore

    def _render_transfers_summary(self) -> None:
        """Renderiza resumo das transferências."""
        st.markdown("### 📊 Resumo de Transferências")

        try:
            with st.spinner("📊 Carregando estatísticas..."):
                time.sleep(1)
                transfers = api_client.get("transfers/")

            if not transfers:
                st.info("📝 Nenhuma transferência encontrada.")
                return

            total_transfers = len(transfers)
            total_value = sum(
                float(
                    t.get(  # type: ignore
                        'value',
                        0
                    )
                ) for t in transfers
            )
            completed_value = sum(
                float(
                    t.get('value', 0)  # type: ignore
                ) for t in transfers if (
                    t.get('transfered', False)  # type: ignore
                )
            )
            pending_value = total_value - completed_value
            completed_transfers = sum(
                1 for t in transfers if (
                    t.get('transfered', False)  # type: ignore
                )
            )
            pending_transfers = total_transfers - completed_transfers

            # Estatísticas por categoria
            pix_count = sum(
                1 for t in transfers if t.get(  # type: ignore
                    'category'
                ) == 'pix'
            )
            ted_count = sum(
                1 for t in transfers if t.get(  # type: ignore
                    'category'
                ) == 'ted'
            )
            doc_count = sum(
                1 for t in transfers if t.get(  # type: ignore
                    'category'
                ) == 'doc'
            )

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total de Transferências", total_transfers)
            with col2:
                st.metric("💰 Valor Total", format_currency_br(total_value))
            with col3:
                st.metric(
                    "✅ Valor Transferido", format_currency_br(completed_value))
            with col4:
                st.metric(
                    "⏳ Valor Pendente", format_currency_br(pending_value)
                )

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Transferências Realizadas", completed_transfers)
            with col2:
                st.metric("⏳ Transferências Pendentes", pending_transfers)
            with col3:
                st.metric("⚡ PIX", pix_count)
            with col4:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("🏦 TED", ted_count)
                with col_b:
                    st.metric("📄 DOC", doc_count)

        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar estatísticas: {e}")
            logger.error(f"Erro ao carregar resumo de transferências: {e}")

    def _create_transfer(self, transfer_data: Dict[str, Any]) -> None:
        """Cria uma nova transferência."""
        try:
            with st.spinner("💾 Criando transferência..."):
                time.sleep(1)
                new_transfer = api_client.post("transfers/", transfer_data)
                print(new_transfer)

            st.toast("✅ Transferência criada com sucesso!")
            time.sleep(1)
            st.rerun()

        except ApiClientError as e:
            st.error(f"❌ Erro ao criar transferência: {e}")
            logger.error(f"Erro ao criar transferência: {e}")

    def _update_transfer(
        self,
        transfer_id: int,
        transfer_data: Dict[
            str,
            Any
        ]
    ) -> None:
        """Atualiza uma transferência."""
        try:
            with st.spinner("💾 Atualizando transferência..."):
                time.sleep(1)
                updated_transfer = api_client.put(
                    f"transfers/{transfer_id}/", transfer_data
                )
                print(updated_transfer)

            st.success("✅ Transferência atualizada com sucesso!")
            st.session_state.pop(f'edit_transfer_{transfer_id}', None)
            st.rerun()

        except ApiClientError as e:
            st.error(f"❌ Erro ao atualizar transferência: {e}")
            logger.error(f"Erro ao atualizar transferência {transfer_id}: {e}")

    def _toggle_transfer_status(
        self,
        transfer_id: int,
        is_transfered: bool
    ) -> None:
        """Alterna o status de uma transferência."""
        try:
            with st.spinner(
                f"""{
                    'Marcando como transferida' if is_transfered else (
                        'Marcando como pendente'
                        )
                    }..."""
            ):
                transfer_data = api_client.get(f"transfers/{transfer_id}/")

                update_data = {
                    'description': transfer_data.get('description'),
                    'value': transfer_data.get('value'),
                    'date': transfer_data.get('date'),
                    'horary': transfer_data.get('horary'),
                    'category': transfer_data.get('category'),
                    'origin_account': transfer_data.get('origin_account'),
                    'destiny_account': transfer_data.get('destiny_account'),
                    'transfered': is_transfered
                }

                api_client.put(f"transfers/{transfer_id}/", update_data)

            status_text = "transferida" if is_transfered else "pendente"
            st.success(f"✅ Transferência marcada como {status_text}!")
            st.rerun()

        except ApiClientError as e:
            st.error(f"❌ Erro ao alterar status: {e}")
            logger.error(
                f"Erro ao alterar status da transferência {transfer_id}: {e}"
            )

    def _delete_transfer(self, transfer_id: int, description: str) -> None:
        """Exclui uma transferência após confirmação."""
        confirm_key = f"confirm_delete_transfer_{transfer_id}"

        if not st.session_state.get(confirm_key, False):
            st.session_state[confirm_key] = True
            st.rerun()

            st.warning(
                f"""⚠️ **Tem certeza que deseja excluir a transferência '{
                    description
                }'?**"""
            )
            st.error("🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🗑️ Sim, Excluir",
                key=f"final_confirm_delete_transfer_{transfer_id}",
                type="primary",
                width='stretch'
            ):
                try:
                    with st.spinner("🗑️ Excluindo transferência..."):
                        api_client.delete(f"transfers/{transfer_id}/")
                        st.success(
                            f"""✅ Transferência '{
                                description
                            }' excluída com sucesso!"""
                        )
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                except ApiClientError as e:
                    st.error(f"❌ Erro ao excluir transferência: {e}")
                    logger.error(
                        f"Erro ao excluir transferência {transfer_id}: {e}"
                    )
                    st.session_state.pop(confirm_key, None)

        with col2:
            if st.button(
                "❌ Cancelar",
                key=f"cancel_delete_transfer_{transfer_id}",
                width='stretch'
            ):
                st.session_state.pop(confirm_key, None)
                st.rerun()

    def _generate_transfer_pdf(self, transfer: Dict[str, Any]) -> None:
        """Gera e oferece download do PDF da transferência."""
        if pdf_generator is None:
            st.error(
                "❌ Gerador de PDF não disponível."
                +
                "Instale o ReportLab: pip install reportlab"
            )
            return
        try:
            with st.spinner("📄 Gerando comprovante..."):
                # Buscar dados das contas
                origin_account_data = None
                destination_account_data = None
                try:
                    accounts = accounts_service.get_all_accounts()
                    origin_account_data = next(
                        (
                            acc for acc in accounts if acc[
                                'id'
                            ] == transfer.get(
                                'origin_account'
                            )
                        ), None
                    )
                    destination_account_data = next(
                        (
                            acc for acc in accounts if acc[
                                'id'
                            ] == transfer.get('destiny_account')), None
                    )
                except Exception:
                    pass

                # Gerar PDF
                pdf_buffer = pdf_generator.generate_transfer_receipt(
                    transfer,
                    origin_account_data,
                    destination_account_data
                )

                # Nome do arquivo
                description = transfer.get('description', 'transferencia')
                date_str = transfer.get('date', '').replace('-', '_')
                filename = f"""comprovante_transferencia_{
                    description
                    }_{date_str}.pdf"""

                # Oferecer download
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_transfer_{transfer.get('id')}"
                )

                # Preview do PDF
                st.success("✅ Comprovante gerado com sucesso!")
                try:
                    pdf_buffer.seek(0)
                    if hasattr(st, 'pdf'):
                        st.pdf(pdf_buffer.getvalue())
                    else:
                        st.info(
                            "📄 PDF gerado."
                            +
                            "Use o botão de download para visualizar."
                        )
                except Exception as e:
                    logger.warning(f"Erro ao exibir preview do PDF: {e}")
            st.info(
                "📄 PDF gerado. Use o botão de download para visualizar.")
        except Exception as e:
            st.error(f"❌ Erro ao gerar comprovante: {e}")
            logger.error(
                f"Erro ao gerar PDF da transferência {transfer.get('id')}: {e}"
            )

    def _show_no_accounts_dialog(self):
        """Mostra dialog quando não há contas cadastradas."""
        @st.dialog("🏦 Nenhuma Conta Encontrada")
        def show_dialog():
            st.error("❌ **Nenhuma conta disponível**")
            st.markdown("""
Para criar transferências, você precisa  \
    ter pelo menos **2 contas** cadastradas.

            **O que fazer:**
            1. Vá para a página **Contas**
            2. Cadastre suas contas bancárias
            3. Volte aqui para criar transferências
            """)

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(
                    "🏦 Ir para Contas",
                    type="primary",
                    use_container_width=True
                ):
                    st.switch_page("pages/accounts.py")
            with col2:
                if st.button("✅ Ok", use_container_width=True):
                    st.rerun()
                    show_dialog()

    def _show_insufficient_accounts_dialog(self):
        """Mostra dialog quando há menos de 2 contas."""
        @st.dialog("🏦 Contas Insuficientes")
        def show_dialog():
            st.warning("⚠️ **Apenas 1 conta encontrada**")
            st.markdown("""
Para fazer transferências, você precisa \
     ter pelo menos **2 contas diferentes**.

            **O que fazer:**
            1. Vá para a página **Contas**
            2. Cadastre uma segunda conta bancária
            3. Volte aqui para criar transferências
            """)

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(
                    "🏦 Ir para Contas",
                    type="primary",
                    use_container_width=True
                ):
                    st.switch_page("pages/accounts.py")
            with col2:
                if st.button("✅ Ok", use_container_width=True):
                    st.rerun()

        show_dialog()
