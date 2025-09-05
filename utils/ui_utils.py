"""
Utilitários de interface do usuário.

Este módulo padroniza mensagens, estilos e componentes visuais
seguindo melhores práticas de UX/UI para o ExpenseLit.
"""

import streamlit as st
import time
from datetime import datetime
from typing import Any, Dict, Optional, List, Callable
from config.settings import db_categories


class MessageStandards:
    """Classe para padronizar mensagens do sistema."""

    # Mensagens de sucesso padronizadas
    SUCCESS_MESSAGES = {
        'created': '✅ {item} criado(a) com sucesso!',
        'updated': '✅ {item} atualizado(a) com sucesso!',
        'deleted': '✅ {item} excluído(a) com sucesso!',
        'activated': '✅ {item} ativado(a) com sucesso!',
        'deactivated': '✅ {item} desativado(a) com sucesso!',
        'saved': '✅ {item} salvo(a) com sucesso!',
        'login': '✅ Login realizado com sucesso!',
        'logout': '👋 Logout realizado com sucesso!',
    }

    # Mensagens de erro padronizadas
    ERROR_MESSAGES = {
        'not_found': '{item} não encontrado(a).',
        'invalid_data': 'Dados inválidos: {details}',
        'required_fields': 'Por favor, preencha todos os campos obrigatórios.',
        'duplicate': '{item} já existe no sistema.',
        'api_error': 'Erro ao {action}: {details}',
        'permission_denied': 'Você não tem permissão para {action}.',
        'connection_error': '🔧 Erro de conexão: {details}',
        'unexpected_error': '💥 Erro inesperado: {details}',
        'invalid_format': 'Formato inválido para {field}.',
        'password_mismatch': 'As senhas não coincidem.',
        'weak_password': 'A senha deve ter pelo menos 8 caracteres.',
    }

    # Mensagens informativas padronizadas
    INFO_MESSAGES = {
        'loading': '🔄 Carregando {item}...',
        'empty_list': '📝 Nenhum(a) {item} cadastrado(a) ainda.',
        'confirm_action': '⚠️ **Tem certeza que deseja {action}?**',
        'irreversible_action': '''
        🚨 **ATENÇÃO:** Esta ação não pode ser desfeita!
        ''',
        'help_contact': '💡 Entre em contato com o administrador do sistema.',
        'api_check': '💡 Verifique se a API está rodando.',
        'security_info': '🔒 **Segurança:** {details}',
    }

    @staticmethod
    def success(message_type: str, **kwargs) -> str:
        """
        Retorna mensagem de sucesso padronizada.

        Parameters
        ----------
        message_type : str
            Tipo da mensagem
        **kwargs
            Variáveis para interpolação na mensagem

        Returns
        -------
        str
            Mensagem formatada
        """
        template = MessageStandards.SUCCESS_MESSAGES.get(
            message_type, '✅ {item}'
        )
        return template.format(**kwargs)

    @staticmethod
    def error(message_type: str, **kwargs) -> str:
        """
        Retorna mensagem de erro padronizada.

        Parameters
        ----------
        message_type : str
            Tipo da mensagem
        **kwargs
            Variáveis para interpolação na mensagem

        Returns
        -------
        str
            Mensagem formatada
        """
        template = MessageStandards.ERROR_MESSAGES.get(
            message_type, '{item}'
        )
        return template.format(**kwargs)

    @staticmethod
    def info(message_type: str, **kwargs) -> str:
        """
        Retorna mensagem informativa padronizada.

        Parameters
        ----------
        message_type : str
            Tipo da mensagem
        **kwargs
            Variáveis para interpolação na mensagem

        Returns
        -------
        str
            Mensagem formatada
        """
        template = MessageStandards.INFO_MESSAGES.get(
            message_type, 'ℹ️ {item}'
        )
        return template.format(**kwargs)


