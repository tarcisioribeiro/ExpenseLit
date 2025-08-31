"""
Página de gestão de empréstimos.

Esta página permite ao usuário visualizar, criar, editar e excluir
empréstimos integrados com a API ExpenseLit.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from utils.date_utils import format_date_for_display, format_date_for_api, format_currency_br

import streamlit as st

from pages.router import BasePage
from services.api_client import api_client, ApiClientError
from services.accounts_service import accounts_service
from services.pdf_generator import pdf_generator
from utils.ui_utils import centered_tabs
from config.settings import db_categories


logger = logging.getLogger(__name__)


class LoansPage(BasePage):
    """
    Página de gestão de empréstimos.
    
    Permite operações CRUD em empréstimos com integração à API.
    """
    
    def __init__(self):
        super().__init__("Empréstimos", "🤝")
        # self.required_permissions = ['loans.view_loan']  # Desabilitado - superusuários têm acesso total

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
        st.subheader("🤝 Empréstimos")
        self.render()

    def render(self) -> None:
        """Renderiza o conteúdo da página de empréstimos."""
        tab1, tab2, tab3, tab4 = centered_tabs([
            "📋 Meus Empréstimos", 
            "💸 Realizar Empréstimo", 
            "💰 Tomar Empréstimo", 
            "📊 Resumo"
        ])
        
        with tab1:
            self._render_loans_list()
        
        with tab2:
            self._render_give_loan_form()
        
        with tab3:
            self._render_receive_loan_form()
        
        with tab4:
            self._render_loans_summary()

    def _render_loans_list(self) -> None:
        """Renderiza a lista de empréstimos."""
        st.markdown("### 🤝 Lista de Empréstimos")
        
        try:
            with st.spinner("🔄 Carregando empréstimos..."):
                time.sleep(1)
                loans = api_client.get("loans/")
            
            if not loans:
                st.info("📝 Nenhum empréstimo cadastrado ainda.")
                return
            
            # Estatísticas rápidas
            total_loans = sum(float(loan.get('value', 0)) for loan in loans)
            paid_loans = sum(float(loan.get('payed_value', 0)) for loan in loans)
            pending_loans = total_loans - paid_loans
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total", format_currency_br(total_loans))
            with col2:
                st.metric("✅ Pago", format_currency_br(paid_loans))
            with col3:
                st.metric("⏳ Pendente", format_currency_br(pending_loans))
            
            st.markdown("---")
            
            for loan in loans:
                self._render_loan_card(loan)
                
        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar empréstimos: {e}")
            logger.error(f"Erro ao listar empréstimos: {e}")

    def _render_loan_card(self, loan: Dict[str, Any]) -> None:
        """Renderiza um card de empréstimo."""
        loan_id = loan.get('id')
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                description = loan.get('description', 'Empréstimo')
                category = loan.get('category', 'others')
                category_emoji = db_categories.EXPENSE_CATEGORY_EMOJIS.get(category, "🤝")
                category_name = db_categories.EXPENSE_CATEGORIES.get(category, category)
                benefited = loan.get('benefited_name', 'Beneficiado')
                creditor = loan.get('creditor_name', 'Credor')
                
                st.markdown(f"### {category_emoji} {description}")
                st.caption(f"📂 {category_name} | 👥 {creditor} → {benefited}")
            
            with col2:
                value = float(loan.get('value', 0))
                payed_value = float(loan.get('payed_value', 0))
                remaining = value - payed_value
                date_str = format_date_for_display(loan.get('date', ''))
                time_str = loan.get('horary', '00:00:00')
                
                st.markdown(f"**Total:** {format_currency_br(value)}")
                st.caption(f"💸 Pago: {format_currency_br(payed_value)}")
                st.caption(f"⏳ Restante: {format_currency_br(remaining)}")
                st.caption(f"📅 {date_str} às {time_str}")
            
            with col3:
                if loan.get('payed', False):
                    st.success("✅ Quitado")
                else:
                    st.warning("⏳ Pendente")
            
            with col4:
                with st.popover("⚙️ Ações"):
                    if st.button(
                        "✏️ Editar",
                        key=f"edit_loan_{loan_id}",
                        width='stretch'
                    ):
                        st.session_state[f'edit_loan_data_{loan_id}'] = loan
                        st.rerun()
                    
                    toggle_text = ("⏳ Marcar Pendente" if loan.get('payed', False) 
                                 else "✅ Marcar Quitado")
                    if st.button(
                        toggle_text,
                        key=f"toggle_loan_{loan_id}",
                        width='stretch'
                    ):
                        self._toggle_loan_payment(loan_id, not loan.get('payed', False))
                    
                    if st.button(
                        "💰 Pagamento",
                        key=f"payment_loan_{loan_id}",
                        width='stretch'
                    ):
                        st.session_state[f'payment_loan_data_{loan_id}'] = loan
                        st.rerun()
                    
                    if st.button(
                        "📄 Gerar PDF",
                        key=f"pdf_btn_loan_{loan_id}",
                        width='stretch'
                    ):
                        self._generate_loan_pdf(loan)
                    
                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_loan_{loan_id}",
                        width='stretch'
                    ):
                        self._delete_loan(loan_id, description)
            
            # Formulário de pagamento inline se ativo
            if st.session_state.get(f'payment_loan_data_{loan_id}'):
                self._render_payment_form(loan)
            
            # Formulário de edição inline se ativo
            if st.session_state.get(f'edit_loan_data_{loan_id}'):
                self._render_edit_loan_form(loan)
            
            st.markdown("---")

    def _render_payment_form(self, loan: Dict[str, Any]) -> None:
        """Renderiza formulário para pagamento de empréstimo."""
        loan_id = loan.get('id')
        value = float(loan.get('value', 0))
        payed_value = float(loan.get('payed_value', 0))
        remaining = value - payed_value
        
        st.markdown("#### 💰 Registrar Pagamento")
        
        with st.form(f"payment_loan_form_{loan_id}"):
            payment_value = st.number_input(
                "💵 Valor do Pagamento",
                min_value=0.01,
                max_value=float(remaining),
                value=float(remaining),
                step=0.01,
                format="%.2f"
            )
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.form_submit_button("💾 Registrar Pagamento", type="primary"):
                    new_payed_value = payed_value + payment_value
                    is_fully_paid = new_payed_value >= value
                    
                    update_data = {
                        'description': loan.get('description'),
                        'value': loan.get('value'),
                        'payed_value': new_payed_value,
                        'date': loan.get('date'),
                        'horary': loan.get('horary'),
                        'category': loan.get('category'),
                        'account': loan.get('account'),
                        'benefited': loan.get('benefited'),
                        'creditor': loan.get('creditor'),
                        'payed': is_fully_paid
                    }
                    self._update_loan(loan_id, update_data)
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.pop(f'payment_loan_data_{loan_id}', None)
                    st.rerun()

    def _render_edit_loan_form(self, loan: Dict[str, Any]) -> None:
        """Renderiza formulário para editar empréstimo."""
        loan_id = loan.get('id')
        
        st.markdown("#### ✏️ Editar Empréstimo")
        
        with st.form(f"edit_loan_form_{loan_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                description = st.text_input(
                    "📝 Descrição",
                    value=loan.get('description', ''),
                    placeholder="Ex: Empréstimo para compra de carro..."
                )
                
                value = st.number_input(
                    "💰 Valor do Empréstimo",
                    min_value=0.01,
                    value=float(loan.get('value', 0)),
                    step=0.01,
                    format="%.2f",
                    help="Valor total do empréstimo"
                )
                
                # Categoria atual
                current_category = loan.get('category', 'others')
                category_display_options = list(db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys())
                current_category_display = None
                for display, code in db_categories.TRANSLATED_EXPENSE_CATEGORIES.items():
                    if code == current_category:
                        current_category_display = display
                        break
                
                category_display = st.selectbox(
                    "📂 Categoria",
                    options=category_display_options,
                    index=category_display_options.index(current_category_display) if current_category_display else 0
                )
                category = db_categories.TRANSLATED_EXPENSE_CATEGORIES[category_display]
            
            with col2:
                # Data e horário atuais
                current_date = datetime.strptime(loan.get('date', ''), '%Y-%m-%d').date() if loan.get('date') else datetime.now().date()
                current_time = datetime.strptime(loan.get('horary', '00:00:00'), '%H:%M:%S').time() if loan.get('horary') else datetime.now().time()
                
                loan_date = st.date_input(
                    "📅 Data do Empréstimo",
                    value=current_date,
                    format="DD/MM/YYYY"
                )
                
                loan_time = st.time_input(
                    "🕐 Horário",
                    value=current_time
                )
                
                # Seleção de conta
                try:
                    accounts = accounts_service.get_all_accounts()
                    if accounts:
                        account_options = [(acc['id'], db_categories.INSTITUTIONS.get(acc['name'], acc['name'])) for acc in accounts if acc.get('is_active', True)]
                        current_account_index = 0
                        for i, (acc_id, _) in enumerate(account_options):
                            if acc_id == loan.get('account'):
                                current_account_index = i
                                break
                        
                        selected_account = st.selectbox(
                            "🏦 Conta",
                            options=account_options,
                            format_func=lambda x: x[1],
                            index=current_account_index
                        )
                        account_id = selected_account[0] if selected_account else None
                    else:
                        st.error("❌ Nenhuma conta disponível.")
                        account_id = None
                except ApiClientError as e:
                    st.error(f"❌ Erro ao carregar contas: {e}")
                    account_id = None
                
                # Seleção de membros
                try:
                    members = api_client.get("members/")
                    if members:
                        member_options = [(member['id'], member['name']) for member in members if member.get('active', True)]
                        
                        # Encontrar índices atuais
                        current_benefited_index = 0
                        current_creditor_index = 0
                        for i, (member_id, _) in enumerate(member_options):
                            if member_id == loan.get('benefited'):
                                current_benefited_index = i
                            if member_id == loan.get('creditor'):
                                current_creditor_index = i
                        
                        selected_benefited = st.selectbox(
                            "👤 Beneficiado",
                            options=member_options,
                            format_func=lambda x: x[1],
                            index=current_benefited_index,
                            help="Quem recebeu o empréstimo"
                        )
                        benefited_id = selected_benefited[0] if selected_benefited else None
                        
                        selected_creditor = st.selectbox(
                            "💼 Credor",
                            options=member_options,
                            format_func=lambda x: x[1],
                            index=current_creditor_index,
                            help="Quem emprestou o dinheiro"
                        )
                        creditor_id = selected_creditor[0] if selected_creditor else None
                    else:
                        st.error("❌ Nenhum membro disponível.")
                        benefited_id = creditor_id = None
                except ApiClientError as e:
                    st.error(f"❌ Erro ao carregar membros: {e}")
                    benefited_id = creditor_id = None
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                    update_data = {
                        'description': description,
                        'value': value,
                        'payed_value': loan.get('payed_value', 0),
                        'date': format_date_for_api(loan_date),
                        'horary': loan_time.strftime('%H:%M:%S'),
                        'category': category,
                        'account': account_id,
                        'benefited': benefited_id,
                        'creditor': creditor_id,
                        'payed': loan.get('payed', False),
                        'loan_type': loan.get('loan_type', 'given')
                    }
                    self._update_loan_edit(loan_id, update_data)
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.pop(f'edit_loan_data_{loan_id}', None)
                    st.rerun()

    def _render_give_loan_form(self) -> None:
        """Renderiza formulário para realizar empréstimo (emprestar dinheiro)."""
        st.markdown("### 💸 Realizar Empréstimo (Emprestar Dinheiro)")
        st.info("👤 Você está emprestando dinheiro para alguém. O dinheiro sairá da sua conta.")
        
        with st.form("create_give_loan_form"):
            loan_data = self._render_loan_form_fields("given")
            self._process_loan_form_submit("given", loan_data)

    def _render_receive_loan_form(self) -> None:
        """Renderiza formulário para tomar empréstimo (receber dinheiro)."""
        st.markdown("### 💰 Tomar Empréstimo (Receber Dinheiro)")
        st.info("🏦 Você está tomando dinheiro emprestado. O dinheiro entrará na sua conta.")
        
        with st.form("create_receive_loan_form"):
            loan_data = self._render_loan_form_fields("received")
            self._process_loan_form_submit("received", loan_data)

    def _render_loan_form_fields(self, loan_type: str) -> Dict[str, Any]:
        """Renderiza os campos do formulário de empréstimo."""
        is_giving = loan_type == "given"
        
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input(
                "📝 Descrição",
                placeholder="Ex: Empréstimo para João...",
                key=f"loan_desc_{loan_type}"
            )
            
            value = st.number_input(
                "💰 Valor do Empréstimo",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                help="Valor total do empréstimo",
                key=f"loan_value_{loan_type}"
            )
            
            category_display = st.selectbox(
                "📂 Categoria",
                options=list(db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys()),
                key=f"loan_category_{loan_type}"
            )
            category = db_categories.TRANSLATED_EXPENSE_CATEGORIES[category_display]
        
        with col2:
            loan_date = st.date_input(
                "📅 Data do Empréstimo",
                value=datetime.now().date(),
                format="DD/MM/YYYY",
                key=f"loan_date_{loan_type}"
            )
            
            loan_time = st.time_input(
                "🕐 Horário",
                value=datetime.now().time(),
                key=f"loan_time_{loan_type}"
            )
        
        # Seleção de membros
        try:
            members = api_client.get("members/")
            if members:
                member_options = [(m['id'], m['name']) for m in members]
                
                if is_giving:
                    # Para empréstimo dado, selecionar beneficiado
                    selected_benefited = st.selectbox(
                        "👤 Para quem você está emprestando",
                        options=member_options,
                        format_func=lambda x: x[1],
                        key=f"benefited_{loan_type}"
                    )
                    benefited_id = selected_benefited[0]
                    creditor_id = None  # Você é o credor
                else:
                    # Para empréstimo recebido, selecionar credor
                    selected_creditor = st.selectbox(
                        "👤 De quem você está recebendo empréstimo",
                        options=member_options,
                        format_func=lambda x: x[1],
                        key=f"creditor_{loan_type}"
                    )
                    creditor_id = selected_creditor[0]
                    benefited_id = None  # Você é o beneficiado
            else:
                st.error("❌ Nenhum membro cadastrado. Cadastre membros primeiro.")
                creditor_id = benefited_id = None
        except Exception:
            st.error("❌ Erro ao carregar membros.")
            creditor_id = benefited_id = None
            
        # Seleção de conta
        try:
            accounts = accounts_service.get_all_accounts()
            if accounts:
                account_options = [(acc['id'], db_categories.INSTITUTIONS.get(acc['name'], acc['name'])) for acc in accounts if acc.get('is_active', True)]
                selected_account = st.selectbox(
                    "🏦 Conta",
                    options=account_options,
                    format_func=lambda x: x[1],
                    key=f"account_{loan_type}"
                )
                account_id = selected_account[0]
            else:
                st.error("❌ Nenhuma conta ativa disponível.")
                account_id = None
        except Exception:
            st.error("❌ Erro ao carregar contas.")
            account_id = None
            
        # Checkbox de confirmação
        confirm_data = st.checkbox(
            "✅ Confirmo que os dados informados estão corretos",
            key=f"confirm_{loan_type}"
        )
        
        return {
            'description': description,
            'value': value,
            'category': category,
            'loan_date': loan_date,
            'loan_time': loan_time,
            'creditor_id': creditor_id,
            'benefited_id': benefited_id,
            'account_id': account_id,
            'confirm_data': confirm_data,
            'loan_type': loan_type
        }
    
    def _process_loan_form_submit(self, loan_type: str, loan_data: Dict[str, Any]) -> None:
        """Processa o envio do formulário de empréstimo."""
        if st.form_submit_button("💾 Criar Empréstimo", type="primary"):
            errors = []
            
            # Validações básicas
            if not loan_data.get('confirm_data'):
                errors.append("Confirme que os dados estão corretos antes de prosseguir")
            if not loan_data.get('description'):
                errors.append("Descrição é obrigatória")
            if not loan_data.get('value') or loan_data['value'] <= 0:
                errors.append("Valor deve ser maior que zero")
            if not loan_data.get('account_id'):
                errors.append("Conta é obrigatória")
            if not loan_data.get('creditor_id') and not loan_data.get('benefited_id'):
                errors.append("Membro é obrigatório")
                
            if errors:
                st.error("❌ **Erros encontrados:**")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Preparar dados para a API
                api_loan_data = {
                    'description': loan_data['description'],
                    'value': float(loan_data['value']),
                    'payed_value': 0.0,
                    'date': format_date_for_api(loan_data['loan_date']),
                    'horary': loan_data['loan_time'].strftime('%H:%M:%S'),
                    'category': loan_data['category'],
                    'account': loan_data['account_id'],
                    'payed': False,
                    'loan_type': loan_type
                }
                
                # Adicionar credor ou beneficiado dependendo do tipo
                if loan_type == "given":
                    api_loan_data['benefited'] = loan_data['benefited_id']
                    api_loan_data['creditor'] = None  # Sistema assume que você é o credor
                else:
                    api_loan_data['creditor'] = loan_data['creditor_id'] 
                    api_loan_data['benefited'] = None  # Sistema assume que você é o beneficiado
                
                self._create_loan(api_loan_data)

    def _calculate_account_balance(self, account_id: int) -> float:
        """
        Calcula o saldo de uma conta baseado em receitas, despesas e transferências.
        
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
            account_revenues = [r for r in revenues if r.get('account') == account_id]
            balance += sum(float(r.get('value', 0)) for r in account_revenues)
            
            # Subtrair despesas da conta
            expenses = api_client.get("expenses/")
            account_expenses = [e for e in expenses if e.get('account') == account_id]
            balance -= sum(float(e.get('value', 0)) for e in account_expenses)
            
            # Transferências onde a conta é origem (subtrai)
            transfers = api_client.get("transfers/")
            outgoing_transfers = [t for t in transfers if t.get('origin_account') == account_id and t.get('transfered', False)]
            balance -= sum(float(t.get('value', 0)) for t in outgoing_transfers)
            
            # Transferências onde a conta é destino (soma)
            incoming_transfers = [t for t in transfers if t.get('destiny_account') == account_id and t.get('transfered', False)]
            balance += sum(float(t.get('value', 0)) for t in incoming_transfers)
            
            # Empréstimos dados (subtrai da conta) - apenas os efetivados
            loans = api_client.get("loans/")
            given_loans = [l for l in loans if l.get('account') == account_id and l.get('loan_type') == 'given']
            balance -= sum(float(l.get('value', 0)) for l in given_loans)
            
            # Empréstimos recebidos (soma na conta) - apenas os efetivados
            received_loans = [l for l in loans if l.get('account') == account_id and l.get('loan_type') == 'received']
            balance += sum(float(l.get('value', 0)) for l in received_loans)
            
            return balance
            
        except Exception as e:
            logger.error(f"Erro ao calcular saldo da conta {account_id}: {e}")
            return None

    def _render_loans_summary(self) -> None:
        """Renderiza resumo dos empréstimos."""
        st.markdown("### 📊 Resumo de Empréstimos")
        
        try:
            with st.spinner("📊 Carregando estatísticas..."):
                time.sleep(1)
                loans = api_client.get("loans/")
            
            if not loans:
                st.info("📝 Nenhum empréstimo encontrado.")
                return
            
            total_loans = len(loans)
            total_value = sum(float(loan.get('value', 0)) for loan in loans)
            total_paid = sum(float(loan.get('payed_value', 0)) for loan in loans)
            total_pending = total_value - total_paid
            paid_loans = sum(1 for loan in loans if loan.get('payed', False))
            pending_loans = total_loans - paid_loans
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total de Empréstimos", total_loans)
            with col2:
                st.metric("💰 Valor Total", format_currency_br(total_value))
            with col3:
                st.metric("✅ Valor Pago", format_currency_br(total_paid))
            with col4:
                st.metric("⏳ Valor Pendente", format_currency_br(total_pending))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("✅ Empréstimos Quitados", paid_loans)
            with col2:
                st.metric("⏳ Empréstimos Pendentes", pending_loans)
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar estatísticas: {e}")
            logger.error(f"Erro ao carregar resumo de empréstimos: {e}")

    def _create_loan(self, loan_data: Dict[str, Any]) -> None:
        """Cria um novo empréstimo."""
        try:
            with st.spinner("💾 Criando empréstimo..."):
                time.sleep(1)
                new_loan = api_client.post("loans/", loan_data)
            
            st.toast("✅ Empréstimo criado com sucesso!")
            time.sleep(1)
            st.rerun()
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao criar empréstimo: {e}")
            logger.error(f"Erro ao criar empréstimo: {e}")

    def _update_loan(self, loan_id: int, loan_data: Dict[str, Any]) -> None:
        """Atualiza um empréstimo."""
        try:
            with st.spinner("💾 Atualizando empréstimo..."):
                time.sleep(1)
                updated_loan = api_client.put(f"loans/{loan_id}/", loan_data)
            
            st.success("✅ Empréstimo atualizado com sucesso!")
            st.session_state.pop(f'payment_loan_data_{loan_id}', None)
            st.rerun()
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao atualizar empréstimo: {e}")
            logger.error(f"Erro ao atualizar empréstimo {loan_id}: {e}")

    def _update_loan_edit(self, loan_id: int, loan_data: Dict[str, Any]) -> None:
        """Atualiza um empréstimo (edição completa)."""
        try:
            with st.spinner("💾 Salvando alterações..."):
                time.sleep(1)
                updated_loan = api_client.put(f"loans/{loan_id}/", loan_data)
            
            st.success("✅ Empréstimo editado com sucesso!")
            st.session_state.pop(f'edit_loan_data_{loan_id}', None)
            st.rerun()
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao editar empréstimo: {e}")
            logger.error(f"Erro ao editar empréstimo {loan_id}: {e}")

    def _toggle_loan_payment(self, loan_id: int, is_paid: bool) -> None:
        """Alterna o status de pagamento de um empréstimo."""
        try:
            with st.spinner(f"{'Marcando como quitado' if is_paid else 'Marcando como pendente'}..."):
                loan_data = api_client.get(f"loans/{loan_id}/")
                
                update_data = {
                    'description': loan_data.get('description'),
                    'value': loan_data.get('value'),
                    'payed_value': loan_data.get('value') if is_paid else 0,
                    'date': loan_data.get('date'),
                    'horary': loan_data.get('horary'),
                    'category': loan_data.get('category'),
                    'account': loan_data.get('account'),
                    'benefited': loan_data.get('benefited'),
                    'creditor': loan_data.get('creditor'),
                    'payed': is_paid
                }
                
                api_client.put(f"loans/{loan_id}/", update_data)
            
            status_text = "quitado" if is_paid else "pendente"
            st.success(f"✅ Empréstimo marcado como {status_text}!")
            st.rerun()
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao alterar status: {e}")
            logger.error(f"Erro ao alterar status do empréstimo {loan_id}: {e}")

    def _delete_loan(self, loan_id: int, description: str) -> None:
        """Exclui um empréstimo após confirmação."""
        confirm_key = f"confirm_delete_loan_{loan_id}"
        
        if not st.session_state.get(confirm_key, False):
            st.session_state[confirm_key] = True
            st.rerun()
        
        st.warning(f"⚠️ **Tem certeza que deseja excluir o empréstimo '{description}'?**")
        st.error("🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "🗑️ Sim, Excluir",
                key=f"final_confirm_delete_loan_{loan_id}",
                type="primary",
                width='stretch'
            ):
                try:
                    with st.spinner("🗑️ Excluindo empréstimo..."):
                        api_client.delete(f"loans/{loan_id}/")
                    
                    st.success(f"✅ Empréstimo '{description}' excluído com sucesso!")
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
                    
                except ApiClientError as e:
                    st.error(f"❌ Erro ao excluir empréstimo: {e}")
                    logger.error(f"Erro ao excluir empréstimo {loan_id}: {e}")
                    st.session_state.pop(confirm_key, None)
        
        with col2:
            if st.button(
                "❌ Cancelar",
                key=f"cancel_delete_loan_{loan_id}",
                width='stretch'
            ):
                st.session_state.pop(confirm_key, None)
                st.rerun()
    
    def _generate_loan_pdf(self, loan: Dict[str, Any]) -> None:
        """Gera e oferece download do PDF do contrato de empréstimo."""
        if pdf_generator is None:
            st.error("❌ Gerador de PDF não disponível. Instale o ReportLab: pip install reportlab")
            return
        
        try:
            with st.spinner("📄 Gerando contrato..."):
                # Buscar dados dos membros
                creditor_data = None
                benefited_data = None
                
                try:
                    members = api_client.get("members/")
                    creditor_data = next((m for m in members if m['id'] == loan.get('creditor')), None)
                    benefited_data = next((m for m in members if m['id'] == loan.get('benefited')), None)
                except ApiClientError:
                    pass
                
                # Gerar PDF
                pdf_buffer = pdf_generator.generate_loan_contract(loan, creditor_data, benefited_data)
                
                # Nome do arquivo
                description = loan.get('description', 'emprestimo')
                date_str = loan.get('date', '').replace('-', '_')
                filename = f"contrato_emprestimo_{description}_{date_str}.pdf"
                
                # Oferecer download
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_loan_{loan.get('id')}"
                )
                
                # Preview do PDF
                st.success("✅ Contrato gerado com sucesso!")
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
            st.error(f"❌ Erro ao gerar contrato: {e}")
            logger.error(f"Erro ao gerar PDF do empréstimo {loan.get('id')}: {e}")
