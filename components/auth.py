"""
Componentes de autenticação.

Este módulo implementa todos os componentes relacionados à
autenticação de usuários na aplicação.
"""

import logging
from typing import Optional
# , Tuple

import streamlit as st

from services.api_client import (
    api_client,
    AuthenticationError,
    ApiClientError
)
# from config.settings import app_config


logger = logging.getLogger(__name__)


class AuthenticationComponent:
    """
    Componente de autenticação da aplicação.

    Esta classe implementa toda a lógica de interface para
    login, logout e gerenciamento de sessão de usuário.
    """

    def __init__(self):
        """Inicializa o componente de autenticação."""
        self.session_keys = [
            'is_authenticated', 'access_token', 'refresh_token',
            'token_expires_at', 'username', 'user_permissions'
        ]

    def render_login_form(self) -> bool:
        """
        Renderiza o formulário de login.

        Returns
        -------
        bool
            True se o usuário foi autenticado com sucesso
        """
        st.markdown("### Login - ExpenseLit")
        st.markdown("---")

        # Verifica se já está autenticado
        if st.session_state.get('is_authenticated', False):
            self._render_authenticated_user()
            return True

        # Formulário de login
        with st.form("login_form", clear_on_submit=False):
            st.markdown("**Credenciais:**")

            col1, col2 = st.columns([3, 1])

            with col1:
                username = st.text_input(
                    "Usuário:",
                    placeholder="Digite seu nome de usuário",
                    help="Nome de usuário cadastrado no sistema"
                )

                password = st.text_input(
                    "Senha:",
                    type="password",
                    placeholder="Digite sua senha",
                    help="Senha do seu usuário"
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                login_button = st.form_submit_button(
                    "Entrar",
                    width='stretch',
                    type="primary"
                )

        # Processa o login
        if login_button:
            if not username or not password:
                st.error("Por favor, preencha todos os campos.")
                return False

            return self._process_login(username, password)

        # Informações de ajuda
        with st.expander("Precisa de ajuda?"):
            st.markdown("""
            **Como fazer login:**
            1. Digite seu nome de usuário no campo "Usuário"
            2. Digite sua senha no campo "Senha"
            3. Clique em "🚀 Entrar"

            **Problemas de acesso:**
            - Verifique se suas credenciais estão corretas
            - Certifique-se de que a API está rodando
            - Entre em contato com o administrador se necessário
            """)

        return False

    def _render_authenticated_user(self) -> None:
        """Renderiza informações do usuário autenticado."""
        username = st.session_state.get('username', 'Usuário')

        col1, col2 = st.columns([3, 1])

        with col1:
            st.success(f"Logado como: **{username}**")

        with col2:
            if st.button("Sair", type="secondary", width='stretch'):
                self.logout()
                st.rerun()

    def _process_login(self, username: str, password: str) -> bool:
        """
        Processa o login do usuário.

        Parameters
        ----------
        username : str
            Nome de usuário
        password : str
            Senha do usuário

        Returns
        -------
        bool
            True se autenticado com sucesso
        """
        try:
            with st.spinner("🔄 Autenticando..."):
                # Tenta fazer login na API
                auth_data = api_client.authenticate(username, password)
                st.write(auth_data)
                # Busca permissões do usuário
                try:
                    user_permissions = api_client.get_user_permissions()
                    st.session_state['user_permissions'] = user_permissions
                except ApiClientError as e:
                    # Se falhar ao buscar permissões,
                    # assume superusuário para evitar bloqueios.
                    st.session_state['user_permissions'] = {
                        'is_superuser': True,
                        'permissions': []
                    }
                    logger.warning(
                        f"""Falha ao buscar permissões do usuário: {e}.
                        Assumindo acesso total.
                        """
                    )

            st.success(f"🎉 Bem-vindo, {username}!")
            logger.info(f"Usuário {username} logado com sucesso")

            # Força atualização da página
            st.rerun()
            return True

        except AuthenticationError as e:
            st.error(f"❌ **Erro de autenticação:** {e}")
            logger.warning(f"Tentativa de login falhada para {username}: {e}")
            return False
        except ApiClientError as e:
            st.error(f"🔧 **Erro de conexão:** {e}")
            st.info("💡 Verifique se a API está rodando e tente novamente.")
            logger.error(f"Erro de API no login: {e}")
            return False
        except Exception as e:
            st.error(f"💥 **Erro inesperado:** {e}")
            logger.error(f"Erro inesperado no login: {e}")
            return False

    def logout(self) -> None:
        """Realiza logout do usuário."""
        try:
            username = st.session_state.get('username', 'usuário')

            # Remove dados de autenticação
            api_client.logout()

            # Limpa outras chaves de sessão específicas da aplicação
            app_keys = ['current_page', 'selected_account', 'filters']
            for key in app_keys:
                st.session_state.pop(key, None)

            st.success(f"👋 Até logo, {username}!")
            logger.info(f"Usuário {username} deslogado")

        except Exception as e:
            st.error(f"Erro ao fazer logout: {e}")
            logger.error(f"Erro no logout: {e}")

    def is_authenticated(self) -> bool:
        """
        Verifica se o usuário está autenticado.

        Returns
        -------
        bool
            True se autenticado
        """
        return st.session_state.get('is_authenticated', False)

    def get_current_user(self) -> Optional[str]:
        """
        Obtém o nome do usuário atual.

        Returns
        -------
        Optional[str]
            Nome do usuário ou None se não autenticado
        """
        if self.is_authenticated():
            return st.session_state.get('username')
        return None

    def get_user_permissions(self) -> dict:
        """
        Obtém as permissões do usuário atual.

        Returns
        -------
        dict
            Dicionário com permissões do usuário
        """
        return st.session_state.get('user_permissions', {})

    def has_permission(self, permission: str) -> bool:
        """
        Verifica se o usuário tem uma permissão específica.

        Parameters
        ----------
        permission : str
            Nome da permissão (ex: 'expenses.add_expense')

        Returns
        -------
        bool
            True se tem a permissão
        """
        if not self.is_authenticated():
            return False

        permissions = self.get_user_permissions()
        user_permissions = permissions.get('permissions', [])

        # Superuser tem todas as permissões
        if permissions.get('is_superuser', False):
            return True

        return permission in user_permissions

    def require_authentication(self) -> bool:
        """
        Garante que o usuário está autenticado.

        Se não estiver autenticado, tenta carregar do cookie.
        Se falhar, exibe o formulário de login e interrompe a execução da página.

        Returns
        -------
        bool
            True se autenticado
        """
        # Primeiro verifica se já está autenticado na sessão
        if self.is_authenticated():
            return True
            
        # Tenta restaurar sessão se não estiver autenticado
        if api_client.restore_session_if_available():
            return True
            
        # Se falhar, mostra login
        st.warning("🔒 **Acesso restrito.** Faça login para continuar.")
        self.render_login_form()
        st.stop()
        return True

    def render_session_info(self) -> None:
        """Renderiza informações da sessão no sidebar."""
        if self.is_authenticated():
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 Sessão")

                username = self.get_current_user()
                st.markdown(f"**Usuário:** {username}")

                # Botão de logout no sidebar
                if st.button(
                    "Sair",
                    key="sidebar_logout",
                    width='stretch'
                ):
                    self.logout()
                    st.rerun()


def require_auth() -> AuthenticationComponent:
    """
    Decorator/função helper para páginas que requerem autenticação.

    Returns
    -------
    AuthenticationComponent
        Instância do componente de autenticação
    """
    auth = AuthenticationComponent()
    auth.require_authentication()
    return auth


class AuthLogin:
    """
    Classe responsável pelo controle de login seguindo o padrão CodexDB.

    Esta classe gerencia o fluxo completo de autenticação e navegação
    da aplicação ExpenseLit.
    """

    def __init__(self):
        """Inicializa o componente de login."""
        self.auth_component = AuthenticationComponent()

    def get_login(self):
        """
        Interface principal para login e navegação da aplicação.

        Similar ao padrão CodexDB, verifica se existe token na sessão ou cookie
        e direciona para login ou menu principal.
        """
        # Primeiro, tenta restaurar sessão se não estiver autenticado
        if not self.auth_component.is_authenticated():
            if api_client.restore_session_if_available():
                # Sessão restaurada com sucesso
                from home.main import HomePage
                HomePage().main_menu()
                return

        # Limpa token inválido se existir
        if 'is_authenticated' in st.session_state and not (
            st.session_state.is_authenticated
        ):
            self._clear_invalid_session()

        # Verifica se usuário já está autenticado
        if not self.auth_component.is_authenticated():
            self._render_login_interface()
        else:
            # Usuário autenticado - carrega menu principal
            from home.main import HomePage
            HomePage().main_menu()

    def _clear_invalid_session(self):
        """Limpa dados de sessão inválidos."""
        invalid_keys = [
            'is_authenticated', 'access_token', 'refresh_token',
            'username', 'user_permissions', 'current_page'
        ]
        for key in invalid_keys:
            st.session_state.pop(key, None)

    def _render_login_interface(self):
        """Renderiza a interface de login."""
        # Header da aplicação (similar ao CodexDB)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("# 💰 ExpenseLit")
            st.markdown("**Controle Financeiro Pessoal**")

        st.divider()

        # Abas para Login e Cadastro
        tab1, tab2 = st.tabs(["🔐 Login", "👤 Novo Usuário"])
        
        with tab1:
            # Formulário de login centralizado
            col4, col5, col6 = st.columns(3)

            with col5:
                username = st.text_input(
                    "Usuário",
                    placeholder="Digite seu usuário",
                    key="login_username"
                )
                password = st.text_input(
                    "Senha",
                    type="password",
                    placeholder="Digite sua senha",
                    key="login_password"
                )

                if st.button("🔑 Entrar", type="primary", width='stretch'):
                    if username and password:
                        # Processa login usando o componente existente
                        success = self._process_login(username, password)

                        if success:
                            st.toast("✅ Login realizado com sucesso!")
                            st.rerun()
                    else:
                        st.error("Preencha todos os campos.")
        
        with tab2:
            self._render_register_form()

    def _process_login(self, username: str, password: str) -> bool:
        """
        Processa o login do usuário.

        Parameters
        ----------
        username : str
            Nome de usuário
        password : str
            Senha

        Returns
        -------
        bool
            True se login foi bem-sucedido
        """
        try:
            with st.spinner("🔄 Autenticando..."):
                # Usa o componente de autenticação existente
                auth_data = api_client.authenticate(username, password)
                # Busca permissões do usuário
                try:
                    user_permissions = api_client.get_user_permissions()
                    st.session_state['user_permissions'] = user_permissions
                except ApiClientError:
                    # Assume superusuário se não conseguir buscar permissões
                    st.session_state['user_permissions'] = {
                        'is_superuser': True,
                        'permissions': []
                    }

                return True

        except AuthenticationError as e:
            st.error(f"❌ Erro de autenticação: {e}")
            return False
        except ApiClientError as e:
            st.error(f"🔧 Erro de conexão: {e}")
            st.info("💡 Verifique se a API está rodando.")
            return False
        except Exception as e:
            st.error(f"💥 Erro inesperado: {e}")
            return False

    def _render_register_form(self) -> None:
        """Renderiza formulário de cadastro de novo usuário."""
        st.markdown("### 👤 Criar Nova Conta")
        st.info("ℹ️ Usuários criados aqui terão acesso a todas as funcionalidades do sistema.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("register_form"):
                # Dados básicos
                st.markdown("**Dados de Acesso:**")
                
                new_username = st.text_input(
                    "👤 Nome de Usuário",
                    placeholder="Ex: joao_silva",
                    help="Nome único para login no sistema"
                )
                
                new_password = st.text_input(
                    "🔒 Senha",
                    type="password",
                    placeholder="Senha segura",
                    help="Mínimo de 8 caracteres"
                )
                
                confirm_password = st.text_input(
                    "🔒 Confirmar Senha",
                    type="password",
                    placeholder="Digite a senha novamente"
                )
                
                st.markdown("**Dados Pessoais:**")
                
                full_name = st.text_input(
                    "📝 Nome Completo",
                    placeholder="Ex: João Silva Santos"
                )
                
                email = st.text_input(
                    "📧 Email",
                    placeholder="joao@email.com"
                )
                
                phone = st.text_input(
                    "📞 Telefone",
                    placeholder="(11) 99999-9999"
                )
                
                document = st.text_input(
                    "📄 CPF",
                    placeholder="000.000.000-00"
                )
                
                sex = st.selectbox(
                    "🚻 Sexo",
                    options=[('M', 'Masculino'), ('F', 'Feminino')],
                    format_func=lambda x: x[1]
                )
                
                # Botão de cadastro
                col_submit, col_info = st.columns([1, 2])
                
                with col_submit:
                    submitted = st.form_submit_button(
                        "✅ Criar Conta",
                        type="primary"
                    )
                
                with col_info:
                    st.caption("🔐 Usuário criado com permissões padrão")
                
                if submitted:
                    self._process_register(
                        new_username, new_password, confirm_password,
                        full_name, email, phone, document, sex[0]
                    )

    def _process_register(self, username: str, password: str, confirm_password: str,
                         full_name: str, email: str, phone: str, document: str, sex: str) -> bool:
        """
        Processa o cadastro de novo usuário.
        
        Parameters
        ----------
        username : str
            Nome de usuário
        password : str
            Senha do usuário
        confirm_password : str
            Confirmação da senha
        full_name : str
            Nome completo
        email : str
            Email
        phone : str
            Telefone
        document : str
            CPF/documento
        sex : str
            Sexo (M/F)
            
        Returns
        -------
        bool
            True se usuário foi criado com sucesso
        """
        # Validações básicas
        if not all([username, password, full_name, email, phone, document]):
            st.error("❌ Por favor, preencha todos os campos obrigatórios.")
            return False
            
        if password != confirm_password:
            st.error("❌ As senhas não coincidem.")
            return False
            
        if len(password) < 8:
            st.error("❌ A senha deve ter pelo menos 8 caracteres.")
            return False
        
        # Valida CPF (formato básico)
        import re
        doc_clean = re.sub(r'[^0-9]', '', document)
        if len(doc_clean) != 11:
            st.error("❌ CPF deve ter 11 dígitos.")
            return False
        
        try:
            with st.spinner("🔄 Criando usuário..."):
                # Primeiro cria o membro
                member_data = {
                    'name': full_name,
                    'document': document,
                    'phone': phone,
                    'email': email,
                    'sex': sex,
                    'is_user': True,
                    'is_creditor': True,
                    'is_benefited': True,
                    'active': True
                }
                
                # Cria membro via API
                new_member = api_client.post("members/", member_data)
                member_id = new_member.get('id')
                
                # Cria usuário via API (assumindo que existe endpoint para isso)
                user_data = {
                    'username': username,
                    'password': password,
                    'member_id': member_id,
                    'is_superuser': False,  # Usuário padrão, não superusuário
                    'is_active': True
                }
                
                # Tenta criar usuário - se não existir endpoint específico, pode adaptar
                try:
                    new_user = api_client.post("users/", user_data)
                    st.success(f"✅ Usuário '{username}' criado com sucesso!")
                    st.info("🔑 Agora você pode fazer login com suas credenciais.")
                    return True
                    
                except ApiClientError as e:
                    # Se erro ao criar usuário, remove o membro criado
                    try:
                        api_client.delete(f"members/{member_id}/")
                    except:
                        pass
                    raise e
                    
        except ApiClientError as e:
            if "already exists" in str(e).lower() or "unique" in str(e).lower():
                st.error("❌ Nome de usuário já existe. Escolha outro.")
            else:
                st.error(f"❌ Erro ao criar usuário: {e}")
            logger.error(f"Erro ao criar usuário: {e}")
            return False
        except Exception as e:
            st.error(f"💥 Erro inesperado: {e}")
            logger.error(f"Erro inesperado ao criar usuário: {e}")
            return False


# Instância global do componente de autenticação
auth_component = AuthenticationComponent()