class UIComponents:
    """Componentes de interface padronizados."""

    @staticmethod
    def render_page_header(title: str, icon: str = "", subtitle: str = ""):
        """
        Renderiza cabeçalho padronizado de página.

        Parameters
        ----------
        title : str
            Título da página
        icon : str, optional
            Ícone da página
        subtitle : str, optional
            Subtítulo da página
        """
        header = f"{icon} {title}" if icon else title
        st.subheader(header)
        if subtitle:
            st.caption(subtitle)
        st.markdown("---")

    @staticmethod
    def render_category_with_emoji(
        category: str, category_type: str = "expense"
    ) -> str:
        """
        Renderiza categoria com emoji correspondente.

        Parameters
        ----------
        category : str
            Categoria a ser formatada
        category_type : str, optional
            Tipo da categoria ('expense' ou 'revenue'), by default "expense"

        Returns
        -------
        str
            Categoria formatada com emoji
        """
        if category_type == "expense":
            emoji = db_categories.EXPENSE_CATEGORY_EMOJIS.get(
                category, "💸"
            )
            display_name = db_categories.EXPENSE_CATEGORIES.get(
                category, category
            )
        else:
            emoji = db_categories.REVENUE_CATEGORY_EMOJIS.get(
                category, "💰"
            )
            display_name = db_categories.REVENUE_CATEGORIES.get(
                category, category
            )

        return f"{emoji} {display_name}"

    @staticmethod
    def render_account_with_emoji(
        account_type: str, institution: str = ""
    ) -> str:
        """
        Renderiza tipo de conta com emoji correspondente.

        Parameters
        ----------
        account_type : str
            Tipo da conta
        institution : str, optional
            Instituição da conta

        Returns
        -------
        str
            Tipo de conta formatado com emoji
        """
        account_emojis = {
            "CC": "🏦",
            "CS": "💼",
            "FG": "🛡️",
            "VA": "🍽️"
        }

        emoji = account_emojis.get(account_type, "🏦")
        display_name = db_categories.ACCOUNT_TYPES.get(
            account_type,
            account_type
        )

        if institution:
            institution_name = db_categories.INSTITUTIONS.get(
                institution,
                institution
            )
            return f"{emoji} {display_name} - {institution_name}"

        return f"{emoji} {display_name}"

    @staticmethod
    def render_timer_display(
        start_time: datetime,
        label: str = "⏱️ Tempo decorrido"
    ) -> None:
        """
        Renderiza um display de timer mostrando tempo decorrido.

        Parameters
        ----------
        start_time : datetime
            Horário de início
        label : str, optional
            Label do timer
        """
        elapsed = datetime.now() - start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        st.metric(label, timer_text)

    @staticmethod
    def render_countdown_timer(
        target_time: datetime, label: str = "⏰ Tempo restante"
    ) -> bool:
        """
        Renderiza um countdown timer.

        Parameters
        ----------
        target_time : datetime
            Horário alvo para o countdown
        label : str, optional
            Label do timer

        Returns
        -------
        bool
            True se o tempo expirou, False caso contrário
        """
        remaining = target_time - datetime.now()

        if remaining.total_seconds() <= 0:
            st.error(f"{label}: ⚠️ TEMPO EXPIRADO!")
            return True

        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Cores baseadas no tempo restante
        if remaining.total_seconds() < 300:  # Menos de 5 minutos - vermelho
            st.error(f"{label}: 🔴 {timer_text}")
        elif remaining.total_seconds() < 900:  # Menos de 15 minutos - amarelo
            st.warning(f"{label}: 🟡 {timer_text}")
        else:  # Mais de 15 minutos - verde
            st.success(f"{label}: 🟢 {timer_text}")

        return False

    @staticmethod
    def render_session_timer() -> None:
        """
        Renderiza timer da sessão atual.
        """
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()

        UIComponents.render_timer_display(
            st.session_state.session_start_time,
            "🕐 Sessão ativa"
        )

    @staticmethod
    def render_loading_progress(
        current: int, total: int, message: str = "Processando"
    ) -> None:
        """
        Renderiza barra de progresso com timer.

        Parameters
        ----------
        current : int
            Item atual sendo processado
        total : int
            Total de itens
        message : str, optional
            Mensagem do progresso
        """
        progress = current / total if total > 0 else 0

        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(progress)
            st.caption(f"{message}... ({current}/{total})")

        with col2:
            if 'progress_start_time' not in st.session_state:
                st.session_state.progress_start_time = datetime.now()

            elapsed = datetime.now() - st.session_state.progress_start_time
            if current > 0:
                estimated_total = elapsed * total / current
                remaining = estimated_total - elapsed

                if remaining.total_seconds() > 0:
                    mins, secs = divmod(int(remaining.total_seconds()), 60)
                    st.caption(f"⏱️ ~{mins}m {secs}s")

    @staticmethod
    def render_enhanced_metric_card(
        title: str,
        value: str,
        delta: Optional[str] = None,
        icon: str = "📊",
        color: str = "blue"
    ) -> None:
        """
        Renderiza card de métrica com visual aprimorado.

        Parameters
        ----------
        title : str
            Título da métrica
        value : str
            Valor da métrica
        delta : str, optional
            Variação da métrica
        icon : str, optional
            Ícone da métrica
        color : str, optional
            Cor do card (blue, green, red, orange)
        """
        # Cores baseadas no tema definido em hex.md
        color_map = {
            "blue": "#8be9fd",
            "green": "#50fa7b",
            "red": "#ff5555",
            "orange": "#ffb86c",
            "purple": "#bd93f9",
            "pink": "#ff79c6",
            "yellow": "#f1fa8c"
        }

        accent_color = color_map.get(color, "#8be9fd")

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #282a36, #44475a);
            border-left: 4px solid {accent_color};
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        ">
            <div style="color: {accent_color}; font-size: 14px; "
                       "font-weight: bold;">
                {icon} {title}
            </div>
            <div style="color: #f8f8f2; font-size: 24px; font-weight: bold; "
                       "margin: 5px 0;">
                {value}
            </div>
            {(
                f'<div style="color: #6272a4; font-size: 12px;">{delta}</div>'
                if delta else ''
            )}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_success_toast(message: str, delay: float = 2.0) -> None:
        """
        Mostra toast de sucesso com delay.

        Parameters
        ----------
        message : str
            Mensagem do toast
        delay : float, optional
            Delay em segundos antes de mostrar o toast
        """
        time.sleep(delay)
        st.toast(message, icon="✅")

    @staticmethod
    def show_error_toast(message: str, delay: float = 1.0) -> None:
        """
        Mostra toast de erro com delay.

        Parameters
        ----------
        message : str
            Mensagem do toast
        delay : float, optional
            Delay em segundos antes de mostrar o toast
        """
        time.sleep(delay)
        st.toast(message, icon="❌")

    @staticmethod
    def show_info_toast(message: str, delay: float = 1.0) -> None:
        """
        Mostra toast informativo com delay.

        Parameters
        ----------
        message : str
            Mensagem do toast
        delay : float, optional
            Delay em segundos antes de mostrar o toast
        """
        time.sleep(delay)
        st.toast(message, icon="ℹ️")

    @staticmethod
    def show_confirmation_dialog(
        title: str,
        message: str,
        confirm_callback: Optional[Callable[..., Any]] = None,
        confirm_text: str = "Confirmar",
        cancel_text: str = "Cancelar",
        dialog_key: str = "confirm_dialog"
    ):
        """
        Exibe diálogo de confirmação usando st.dialog.

        Parameters
        ----------
        title : str
            Título do diálogo
        message : str
            Mensagem de confirmação
        confirm_callback : Callable, optional
            Função a ser executada na confirmação
        confirm_text : str, optional
            Texto do botão de confirmação
        cancel_text : str, optional
            Texto do botão de cancelamento
        dialog_key : str, optional
            Chave única para o diálogo

        Returns
        -------
        bool
            True se confirmado, False se cancelado
        """
        if f"show_{dialog_key}" not in st.session_state:
            st.session_state[f"show_{dialog_key}"] = False

        @st.dialog(title)
        def confirmation_dialog():
            st.markdown(f"### ⚠️ {title}")
            st.write(message)
            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    f"✅ {confirm_text}",
                    type="primary",
                    use_container_width=True,
                    key=f"{dialog_key}_confirm"
                ):
                    st.session_state[f"show_{dialog_key}"] = False
                    st.session_state[f"{dialog_key}_result"] = True
                    if confirm_callback is not None:
                        confirm_callback()
                    st.rerun()

            with col2:
                if st.button(
                    f"❌ {cancel_text}",
                    use_container_width=True,
                    key=f"{dialog_key}_cancel"
                ):
                    st.session_state[f"show_{dialog_key}"] = False
                    st.session_state[f"{dialog_key}_result"] = False
                    st.rerun()

        if st.session_state.get(f"show_{dialog_key}", False):
            confirmation_dialog()

        return st.session_state.get(f"{dialog_key}_result", False)

    @staticmethod
    def show_error_dialog(
        title: str,
        error_message: str,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        dialog_key: str = "error_dialog"
    ):
        """
        Exibe diálogo de erro detalhado usando st.dialog.

        Parameters
        ----------
        title : str
            Título do erro
        error_message : str
            Mensagem principal do erro
        details : str, optional
            Detalhes técnicos do erro
        suggestions : List[str], optional
            Lista de sugestões para resolver o erro
        dialog_key : str, optional
            Chave única para o diálogo
        """
        if f"show_{dialog_key}" not in st.session_state:
            st.session_state[f"show_{dialog_key}"] = False

        @st.dialog(f"🚨 {title}")
        def error_dialog():
            # Mensagem principal do erro
            st.error(f"**{error_message}**")

            if details:
                st.markdown("### 🔍 Detalhes Técnicos")
                st.code(details, language="text")

            if suggestions:
                st.markdown("### 💡 Possíveis Soluções")
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"**{i}.** {suggestion}")

            st.markdown("---")

            # Informações adicionais de ajuda
            with st.expander("🆘 Precisa de mais ajuda?"):
                st.info(
                    "💡 Entre em contato com o administrador do sistema se "
                    "o problema persistir."
                )
                st.info("🔧 Verifique se a API está rodando corretamente.")

            # Botão para fechar
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "✅ Entendido",
                    type="primary",
                    use_container_width=True,
                    key=f"{dialog_key}_close"
                ):
                    st.session_state[f"show_{dialog_key}"] = False
                    st.rerun()

        if st.session_state.get(f"show_{dialog_key}", False):
            error_dialog()

    @staticmethod
    def show_persistent_error(
        error_message: str,
        error_type: str = "erro_generico",
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        auto_show: bool = True
    ):
        """
        Exibe erro em diálogo persistente que permanece até ser confirmado
        pelo usuário.

        Parameters
        ----------
        error_message : str
            Mensagem principal do erro
        error_type : str, optional
            Tipo do erro para gerar chave única
        details : str, optional
            Detalhes técnicos do erro
        suggestions : List[str], optional
            Lista de sugestões para resolver o erro
        auto_show : bool, optional
            Se deve mostrar automaticamente o diálogo
        """
        error_key = f"persistent_error_{error_type}"

        # Armazena informações do erro na sessão
        st.session_state[f"{error_key}_message"] = error_message
        st.session_state[f"{error_key}_details"] = details
        st.session_state[f"{error_key}_suggestions"] = suggestions or []

        if auto_show:
            st.session_state[f"show_{error_key}"] = True

        # Exibe o diálogo se solicitado
        UIComponents.show_error_dialog(
            title="Erro no Sistema",
            error_message=error_message,
            details=details,
            suggestions=suggestions,
            dialog_key=error_key
        )

    @staticmethod
    def render_enhanced_form_container(title: str, icon: str = "📝") -> None:
        """
        Renderiza container aprimorado para formulários.

        Parameters
        ----------
        title : str
            Título do formulário
        icon : str, optional
            Ícone do formulário
        """
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #282a36, #44475a);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid #bd93f9;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        ">
            <h3 style="color: #bd93f9; margin: 0 0 20px 0; font-size: 1.5em;">
                {icon} {title}
            </h3>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_form_section(title: str, icon: str = "📋") -> None:
        """
        Renderiza seção de formulário com visual aprimorado.

        Parameters
        ----------
        title : str
            Título da seção
        icon : str, optional
            Ícone da seção
        """
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #6272a4, #44475a);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            border-left: 3px solid #8be9fd;
        ">
            <h4 style="color: #8be9fd; margin: 0; font-size: 1.1em;">
                {icon} {title}
            </h4>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def get_category_for_api(
        display_category: str, category_type: str = "expense"
    ) -> str:
        """
        Converte categoria exibida (com emoji) para formato da API.

        Parameters
        ----------
        display_category : str
            Categoria como exibida na interface (com emoji)
        category_type : str, optional
            Tipo da categoria ('expense' ou 'revenue')

        Returns
        -------
        str
            Categoria no formato da API (inglês)
        """
        # Remove emoji e espaços extras
        clean_display = (
            display_category.split(' ', 1)[-1]
            if ' ' in display_category else display_category
        )

        if category_type == "expense":
            for api_key, display_name in (
                db_categories.EXPENSE_CATEGORIES.items()
            ):
                if display_name == clean_display:
                    return api_key
            # Se não encontrar, retorna a própria categoria
            # (pode já estar no formato da API)
            return clean_display
        else:
            for api_key, display_name in (
                db_categories.REVENUE_CATEGORIES.items()
            ):
                if display_name == clean_display:
                    return api_key
            return clean_display

    @staticmethod
    def format_currency_br(value: float) -> str:
        """
        Formata valor monetário para padrão brasileiro.

        Parameters
        ----------
        value : float
            Valor a ser formatado

        Returns
        -------
        str
            Valor formatado em padrão brasileiro (R$ 1.234,56)
        """
        formatted = f"R$ {value:,.2f}"
        return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

    @staticmethod
    def render_loading_spinner(message: str = "Carregando..."):
        """
        Renderiza spinner de carregamento padronizado.

        Parameters
        ----------
        message : str, optional
            Mensagem do spinner
        """
        return st.spinner(f"🔄 {message}")

    @staticmethod
    def render_confirmation_dialog(
        title: str,
        message: str,
        confirm_text: str = "Sim, Confirmar",
        cancel_text: str = "Cancelar",
        key_prefix: str = ""
    ):
        """
        Renderiza diálogo de confirmação padronizado.

        Parameters
        ----------
        title : str
            Título do diálogo
        message : str
            Mensagem do diálogo
        confirm_text : str, optional
            Texto do botão de confirmação
        cancel_text : str, optional
            Texto do botão de cancelamento
        key_prefix : str, optional
            Prefixo para as chaves dos botões

        Returns
        -------
        tuple[bool, bool]
            (confirmed, cancelled)
        """
        st.warning(f"⚠️ **{title}**")
        st.error(message)

        col1, col2 = st.columns(2)

        with col1:
            confirmed = st.button(
                f"✅ {confirm_text}",
                key=f"{key_prefix}_confirm",
                type="primary",
                width='stretch'
            )

        with col2:
            cancelled = st.button(
                f"{cancel_text}",
                key=f"{key_prefix}_cancel",
                width='stretch'
            )

        return confirmed, cancelled

    @staticmethod
    def render_metrics_row(metrics: Dict[str, Any], columns: int = 4):
        """
        Renderiza linha de métricas padronizada.

        Parameters
        ----------
        metrics : Dict[str, Any]
            Dicionário com as métricas (label: value)
        columns : int, optional
            Número de colunas, by default 4
        """
        cols = st.columns(columns)

        for i, (label, value) in enumerate(metrics.items()):
            with cols[i % columns]:
                st.metric(label, value)

    @staticmethod
    def render_filter_section(
        filters: Dict[
            str,
            Dict[
                str,
                Any
            ]
        ]
    ) -> Dict[str, Any]:
        """
        Renderiza seção de filtros padronizada.

        Parameters
        ----------
        filters : Dict[str, Dict[str, Any]]
            Configuração dos filtros

        Returns
        -------
        Dict[str, Any]
            Valores selecionados nos filtros
        """
        st.markdown("#### 🔍 Filtros")

        # Determina número de colunas baseado na quantidade de filtros
        num_filters = len(filters)
        cols = st.columns(min(num_filters, 4))

        filter_values = {}

        for i, (filter_key, filter_config) in enumerate(filters.items()):
            with cols[i % len(cols)]:
                filter_type = filter_config.get('type', 'selectbox')
                label = filter_config.get('label', filter_key)
                options = filter_config.get('options', [])
            default = filter_config.get(
                'default', options[0] if options else None
            )

            if filter_type == 'selectbox':
                filter_values[filter_key] = st.selectbox(
                    label,
                    options=options,
                    index=options.index(default) if default in options else 0
                )
            elif filter_type == 'multiselect':
                filter_values[filter_key] = st.multiselect(
                    label,
                    options=options,
                    default=default
                )
            elif filter_type == 'checkbox':
                filter_values[filter_key] = st.checkbox(
                    label,
                    value=filter_config.get('default', False)
                )

        return filter_values

    @staticmethod
    def render_action_buttons(
        actions: Dict[str, Dict[str, Any]],
        key_prefix: str = ""
    ) -> Dict[str, bool]:
        """
        Renderiza botões de ação padronizados.

        Parameters
        ----------
        actions : Dict[str, Dict[str, Any]]
            Configuração dos botões de ação
        key_prefix : str, optional
            Prefixo para as chaves dos botões

        Returns
        -------
        Dict[str, bool]
            Estado dos botões (clicado ou não)
        """
        button_states = {}

        for action_key, action_config in actions.items():
            icon = action_config.get('icon', '')
            label = action_config.get('label', action_key)
            button_type = action_config.get('type', 'secondary')
            disabled = action_config.get('disabled', False)
            help_text = action_config.get('help', '')

            button_label = f"{icon} {label}" if icon else label

            button_states[action_key] = st.button(
                button_label,
                key=f"{key_prefix}_{action_key}",
                type=button_type,
                disabled=disabled,
                help=help_text,
                width='stretch'
            )

        return button_states

    @staticmethod
    def render_crud_actions_menu(
        item_id: str,
        item_name: str,
        permissions: Dict[str, bool],
        key_prefix: str = "",
        edit_callback: Optional[Callable[..., Any]] = None,
        delete_callback: Optional[Callable[..., Any]] = None,
        view_callback: Optional[Callable[..., Any]] = None,
        duplicate_callback: Optional[Callable[..., Any]] = None
    ) -> Dict[str, bool]:
        """
        Renderiza menu de ações CRUD para itens de listagem.

        Parameters
        ----------
        item_id : str
            ID do item
        item_name : str
            Nome/descrição do item
        permissions : Dict[str, bool]
            Permissões do usuário (create, read, update, delete)
        key_prefix : str, optional
            Prefixo para as chaves dos botões
        edit_callback : Callable, optional
            Função para editar o item
        delete_callback : Callable, optional
            Função para excluir o item
        view_callback : Callable, optional
            Função para visualizar o item
        duplicate_callback : Callable, optional
            Função para duplicar o item

        Returns
        -------
        Dict[str, bool]
            Estado das ações executadas
        """
        actions_performed = {}

        # Botão de menu principal
        if st.button(
            "⚙️",
            key=f"{key_prefix}_menu_{item_id}",
            help="Opções de edição"
        ):
            st.session_state[f"show_menu_{key_prefix}_{item_id}"] = True

        # Menu de opções
        if st.session_state.get(f"show_menu_{key_prefix}_{item_id}", False):

            with st.container():
                st.markdown(f"**Opções para:** {item_name}")

                # Ações baseadas em permissões
                action_cols = st.columns(4)

                with action_cols[0]:
                    if permissions.get('read', True):
                        if st.button(
                            "👁️ Ver",
                            key=f"{key_prefix}_view_{item_id}",
                            use_container_width=True
                        ):
                            if view_callback is not None:
                                view_callback(item_id)
                            actions_performed['view'] = True
                            menu_key = f"show_menu_{key_prefix}_{item_id}"
                            st.session_state[menu_key] = False

                with action_cols[1]:
                    if permissions.get('update', False):
                        if st.button(
                            "✏️ Editar",
                            key=f"{key_prefix}_edit_{item_id}",
                            use_container_width=True
                        ):
                            if edit_callback is not None:
                                edit_callback(item_id)
                            actions_performed['edit'] = True
                            menu_key = f"show_menu_{key_prefix}_{item_id}"
                            st.session_state[menu_key] = False

                with action_cols[2]:
                    if permissions.get('create', False):
                        if st.button(
                            "📋 Duplicar",
                            key=f"{key_prefix}_duplicate_{item_id}",
                            use_container_width=True
                        ):
                            if duplicate_callback is not None:
                                duplicate_callback(item_id)
                            actions_performed['duplicate'] = True
                            menu_key = f"show_menu_{key_prefix}_{item_id}"
                            st.session_state[menu_key] = False

                with action_cols[3]:
                    if permissions.get('delete', False):
                        if st.button(
                            "🗑️ Excluir",
                            key=f"{key_prefix}_delete_{item_id}",
                            type="primary",
                            use_container_width=True
                        ):
                            # Confirma antes de excluir
                            confirm_key = (
                                f"confirm_delete_{key_prefix}_{item_id}"
                            )
                            st.session_state[confirm_key] = True
                            menu_key = f"show_menu_{key_prefix}_{item_id}"
                            st.session_state[menu_key] = False

                # Botão fechar menu
                if st.button(
                    "❌ Fechar",
                    key=f"{key_prefix}_close_menu_{item_id}",
                    use_container_width=True
                ):
                    menu_key = f"show_menu_{key_prefix}_{item_id}"
                    st.session_state[menu_key] = False
                    st.rerun()

        # Diálogo de confirmação para exclusão
        confirm_key = f"confirm_delete_{key_prefix}_{item_id}"
        if st.session_state.get(confirm_key, False):
            dialog_key = f"delete_{key_prefix}_{item_id}"
            message = (
                f"Tem certeza que deseja excluir **{item_name}**? "
                "Esta ação não pode ser desfeita."
            )
            if UIComponents.show_confirmation_dialog(
                title="Confirmar Exclusão",
                message=message,
                confirm_text="Sim, Excluir",
                cancel_text="Cancelar",
                dialog_key=dialog_key
            ):
                if delete_callback is not None:
                    delete_callback(item_id)
                actions_performed['delete'] = True
                st.session_state[confirm_key] = False

        return actions_performed


