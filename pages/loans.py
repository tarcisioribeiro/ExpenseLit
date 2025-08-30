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
        tab1, tab2, tab3 = st.tabs(["📋 Meus Empréstimos", "➕ Novo Empréstimo", "📊 Resumo"])
        
        with tab1:
            self._render_loans_list()
        
        with tab2:
            self._render_loan_form()
        
        with tab3:
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
                loan_id = loan.get('id')
                with st.popover("⚙️ Ações"):
                    edit_clicked = st.button(
                        "✏️ Editar",
                        key=f"edit_loan_{loan_id}",
                        width='stretch'
                    )
                    
                    toggle_text = ("⏳ Marcar Pendente" if loan.get('payed', False) 
                                 else "✅ Marcar Quitado")
                    if st.button(
                        toggle_text,
                        key=f"toggle_loan_{loan_id}",
                        width='stretch'
                    ):
                        self._toggle_loan_payment(loan_id, not loan.get('payed', False))
                    
                    payment_clicked = st.button(
                        "💰 Pagamento",
                        key=f"payment_loan_{loan_id}",
                        width='stretch'
                    )
                    
                    if st.button(
                        "🗑️ Excluir",
                        key=f"delete_loan_{loan_id}",
                        width='stretch'
                    ):
                        self._delete_loan(loan_id, description)
            
            # Processa ações fora do contexto do widget
            if edit_clicked:
                st.session_state[f'edit_loan_{loan_id}'] = loan
                st.rerun()
            
            if payment_clicked:
                st.session_state[f'payment_loan_{loan_id}'] = loan
                st.rerun()
            
            # Formulário de pagamento inline se ativo
            if st.session_state.get(f'payment_loan_{loan_id}'):
                self._render_payment_form(loan)
            
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
                    st.session_state.pop(f'payment_loan_{loan_id}', None)
                    st.rerun()

    def _render_loan_form(self) -> None:
        """Renderiza formulário para criar empréstimo."""
        st.markdown("### ➕ Criar Novo Empréstimo")
        
        with st.form("create_loan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                description = st.text_input(
                    "📝 Descrição",
                    placeholder="Ex: Empréstimo para compra de carro..."
                )
                
                value = st.number_input(
                    "💰 Valor do Empréstimo",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Valor total do empréstimo"
                )
                
                category_display = st.selectbox(
                    "📂 Categoria",
                    options=list(db_categories.TRANSLATED_EXPENSE_CATEGORIES.keys())
                )
                category = db_categories.TRANSLATED_EXPENSE_CATEGORIES[category_display]
                
                # Tipo de empréstimo
                loan_type = st.selectbox(
                    "🤝 Tipo de Empréstimo",
                    options=[
                        ("given", "💸 Empréstimo Dado (Saindo da conta)"),
                        ("received", "💰 Empréstimo Recebido (Entrando na conta)")
                    ],
                    format_func=lambda x: x[1],
                    help="Selecione se você está emprestando ou recebendo dinheiro"
                )
            
            with col2:
                loan_date = st.date_input(
                    "📅 Data do Empréstimo",
                    value=datetime.now().date(),
                    format="DD/MM/YYYY"
                )
                
                loan_time = st.time_input(
                    "🕐 Horário",
                    value=datetime.now().time()
                )
                
                # Seleção de conta
                try:
                    accounts = accounts_service.get_all_accounts()
                    if not accounts:
                        st.error("❌ Nenhuma conta disponível. Cadastre uma conta primeiro.")
                        return
                    
                    account_options = [(acc['id'], db_categories.INSTITUTIONS.get(acc['name'], acc['name'])) for acc in accounts if acc.get('is_active', True)]
                    selected_account = st.selectbox(
                        "🏦 Conta",
                        options=account_options,
                        format_func=lambda x: x[1]
                    )
                    account_id = selected_account[0]
                except ApiClientError:
                    st.error("❌ Erro ao carregar contas")
                    return
                
                # Seleção de membros
                try:
                    members = api_client.get("members/")
                    if not members:
                        st.error("❌ Nenhum membro disponível. Cadastre membros primeiro.")
                        return
                    
                    member_options = [(member['id'], member['name']) for member in members if member.get('active', True)]
                    
                    selected_benefited = st.selectbox(
                        "👤 Beneficiado",
                        options=member_options,
                        format_func=lambda x: x[1],
                        help="Quem recebeu o empréstimo"
                    )
                    benefited_id = selected_benefited[0]
                    
                    selected_creditor = st.selectbox(
                        "💼 Credor",
                        options=member_options,
                        format_func=lambda x: x[1],
                        help="Quem emprestou o dinheiro"
                    )
                    creditor_id = selected_creditor[0]
                except ApiClientError:
                    st.error("❌ Erro ao carregar membros")
                    return
            
            # Validação de saldo para empréstimos dados
            if loan_type[0] == "given" and value and account_id:
                try:
                    account_balance = self._calculate_account_balance(account_id)
                    
                    if account_balance is not None:
                        remaining_balance = account_balance - value
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("💰 Saldo Atual", format_currency_br(account_balance))
                        with col2:
                            st.metric("💸 Empréstimo", format_currency_br(value))
                        with col3:
                            if remaining_balance >= 0:
                                st.metric("✅ Saldo Após", format_currency_br(remaining_balance), delta=f"-{format_currency_br(value)}")
                            else:
                                st.metric("❌ Saldo Após", format_currency_br(remaining_balance), delta=f"-{format_currency_br(value)}")
                                st.error(f"⚠️ **Saldo insuficiente!** Faltam {format_currency_br(abs(remaining_balance))}")
                    else:
                        st.warning("⚠️ Não foi possível verificar o saldo da conta")
                        
                except Exception as e:
                    st.warning("⚠️ Erro ao verificar saldo da conta")
                    logger.warning(f"Erro ao verificar saldo: {e}")
            
            if st.form_submit_button("💾 Criar Empréstimo", type="primary"):
                # Validações mais robustas
                errors = []
                
                if not description:
                    errors.append("Descrição é obrigatória")
                
                if not value or value <= 0:
                    errors.append("Valor deve ser maior que zero")
                
                if not account_id:
                    errors.append("Selecione uma conta")
                
                if not benefited_id or not creditor_id:
                    errors.append("Selecione beneficiado e credor")
                
                # Validação de saldo para empréstimos dados
                if loan_type[0] == "given" and value and account_id:
                    try:
                        balance = self._calculate_account_balance(account_id)
                        if balance is not None and balance < value:
                            errors.append(f"Saldo insuficiente na conta. Saldo: {format_currency_br(balance)}")
                    except Exception:
                        errors.append("Não foi possível verificar o saldo da conta")
                
                if errors:
                    st.error("❌ **Erros encontrados:**")
                    for error in errors:
                        st.error(f"• {error}")
                else:
                    loan_data = {
                        'description': description,
                        'value': value,
                        'payed_value': 0.0,  # Sempre começa com 0
                        'date': format_date_for_api(loan_date),
                        'horary': loan_time.strftime('%H:%M:%S'),
                        'category': category,
                        'account': account_id,
                        'benefited': benefited_id,
                        'creditor': creditor_id,
                        'payed': False,  # Sempre começa como não pago
                        'loan_type': loan_type[0]  # Adiciona o tipo
                    }
                    self._create_loan(loan_data)

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
            st.session_state.pop(f'payment_loan_{loan_id}', None)
            st.rerun()
            
        except ApiClientError as e:
            st.error(f"❌ Erro ao atualizar empréstimo: {e}")
            logger.error(f"Erro ao atualizar empréstimo {loan_id}: {e}")

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
