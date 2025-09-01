"""
Utilitários de interface do usuário.

Este módulo padroniza mensagens, estilos e componentes visuais
seguindo melhores práticas de UX/UI para o ExpenseLit.
"""

import streamlit as st
from typing import Any, Dict, Optional, List


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