class ValidationMessages:
    """Mensagens de validação padronizadas."""

    @staticmethod
    def validate_required_fields(
        data: Dict[
            str,
            Any
        ],
        required_fields: list
    ) -> Optional[str]:
        """
        Valida campos obrigatórios.

        Parameters
        ----------
        data : Dict[str, Any]
            Dados para validação
        required_fields : list
            Lista de campos obrigatórios

        Returns
        -------
        Optional[str]
            Mensagem de erro se houver campos vazios, None caso contrário
        """
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)

        if missing_fields:
            fields_str = ", ".join(missing_fields)
            return MessageStandards.error(
                'invalid_data',
                details=f"Campos obrigatórios: {fields_str}"
            )
        return None

    @staticmethod
    def validate_document(document: str) -> Optional[str]:
        """
        Valida formato de documento (CPF/CNPJ).

        Parameters
        ----------
        document : str
            Documento para validação

        Returns
        -------
        Optional[str]
            Mensagem de erro se inválido, None caso contrário
        """
        import re

        if not document:
            return MessageStandards.error('invalid_format', field="documento")

        # Remove caracteres não numéricos
        doc_clean = re.sub(r'[^0-9]', '', document)

        # Verifica se é CPF (11 dígitos) ou CNPJ (14 dígitos)
        if len(doc_clean) not in [11, 14]:
            return MessageStandards.error(
                'invalid_format',
                field="""
                documento (deve ser CPF com 11 dígitos ou CNPJ com 14 dígitos)
                """
            )

        return None

    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        """
        Valida formato de email.

        Parameters
        ----------
        email : str
            Email para validação

        Returns
        -------
        Optional[str]
            Mensagem de erro se inválido, None caso contrário
        """
        import re

        if not email:
            return None  # Email é opcional

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return MessageStandards.error('invalid_format', field="email")

        return None


