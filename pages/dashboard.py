"""
Página de Dashboard da aplicação ExpenseLit.

Esta página apresenta uma visão geral das finanças do usuário,
incluindo resumos, gráficos e indicadores principais.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from utils.date_utils import format_date_for_display, format_date_for_api, format_currency_br

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pages.router import BasePage
from services.api_client import api_client, ApiClientError, AuthenticationError
from services.accounts_service import accounts_service
from services.expenses_service import expenses_service
from services.revenues_service import revenues_service
from config.settings import db_categories


logger = logging.getLogger(__name__)


class DashboardPage(BasePage):
    """
    Página de Dashboard da aplicação.

    Apresenta uma visão geral das finanças pessoais do usuário,
    incluindo saldos, gastos recentes, receitas e gráficos.
    """

    def __init__(self):
        """Inicializa a página de Dashboard."""
        super().__init__("Dashboard - Visão Geral", "📊")

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
        st.subheader("📊 Dashboard - Visão Geral")
        self.render()

    def render(self) -> None:
        """
        Renderiza o conteúdo da página de Dashboard.

        Apresenta:
        - Cards com métricas principais
        - Gráficos de gastos e receitas
        - Lista de transações recentes
        - Alertas e notificações
        """
        try:
            # Filtros de período
            self._render_period_filters()

            # Carrega dados
            with st.spinner("📊 Carregando dados do dashboard..."):
                dashboard_data = self._load_dashboard_data()

            # Renderiza métricas principais
            self._render_main_metrics(dashboard_data)

            # Duas colunas para gráficos
            col1, col2 = st.columns(2)

            with col1:
                self._render_expenses_chart(dashboard_data)
                self._render_category_chart(dashboard_data)

            with col2:
                self._render_balance_evolution(dashboard_data)
                self._render_accounts_summary(dashboard_data)

            # Transações recentes
            self._render_recent_transactions(dashboard_data)

        except AuthenticationError as e:
            st.error("🔐 **Sessão Expirada**")
            st.warning("Sua sessão expirou. Por favor, faça login novamente para continuar.")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Fazer Login", type="primary", use_container_width=True):
                    # Limpa dados de autenticação
                    for key in ['access_token', 'refresh_token', 'is_authenticated', 'username', 'token_expires_at']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            logger.error(f"Erro de autenticação no dashboard: {e}")
        except ApiClientError as e:
            st.error(f"❌ Erro ao carregar dashboard: {e}")
            logger.error(f"Erro no dashboard: {e}")
        except Exception as e:
            st.error(f"💥 Erro inesperado: {e}")
            logger.error(f"Erro inesperado no dashboard: {e}")

    def _render_period_filters(self) -> None:
        """Renderiza filtros de período."""
        st.markdown("### 📅 Filtros de Período")

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            dateFrom = st.date_input(
                "📅 Data Inicial",
                value=datetime.now().replace(day=1),
                key="dashboard_date_from",
                help="Data inicial para análise",
                format="DD/MM/YYYY"
            )

        with col2:
            dateTo = st.date_input(
                "📅 Data Final",
                value=datetime.now(),
                key="dashboard_date_to",
                help="Data final para análise",
                format="DD/MM/YYYY"
            )

        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Atualizar", width='stretch'):
                st.rerun()

        # Armazena filtros na sessão
        st.session_state['dashboard_filters'] = {
            'date_from': format_date_for_api(dateFrom),
            'date_to': format_date_for_api(dateTo)
        }

        st.markdown("---")

    def _load_dashboard_data(self) -> Dict[str, Any]:
        """
        Carrega todos os dados necessários para o dashboard.

        Returns
        -------
        Dict[str, Any]
            Dados compilados do dashboard
        """
        filters = st.session_state.get('dashboard_filters', {})

        # Carrega dados básicos
        accounts = accounts_service.get_all_accounts(active_only=False)

        # Carrega despesas com filtros
        expenses = expenses_service.get_all_expenses(
            date_from=filters.get('date_from'),
            date_to=filters.get('date_to')
        )

        # Carrega receitas com filtros
        revenues = revenues_service.get_all_revenues(
            date_from=filters.get('date_from'),
            date_to=filters.get('date_to')
        )
        
        # Carrega empréstimos
        loans = []
        try:
            loans_data = api_client.get("loans/")
            if isinstance(loans_data, list):
                loans = loans_data
            elif isinstance(loans_data, dict) and 'results' in loans_data:
                loans = loans_data['results']
        except Exception as e:
            logger.warning(f"Erro ao carregar empréstimos: {e}")
            loans = []

        return {
            'accounts': accounts,
            'expenses': expenses,
            'revenues': revenues,
            'loans': loans,
            'filters': filters
        }

    def _render_main_metrics(self, data: Dict[str, Any]) -> None:
        """
        Renderiza as métricas principais do dashboard.

        Parameters
        ----------
        data : Dict[str, Any]
            Dados do dashboard
        """
        st.markdown("### 📈 Resumo Financeiro")

        # Calcula métricas considerando apenas transações pagas/recebidas
        total_expenses = sum(float(exp.get('value', 0))
                             for exp in data['expenses'] 
                             if exp.get('payed', False))
        
        total_revenues = sum(float(rev.get('value', 0))
                             for rev in data['revenues']
                             if rev.get('received', False))
        
        # Calcula empréstimos dados (saindo da conta) e recebidos (entrando na conta)
        loans_given = sum(float(loan.get('value', 0)) - float(loan.get('payed_value', 0))
                         for loan in data['loans'] 
                         if loan.get('loan_type') == 'given' and not loan.get('payed', False))
        
        loans_received = sum(float(loan.get('value', 0)) - float(loan.get('payed_value', 0))
                           for loan in data['loans']
                           if loan.get('loan_type') == 'received' and not loan.get('payed', False))
        
        # Saldo real considerando empréstimos
        # Empréstimos dados: dinheiro que saiu (negativo no saldo)
        # Empréstimos recebidos: dinheiro que entrou (positivo no saldo)
        balance = total_revenues - total_expenses - loans_given + loans_received
        
        active_accounts = len(
            [acc for acc in data['accounts'] if acc.get('is_active', True)])

        # Renderiza cards - primeira linha
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="💰 Receitas Recebidas",
                value=format_currency_br(total_revenues),
                delta=None,
                help="Total de receitas já recebidas no período"
            )

        with col2:
            st.metric(
                label="💸 Despesas Pagas",
                value=format_currency_br(total_expenses),
                delta=None,
                help="Total de despesas já pagas no período"
            )

        with col3:
            delta_color = "normal" if balance >= 0 else "inverse"
            st.metric(
                label="⚖️ Saldo Real",
                value=format_currency_br(balance),
                delta=f"{'Positivo' if balance >= 0 else 'Negativo'}",
                delta_color=delta_color,
                help="Saldo real considerando receitas, despesas e empréstimos"
            )

        with col4:
            st.metric(
                label="🏦 Contas Ativas",
                value=str(active_accounts),
                help="Número de contas ativas"
            )
        
        # Segunda linha - métricas de empréstimos se houver
        if data['loans']:
            st.markdown("---")
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric(
                    label="💸 Empréstimos Dados",
                    value=format_currency_br(loans_given),
                    delta=None,
                    help="Valor total emprestado a terceiros (pendente)"
                )
            
            with col6:
                st.metric(
                    label="💰 Empréstimos Recebidos", 
                    value=format_currency_br(loans_received),
                    delta=None,
                    help="Valor total recebido de empréstimos (pendente)"
                )
                
            with col7:
                total_loans_impact = loans_received - loans_given
                impact_color = "normal" if total_loans_impact >= 0 else "inverse"
                st.metric(
                    label="🤝 Impacto dos Empréstimos",
                    value=format_currency_br(total_loans_impact),
                    delta=f"{'Positivo' if total_loans_impact >= 0 else 'Negativo'}",
                    delta_color=impact_color,
                    help="Impacto líquido dos empréstimos no saldo"
                )
            
            with col8:
                total_loans = len(data['loans'])
                active_loans = len([l for l in data['loans'] if not l.get('payed', False)])
                st.metric(
                    label="📋 Empréstimos",
                    value=f"{active_loans}/{total_loans}",
                    help="Empréstimos ativos / Total de empréstimos"
                )

        st.markdown("---")

    def _render_expenses_chart(self, data: Dict[str, Any]) -> None:
        """
        Renderiza gráfico de despesas por categoria.

        Parameters
        ----------
        data : Dict[str, Any]
            Dados do dashboard
        """
        st.markdown("#### 💸 Despesas por Categoria")

        if not data['expenses']:
            st.info("📝 Nenhuma despesa encontrada no período selecionado.")
            return

        # Processa dados para o gráfico
        category_totals = {}
        for expense in data['expenses']:
            category = expense.get('category', 'others')
            category_name = db_categories.EXPENSE_CATEGORIES.get(
                category, category)
            value = float(expense.get('value', 0))
            category_totals[category_name] = category_totals.get(
                category_name, 0) + value

        if category_totals:
            # Cria DataFrame
            df = pd.DataFrame(
                list(category_totals.items()),
                columns=['Categoria', 'Valor']
            )

            # Gráfico de pizza
            fig = px.pie(
                df,
                values='Valor',
                names='Categoria',
                title="Distribuição de Despesas"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("📊 Dados insuficientes para gerar gráfico.")

    def _render_balance_evolution(self, data: Dict[str, Any]) -> None:
        """
        Renderiza gráfico de evolução do saldo.

        Parameters
        ----------
        data : Dict[str, Any]
            Dados do dashboard
        """
        st.markdown("#### 📈 Evolução Financeira")

        # Combina receitas, despesas e empréstimos por data
        all_transactions = []

        # Adiciona despesas (apenas pagas)
        for expense in data['expenses']:
            if expense.get('payed', False):
                all_transactions.append({
                    'date': expense.get('date'),
                    'value': -float(expense.get('value', 0)),
                    'type': 'Despesa'
                })

        # Adiciona receitas (apenas recebidas)
        for revenue in data['revenues']:
            if revenue.get('received', False):
                all_transactions.append({
                    'date': revenue.get('date'),
                    'value': float(revenue.get('value', 0)),
                    'type': 'Receita'
                })
        
        # Adiciona empréstimos
        for loan in data['loans']:
            loan_date = loan.get('date')
            loan_value = float(loan.get('value', 0))
            
            if loan.get('loan_type') == 'given':
                # Empréstimo dado: dinheiro saiu da conta (negativo)
                all_transactions.append({
                    'date': loan_date,
                    'value': -loan_value,
                    'type': 'Empréstimo Dado'
                })
            elif loan.get('loan_type') == 'received':
                # Empréstimo recebido: dinheiro entrou na conta (positivo)
                all_transactions.append({
                    'date': loan_date,
                    'value': loan_value,
                    'type': 'Empréstimo Recebido'
                })

        if not all_transactions:
            st.info("📊 Nenhuma transação encontrada no período.")
            return

        # Cria DataFrame e ordena por data
        df = pd.DataFrame(all_transactions)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Calcula saldo acumulado
        df['cumulative_balance'] = df['value'].cumsum()

        # Gráfico de linha
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['cumulative_balance'],
            mode='lines+markers',
            name='Saldo Acumulado',
            line=dict(color='blue', width=2)
        ))

        fig.update_layout(
            title="Evolução do Saldo",
            xaxis_title="Data",
            yaxis_title="Valor (R$)",
            hovermode='x unified'
        )

        st.plotly_chart(fig, width='stretch')

    def _render_category_chart(self, data: Dict[str, Any]) -> None:
        """
        Renderiza gráfico de pizza de receitas por categoria.

        Parameters
        ----------
        data : Dict[str, Any]
            Dados do dashboard
        """
        st.markdown("#### 💰 Receitas por Categoria")

        if not data['revenues']:
            st.info("📝 Nenhuma receita encontrada no período selecionado.")
            return

        # Processa dados para o gráfico
        category_totals = {}
        for revenue in data['revenues']:
            category = revenue.get('category', 'others')
            category_name = db_categories.REVENUE_CATEGORIES.get(
                category, category)
            value = float(revenue.get('value', 0))
            category_totals[category_name] = category_totals.get(
                category_name, 0) + value

        if category_totals:
            # Cria DataFrame
            df = pd.DataFrame(
                list(category_totals.items()),
                columns=['Categoria', 'Valor']
            )

            # Gráfico de pizza
            fig = px.pie(
                df,
                values='Valor',
                names='Categoria',
                title="Distribuição de Receitas"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("📊 Dados insuficientes para gerar gráfico.")

    def _render_accounts_summary(self, data: Dict[str, Any]) -> None:
        """
        Renderiza resumo das contas.

        Parameters
        ----------
        data : Dict[str, Any]
            Dados do dashboard
        """
        st.markdown("#### 🏦 Resumo das Contas")

        if not data['accounts']:
            st.info("📝 Nenhuma conta cadastrada.")
            return

        for account in data['accounts']:
            if account.get('is_active', True):
                account_name_code = account.get('name', 'Conta')
                account_name = db_categories.INSTITUTIONS.get(
                    account_name_code, account_name_code
                )
                account_type = db_categories.ACCOUNT_TYPES.get(
                    account.get('account_type', ''),
                    'Tipo não identificado'
                )

                # Card da conta
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**{account_name}**")
                        st.caption(f"Tipo: {account_type}")

                    with col2:
                        if account.get('is_active', True):
                            st.success("✅ Ativa")
                        else:
                            st.warning("⚠️ Inativa")

                    st.markdown("---")

    def _render_recent_transactions(self, data: Dict[str, Any]) -> None:
        """
        Renderiza lista de transações recentes.

        Parameters
        ----------
        data : Dict[str, Any]
            Dados do dashboard
        """
        st.markdown("### 📋 Transações Recentes")

        # Combina todas as transações
        recent_transactions = []

        # Adiciona despesas
        for expense in data['expenses']:
            recent_transactions.append({
                'date': format_date_for_display(expense.get('date')),
                'time': expense.get('horary', '00:00:00'),
                'description': expense.get('description', 'Despesa'),
                'value': f"-{format_currency_br(expense.get('value', 0))}",
                'type': 'Despesa',
                'category': db_categories.EXPENSE_CATEGORIES.get(
                    expense.get('category', 'others'),
                    expense.get('category', 'Outros')
                ),
                'status': '✅ Pago' if expense.get('payed', False) else '⏳ Pendente'
            })

        # Adiciona receitas
        for revenue in data['revenues']:
            recent_transactions.append({
                'date': format_date_for_display(revenue.get('date')),
                'time': revenue.get('horary', '00:00:00'),
                'description': revenue.get('description', 'Receita'),
                'value': f"+{format_currency_br(revenue.get('value', 0))}",
                'type': 'Receita',
                'category': db_categories.REVENUE_CATEGORIES.get(
                    revenue.get('category', 'others'),
                    revenue.get('category', 'Outros')
                ),
                'status': '✅ Recebido' if revenue.get('received', False) else '⏳ Pendente'
            })

        if not recent_transactions:
            st.info("📝 Nenhuma transação encontrada no período selecionado.")
            return

        # Ordena por data e horário (mais recentes primeiro)
        recent_transactions.sort(
            key=lambda x: (x['date'], x['time']),
            reverse=True
        )

        # Limita a 10 transações mais recentes
        recent_transactions = recent_transactions[:10]

        # Renderiza como DataFrame
        df = pd.DataFrame(recent_transactions)
        df = df[['date', 'description', 'category', 'value', 'status']]
        df.columns = ['Data', 'Descrição', 'Categoria', 'Valor', 'Status']

        st.dataframe(
            df,
            width='stretch',
            hide_index=True
        )

        # Botão para ver todas as transações
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📊 Ver Todas as Transações", width='stretch'):
                st.session_state['current_page'] = 'reports'
                st.rerun()
