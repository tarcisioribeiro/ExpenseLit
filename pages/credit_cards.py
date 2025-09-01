"""
Página de gestão de cartões de crédito.

Esta página permite ao usuário visualizar, criar e gerenciar
cartões de crédito integrados com a API ExpenseLit.
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
from utils.ui_utils import centered_tabs
from config.settings import db_categories


def show_missing_resource_dialog(
    resource_type: str,
    resource_name: str,
    page_name: str
):
    """Exibe diálogo quando um recurso necessário não está disponível."""
    st.warning(f"⚠️ Nenhuma {resource_name} disponível.")
    st.info(
        f"""Cadastre uma {
            resource_name
        } primeiro na página de {page_name.title()}."""
    )


logger = logging.getLogger(__name__)


class CreditCardsPage(BasePage):
    """
    Página de gestão de cartões de crédito.

    Permite operações CRUD em cartões de crédito com integração à API.
    """
    def __init__(self):
        """Inicializa a página de cartões de crédito."""
        super().__init__("Cartões de Crédito", "💳")
        self.required_permissions = ['credit_cards.view_creditcard']

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
        st.subheader("💳 Cartões de Crédito")
        self.render()

    def render(self) -> None:
        """Renderiza o conteúdo da página de cartões."""
        tab1, tab2 = centered_tabs(["💳 Cartões", "📄 Faturas"])

        with tab1:
            self._render_cards_section()
        with tab2:
            self._render_bills_section()

    def _render_cards_section(self) -> None:
        """Renderiza a seção de cartões com sub-tabs."""
        # Sub-tabs para cartões
        subtab1, subtab2 = centered_tabs(["📋 Meus Cartões", "➕ Novo Cartão"])

        with subtab1:
            self._render_cards_list()

        with subtab2:
            self._render_card_form()

    def _render_cards_list(self) -> None:
        """Renderiza a lista de cartões de crédito."""
        st.markdown("### 💳 Meus Cartões de Crédito")

        try:
            with st.spinner("🔄 Carregando cartões..."):
                time.sleep(1)
                cards = api_client.get("credit-cards/")

            if not cards:
                st.info("📝 Nenhum cartão cadastrado ainda.")
                return

            for card in cards:
                self._render_card_card(
                        card  # type: ignore
                    )

        except ApiClientError as e:
            st.error(f"Erro ao carregar cartões: {e}")
            logger.error(f"Erro ao listar cartões: {e}")

    def _render_card_card(self, card: Dict[str, Any]) -> None:
        """Renderiza um card de cartão de crédito."""
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"### 💳 {card.get('name', 'Cartão')}")
                flag_name = db_categories.CARD_FLAGS.get(
                    card.get('flag', 'MSC'), 'Master Card'
                )
                st.caption(
                    f"🏷️ {flag_name} | 👤 {card.get('on_card_name', '')}"
                )

            with col2:
                credit_limit = float(card.get('credit_limit', 0))
                max_limit = float(card.get('max_limit', 0))
                st.markdown(f"**Limite:** {format_currency_br(credit_limit)}")
                st.caption(f"Máximo: {format_currency_br(max_limit)}")

            with col3:
                validation_date = card.get('validation_date', '')
                if validation_date:
                    try:
                        val_date = datetime.strptime(
                            validation_date, '%Y-%m-%d'
                        )
                        if val_date > datetime.now():
                            st.success("✅ Válido")
                        else:
                            st.error("Expirado")
                    except:
                        st.info("📅 Data inválida")

            st.markdown("---")

    def _render_card_form(self) -> None:
        """Renderiza formulário para criação de cartão."""
        st.markdown("### ➕ Criar Novo Cartão")

        with st.form("create_card_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "💳 Nome do Cartão",
                    placeholder="Ex: Cartão Principal"
                )
                on_card_name = st.text_input(
                    "👤 Nome no Cartão",
                    placeholder="NOME SOBRENOME"
                )

                flag_display = st.selectbox(
                    "🏷️ Bandeira",
                    options=list(db_categories.TRANSLATED_CARD_FLAGS.keys())
                )
                flag = db_categories.TRANSLATED_CARD_FLAGS[flag_display]

            with col2:
                validation_date = st.date_input(
                    "📅 Data de Validade",
                    min_value=datetime.now().date()
                )

                security_code = st.text_input(
                    "🔒 CVV",
                    max_chars=4,
                    type="password",
                    help="Código de segurança (3 ou 4 dígitos)"
                )

                credit_limit = st.number_input(
                    "💰 Limite de Crédito",
                    min_value=0.01,
                    step=100.00,
                    format="%.2f"
                )

                max_limit = st.number_input(
                    "📈 Limite Máximo",
                    min_value=credit_limit,
                    step=100.00,
                    format="%.2f"
                )

            # Campos opcionais adicionais em nova seção
            st.markdown("---")
            st.markdown("**Configurações Avançadas (Opcional)**")

            col3, col4 = st.columns(2)

            with col3:
                card_number = st.text_input(
                    "💳 Número do Cartão",
                    max_chars=19,
                    type="password",
                    help="Número do cartão (será criptografado)"
                )

                closing_day = st.number_input(
                    "📅 Dia de Fechamento",
                    min_value=1,
                    max_value=31,
                    value=5,
                    help="Dia do fechamento da fatura"
                )

                due_day = st.number_input(
                    "💸 Dia de Vencimento",
                    min_value=1,
                    max_value=31,
                    value=15,
                    help="Dia de vencimento da fatura"
                )

            with col4:
                interest_rate = st.number_input(
                    "📊 Taxa de Juros (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=2.5,
                    step=0.1,
                    format="%.2f",
                    help="Taxa de juros mensal"
                )

                annual_fee = st.number_input(
                    "💳 Anuidade",
                    min_value=0.0,
                    value=0.0,
                    step=10.00,
                    format="%.2f",
                    help="Valor da anuidade"
                )

            notes = st.text_area(
                "📝 Observações",
                help="Observações sobre o cartão"
            )

            # Seleção de conta associada e proprietário
            col5, col6 = st.columns(2)

            with col5:
                try:
                    accounts = accounts_service.get_all_accounts()
                    account_options = [
                            (
                                acc['id'],
                                db_categories.INSTITUTIONS.get(
                                    acc['name'],
                                    acc['name']
                                )
                            ) for acc in accounts if acc.get('is_active', True)
                        ]

                    if account_options:
                        selected_account = st.selectbox(
                            "🏦 Conta Associada",
                            options=account_options,
                            format_func=lambda x: x[1],
                            help="Conta bancária associada ao cartão"
                        )
                        associated_account = selected_account[0]
                    else:
                        show_missing_resource_dialog(
                            "Conta", "conta", "accounts"
                        )
                        associated_account = None
                except:
                    associated_account = None

            with col6:
                # Seleção do proprietário do cartão
                try:
                    members = api_client.get("members/")
                    if members:
                        member_options = [
                               (
                                member['id'],  # type: ignore
                                member['name']  # type: ignore
                                ) for member in members if (
                                   member.get('active', True)  # type: ignore
                                )
                            ]
                        if member_options:
                            selected_owner = st.selectbox(
                                "👤 Proprietário",
                                options=member_options,
                                format_func=lambda x: x[1],
                                help="Membro proprietário do cartão"
                            )
                            owner_id = selected_owner[0]
                        else:
                            st.error("Nenhum membro disponível.")
                            owner_id = None
                    else:
                        st.error("Nenhum membro cadastrado.")
                        owner_id = None
                except ApiClientError:
                    st.error("Erro ao carregar membros.")
                    owner_id = None

            # Checkbox de confirmação
            confirm_data = st.checkbox(
                "✅ Confirmo que os dados informados estão corretos")

            if st.form_submit_button("💾 Criar Cartão", type="primary"):
                # Validações
                errors = []
                if not confirm_data:
                    errors.append(
                        "Antes, Confirme que os dados estão corretos."
                    )
                if not name:
                    errors.append("Nome do cartão é obrigatório")
                if not on_card_name:
                    errors.append("Nome no cartão é obrigatório")
                if not security_code:
                    errors.append("CVV é obrigatório")
                elif not security_code.isdigit() or len(security_code) not in [
                    3, 4
                ]:
                    errors.append("CVV deve conter apenas 3 ou 4 dígitos")
                if not associated_account:
                    errors.append("Conta associada é obrigatória")
                if not owner_id:
                    errors.append("Proprietário do cartão é obrigatório")
                if credit_limit > max_limit:
                    errors.append(
                        """
                        Limite de crédito não pode ser maior que limite máximo
                        """
                    )
                if card_number and not card_number.replace(
                    " ", ""
                ).isdigit() or len(card_number.replace(" ", "")) < 13:
                    errors.append(
                        """Número deve conter somente e ao menos 13 dígitos"""
                    )

                if errors:
                    for error in errors:
                        st.error(f"{error}")
                else:
                    card_data = {
                        'name': name,
                        'on_card_name': on_card_name.upper(),
                        'flag': flag,
                        'validation_date': format_date_for_api(
                            validation_date
                        ),
                        'security_code': security_code,
                        'credit_limit': credit_limit,
                        'max_limit': max_limit,
                        'associated_account': associated_account,
                        'owner': owner_id,  # Campo obrigatório
                        'is_active': True,  # Sempre ativo na criação
                        'closing_day': closing_day,
                        'due_day': due_day,
                        'interest_rate': interest_rate,
                        'annual_fee': annual_fee,
                        'notes': notes if notes else ""
                    }

                    # Adicionar número do cartão se fornecido
                    if card_number:
                        card_data['card_number'] = card_number.replace(" ", "")

                    self._create_card(card_data)

    def _create_card(self, card_data: Dict[str, Any]) -> None:
        """Cria um novo cartão de crédito."""
        try:
            with st.spinner("💾 Criando cartão..."):
                time.sleep(1)
                new_card = api_client.post("credit-cards/", card_data)
                print(new_card)

            st.toast("✅ Cartão criado com sucesso!")
            time.sleep(1)
            st.info(
                "🔒 **Segurança:** O CVV foi criptografado e não será exibido.")
            st.rerun()

        except ApiClientError as e:
            st.error(f"Erro ao criar cartão: {e}")
            logger.error(f"Erro ao criar cartão: {e}")

    def _render_bills_section(self) -> None:
        """Renderiza a seção de faturas de cartão."""
        st.markdown("### 📄 Faturas de Cartão de Crédito")

        # Sub-tabs para faturas
        bill_tab1, bill_tab2 = centered_tabs(
            ["📋 Minhas Faturas", "➕ Nova Fatura"])

        with bill_tab1:
            self._render_bills_list()

        with bill_tab2:
            self._render_bill_form()

    def _render_bills_list(self) -> None:
        """Renderiza a lista de faturas."""
        st.markdown("#### 📋 Faturas Cadastradas")

        try:
            with st.spinner("🔄 Carregando faturas..."):
                time.sleep(1)
                bills = api_client.get("credit-cards-bills/")

            if not bills:
                st.info("📝 Nenhuma fatura cadastrada ainda.")
                return

            for bill in bills:
                self._render_bill_card(bill)  # type: ignore

        except ApiClientError as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "recurso não encontrado" in (
                error_msg
            ):
                st.info("📝 Nenhuma fatura cadastrada ainda.")
                st.info(
                    "💡 **Dica:** "
                    +
                    "Use a aba 'Nova Fatura' para criar uma fatura."
                )
            else:
                st.error(f"Erro ao carregar faturas: {e}")
                st.info(
                    "💡 **Solução:** "
                    +
                    "Verifique sua conexão com a internet e tente novamente."
                )
                logger.error(f"Erro ao listar faturas: {e}")

    def _render_bill_card(self, bill: Dict[str, Any]) -> None:
        """Renderiza um card de fatura."""
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                # Obter nome do cartão através do ID
                card_id = bill.get('credit_card', 0)
                card_name = self._get_card_name_by_id(card_id)
                month_year = f"{bill.get('month', '')}/{bill.get('year', '')}"
                st.markdown(f"### 📄 {card_name}")
                st.caption(f"🗓️ {month_year}")

            with col2:
                start_date = bill.get('invoice_beginning_date', '')
                end_date = bill.get('invoice_ending_date', '')
                if start_date and end_date:
                    st.markdown(
                        f"""**Período:** {
                            format_date_for_display(start_date)
                        } - {format_date_for_display(end_date)}"""
                    )

            with col3:
                if bill.get('closed', False):
                    st.success("✅ Fechada")
                else:
                    st.warning("⏳ Aberta")

            st.markdown("---")

    def _render_bill_form(self) -> None:
        """Renderiza formulário para criar fatura com validações melhoradas."""
        st.markdown("#### ➕ Criar Nova Fatura")

        # Inicializar variáveis
        cards = []
        card_options = []
        credit_card_id = None
        cards_error = None

        # Tentar carregar cartões
        try:
            cards = api_client.get("credit-cards/")
            if cards:
                card_options = [
                    (
                        card['id'],  # type: ignore
                        card['name']  # type: ignore
                    ) for card in cards]
        except ApiClientError as e:
            cards_error = str(e)

        with st.form("create_bill_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Seleção de cartão com tratamento de erro melhorado
                if cards_error:
                    st.error(f"**Erro ao carregar cartões:** {cards_error}")
                    st.info(
                        "💡 **Solução:** "
                        +
                        "Verifique sua conexão e tente novamente."
                    )
                    # Ainda assim, mostra o campo para o usuário tentar
                    st.selectbox(
                        "💳 Cartão",
                        options=[],
                        help="Erro ao carregar - verifique sua conexão",
                        disabled=True
                    )
                elif not cards:
                    st.error("**Nenhum cartão disponível**")
                    st.info(
                        "💡 **Solução:** "
                        +
                        "Cadastre um cartão de crédito primeiro na aba "
                        +
                        "'Novo Cartão'."
                    )
                    # Ainda assim, mostra o campo para o usuário ver
                    st.selectbox(
                        "💳 Cartão",
                        options=[],
                        help="Nenhum cartão disponível - cadastre um primeiro",
                        disabled=True
                    )
                else:
                    selected_card = st.selectbox(
                        "💳 Cartão",
                        options=card_options,
                        format_func=lambda x: x[1],
                        help="Selecione o cartão para criar a fatura"
                    )
                    credit_card_id = selected_card[
                        0
                    ] if selected_card else None

                # Ano e mês com validação
                current_year = datetime.now().year
                current_month = datetime.now().month
                print(current_month)
                years = [
                    (
                        str(y),
                        str(y)) for y in range(
                            current_year - 1,
                            current_year + 3
                        )
                ]
                selected_year = st.selectbox(
                    "📅 Ano",
                    options=years,
                    format_func=lambda x: x[1],
                    help="Selecione o ano da fatura"
                )
                year = selected_year[0]

                months = [
                    ('Jan', 'Janeiro'),
                    ('Feb', 'Fevereiro'),
                    ('Mar', 'Março'),
                    ('Apr', 'Abril'),
                    ('May', 'Maio'),
                    ('Jun', 'Junho'),
                    ('Jul', 'Julho'),
                    ('Aug', 'Agosto'),
                    ('Sep', 'Setembro'),
                    ('Oct', 'Outubro'),
                    ('Nov', 'Novembro'),
                    ('Dec', 'Dezembro')
                ]

                selected_month = st.selectbox(
                    "📅 Mês",
                    options=months,
                    format_func=lambda x: x[1],
                    help="Selecione o mês da fatura"
                )
                month = selected_month[0]

            with col2:
                invoice_beginning_date = st.date_input(
                    "📅 Data de Início da Fatura",
                    help="Data de início do período da fatura"
                )

                invoice_ending_date = st.date_input(
                    "📅 Data de Fim da Fatura",
                    min_value=invoice_beginning_date,
                    help="Data de fim do período da fatura"
                )

                closed = st.checkbox(
                    "🔒 Fatura Fechada",
                    help="Marque se a fatura já está fechada"
                )

            # Preview da fatura - sempre mostrar se tiver dados válidos
            if credit_card_id and year and month and cards:
                with st.expander("👁️ Preview da Fatura", expanded=True):
                    card_name = next(
                        (
                            card[  # type: ignore
                                'name'
                            ] for card in cards if (
                                card['id'] == credit_card_id  # type: ignore
                            )
                        )
                    )
                    month_name = selected_month[1]
                    card_data = next(
                        (
                            card for card in cards if card[  # type: ignore
                                'id'
                            ] == credit_card_id
                        ),
                        {}
                    )

                    st.info(f"""
                    **Cartão:** {card_name}
                    **Período:** {month_name}/{year}
                    **Data Início:** {
                        format_date_for_display(invoice_beginning_date)
                    }
                    **Data Fim:** {format_date_for_display(
                        invoice_ending_date)}
                    **Status:** {'Fechada' if closed else 'Aberta'}
                    **Fechamento:** Dia {
                        card_data.get('closing_day', 'N/A')} do mês
                    **Vencimento:** Dia {
                        card_data.get('due_day', 'N/A')
                    } do mês
                    """
                    )
            elif not cards and not cards_error:
                with st.expander("👁️ Preview da Fatura", expanded=False):
                    st.warning(
                        "⚠️ Cadastre um cartão de crédito primeiro"
                        +
                        "para visualizar o preview."
                    )
            elif cards_error:
                with st.expander("👁️ Preview da Fatura", expanded=False):
                    st.error(
                        "Não é possível mostrar preview devido"
                        +
                        " ao erro ao carregar cartões."
                    )

            # Botão de submit sempre visível
            submit_clicked = st.form_submit_button(
                "💾 Criar Fatura",
                type="primary"
            )

            if submit_clicked:
                # Validações específicas
                validation_errors = []

                # Verificar se há erro de conectividade primeiro
                if cards_error:
                    validation_errors.append(
                        "Não foi possível carregar os cartões."
                        +
                        " Verifique sua conexão."
                    )
                elif not cards:
                    validation_errors.append(
                        "Nenhum cartão disponível. Cadastre um primeiro.")
                elif not credit_card_id:
                    validation_errors.append("Selecione um cartão")

                if not year or not month:
                    validation_errors.append("Selecione ano e mês")

                if invoice_beginning_date >= invoice_ending_date:
                    validation_errors.append(
                        "Data de fim deve ser posterior à data de início"
                    )

                # Só verificar duplicatas se temos um cartão válido
                if credit_card_id and not cards_error:
                    try:
                        existing_bills = api_client.get("credit-cards-bills/")
                        duplicate_bill = next((
                            bill for bill in existing_bills
                            if (bill.get('credit_card') == (  # type: ignore
                                credit_card_id
                            ) and
                                bill.get('year') == year and  # type: ignore
                                bill.get('month') == month)  # type: ignore
                        ), None)

                        if duplicate_bill:
                            validation_errors.append(
                                f"""Já existe uma fatura para {
                                    selected_month[1]}/{year} neste cartão"""
                            )

                    except ApiClientError:
                        st.warning(
                            "⚠️ Não foi possível verificar faturas duplicadas")

                if validation_errors:
                    st.error("**Erros encontrados:**")
                    for error in validation_errors:
                        st.error(f"• {error}")
                else:
                    bill_data = {
                        'credit_card': credit_card_id,
                        'year': year,
                        'month': month,
                        'invoice_beginning_date': format_date_for_api(
                            invoice_beginning_date
                        ),
                        'invoice_ending_date': format_date_for_api(
                            invoice_ending_date
                        ),
                        'closed': closed
                    }
                    self._create_bill(bill_data)

    def _get_card_name_by_id(self, card_id: int) -> str:
        """Obtém o nome do cartão pelo ID."""
        try:
            cards = api_client.get("credit-cards/")
            card = next(
                (c for c in cards if c[
                    'id'  # type: ignore
                ] == card_id), None
            )
            return card[
                'name'  # type: ignore
            ] if card else f"Cartão #{card_id}"
        except ApiClientError:
            return f"Cartão #{card_id}"

    def _create_bill(self, bill_data: Dict[str, Any]) -> None:
        """Cria uma nova fatura com mensagens de erro melhoradas."""
        try:
            with st.spinner("💾 Criando fatura..."):
                time.sleep(1)
                new_bill = api_client.post("credit-cards-bills/", bill_data)
                print(new_bill)

            st.toast("✅ Fatura criada com sucesso!")
            time.sleep(1)
            st.rerun()

        except ApiClientError as e:
            error_message = str(e).lower()

            # Mensagens de erro específicas baseadas no tipo de erro
            if "duplicate" in error_message or "already exists" in (
                error_message
            ):
                st.error("**Fatura duplicada**")
                st.info(
                    "💡 **Solução:** "
                    +
                    "Já existe uma fatura para este cartão no período."
                    +
                    " Escolha outro mês/ano."
                )
            elif "credit_card" in error_message:
                st.error("**Erro no cartão de crédito**")
                st.info(
                    "💡 **Solução:** "
                    +
                    "Verifique se o cartão ainda está ativo e tente novamente."
                )
            elif "date" in error_message:
                st.error("**Erro nas datas da fatura**")
                st.info(
                    "💡 **Solução:** "
                    +
                    "Verifique se as datas estão corretas e a "
                    +
                    "data de fim é posterior à data de início."
                )
            elif "validation" in error_message:
                st.error("**Dados inválidos**")
                st.info("💡 **Solução:**" + (
                    "Verifique se todos os campos obrigatórios "
                    ) + (
                        "foram preenchidos corretamente."
                    )
                )
            elif "not found" in error_message or "recurso não encontrado" in (
                error_message
            ):
                st.error("**Recurso não encontrado**")
                st.info(
                    "💡 **Solução:** "
                    +
                    "Verifique se o cartão de crédito existe e está ativo."
                )
                st.info(
                    "🔧 **Alternativa:** Tente cadastrar um novo cartão.")
            else:
                st.error(f"**Erro ao criar fatura:** {e}")
                st.info(
                    "💡 **Solução:** "
                    +
                    "Verifique sua conexão com a internet e tente novamente."
                )
            logger.error(f"Erro ao criar fatura: {e}")