def centered_tabs(
    tab_labels: List[str]
) -> List[Any]:
    """
    Cria tabs centralizadas usando CSS customizado.

    Parameters
    ----------
    tab_labels : List[str]
        Lista com os labels das tabs

    Returns
    -------
    List[Any]
        Lista de objetos de tabs do Streamlit
    """
    # CSS para centralizar as tabs com suporte ao modo escuro
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center !important;
        gap: 20px !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px !important;
        padding: 0 20px !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease !important;
    }

    /* Modo claro */
    @media (prefers-color-scheme: light) {
        .stTabs [data-baseweb="tab"] {
            background: linear-gradient(
                45deg,
                #f0f2f6,
                # #ffffff
            ) !important;
            color: #262730 !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(
                45deg,
                #e1e5ea,
                # #f8f9fa
            ) !important;
            border-color: #bd93f9 !important;
        }
    }

    /* Modo escuro */
    @media (prefers-color-scheme: dark) {
        .stTabs [data-baseweb="tab"] {
            background: linear-gradient(
                45deg,
                #44475a,
                # #6272a4
            ) !important;
            color: #f8f8f2 !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(
                45deg,
                #6272a4,
                # #bd93f9
            ) !important;
            border-color: #ff79c6 !important;
        }
    }

    /* Tab ativa - funciona em ambos os modos */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #bd93f9, #ff79c6) !important;
        color: #282a36 !important;
        border-color: #8be9fd !important;
        box-shadow: 0 4px 15px rgba(189, 147, 249, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(45deg, #ff79c6, #bd93f9) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(255, 121, 198, 0.5) !important;
    }

    /* Forçar estilos para modo escuro se classe dark estiver presente */
    [data-theme="dark"] .stTabs [data-baseweb="tab"] {
        background: linear-gradient(45deg, #44475a, #6272a4) !important;
        color: #f8f8f2 !important;
    }

    [data-theme="dark"] .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(45deg, #6272a4, #bd93f9) !important;
        border-color: #ff79c6 !important;
    }

    /* Forçar estilos para modo claro se classe light estiver presente */
    [data-theme="light"] .stTabs [data-baseweb="tab"] {
        background: linear-gradient(45deg, #f0f2f6, #ffffff) !important;
        color: #262730 !important;
    }

    [data-theme="light"] .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(45deg, #e1e5ea, #f8f9fa) !important;
        border-color: #bd93f9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Criar as tabs com o CSS aplicado
    return st.tabs(tab_labels)  # type: ignore


# Instâncias globais
messages = MessageStandards()
ui_components = UIComponents()
validation = ValidationMessages()
