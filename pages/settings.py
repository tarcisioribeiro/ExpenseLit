"""
Página de configurações.
"""

import streamlit as st
from pages.router import BasePage
import time
import json
from pathlib import Path
import configparser
from config.settings import db_categories


class SettingsPage(BasePage):
    def __init__(self):
        super().__init__("Configurações", "⚙️")
        # Aplicar tema inicial se definido
        self._apply_initial_theme()
    
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
        st.subheader("⚙️ Configurações")
        self.render()
    
    def render(self) -> None:
        """
        Renderiza as configurações da aplicação.
        """
        # Tabs para organizar as configurações
        tab1, tab2, tab3 = st.tabs(["🎨 Aparência", "🔧 Sistema", "📊 Dados"])
        
        with tab1:
            self._render_theme_settings()
        
        with tab2:
            self._render_system_settings()
            
        with tab3:
            self._render_data_settings()
    
    def _render_theme_settings(self) -> None:
        """
        Renderiza as configurações de tema.
        """
        st.markdown("### 🎨 Configurações de Aparência")
        
        # Seleção do tema
        current_theme = st.session_state.get('theme', 'dark')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Selecionar Tema:**")
            
            # Opções de tema
            theme_options = {
                "Escuro (Dracula)": "dark",
                "Claro": "light"
            }
            
            selected_theme_display = st.radio(
                "Escolha o tema da aplicação:",
                options=list(theme_options.keys()),
                index=0 if current_theme == 'dark' else 1,
                horizontal=True,
                help="Altere a aparência da aplicação"
            )
            
            selected_theme = theme_options[selected_theme_display]
            
        with col2:
            # Preview do tema
            if selected_theme == 'dark':
                st.markdown(
                    """
                    <div style="
                        background: linear-gradient(135deg, #bd93f9 0%, #ff79c6 100%);
                        padding: 1rem;
                        border-radius: 8px;
                        color: #f8f8f2;
                        text-align: center;
                        margin: 1rem 0;
                    ">
                        🌙 <strong>Tema Escuro</strong><br>
                        <small>Baseado no Dracula</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="
                        background: linear-gradient(135deg, #bd93f9 0%, #ff79c6 100%);
                        padding: 1rem;
                        border-radius: 8px;
                        color: #ffffff;
                        text-align: center;
                        margin: 1rem 0;
                        border: 1px solid #e5e7eb;
                    ">
                        ☀️ <strong>Tema Claro</strong><br>
                        <small>Inspirado no Dracula</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Aplicar tema
        if st.button(
            "🎨 Aplicar Tema", 
            type="primary",
            help="Clique para aplicar o tema selecionado"
        ):
            self._apply_theme(selected_theme)
        
        # Informações sobre os temas
        with st.expander("ℹ️ Sobre os Temas"):
            st.markdown(
                """
                **Tema Escuro (Dracula):**
                - Paleta de cores baseada no popular tema Dracula
                - Ideal para uso noturno ou ambientes com pouca luz
                - Reduz o cansaço visual em sessões prolongadas
                
                **Tema Claro:**
                - Inspirado no Dracula mas com fundo claro
                - Melhor legibilidade em ambientes bem iluminados
                - Contraste otimizado para impressão
                """
            )
    
    def _render_system_settings(self) -> None:
        """
        Renderiza as configurações do sistema.
        """
        st.markdown("### 🔧 Configurações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Configurações de Interface:**")
            
            # Configuração de spinners
            spinner_duration = st.slider(
                "⏱️ Duração dos Spinners (segundos)",
                min_value=1,
                max_value=5,
                value=2,
                help="Tempo de exibição dos indicadores de carregamento"
            )
            
            # Configuração de toast
            toast_duration = st.slider(
                "🍞 Duração das Notificações (segundos)", 
                min_value=1,
                max_value=10,
                value=2,
                help="Tempo de exibição das mensagens de sucesso"
            )
            
        with col2:
            st.markdown("**Configurações de Dados:**")
            
            # Configuração de paginação
            items_per_page = st.number_input(
                "📄 Itens por página",
                min_value=10,
                max_value=100,
                value=20,
                step=10,
                help="Número de itens exibidos por página nas listas"
            )
            
            # Auto-refresh
            auto_refresh = st.checkbox(
                "🔄 Atualização automática",
                value=False,
                help="Atualizar dados automaticamente a cada 30 segundos"
            )
        
        if st.button("💾 Salvar Configurações do Sistema", type="secondary"):
            # Salvar configurações no session_state
            st.session_state.update({
                'spinner_duration': spinner_duration,
                'toast_duration': toast_duration, 
                'items_per_page': items_per_page,
                'auto_refresh': auto_refresh
            })
            
            st.toast("⚙️ Configurações do sistema salvas com sucesso!")
            time.sleep(2)
    
    def _render_data_settings(self) -> None:
        """
        Renderiza as configurações de dados.
        """
        st.markdown("### 📊 Configurações de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Exportação:**")
            
            if st.button("📤 Exportar Dados", help="Exportar todos os dados para JSON"):
                st.info("🚧 Funcionalidade em desenvolvimento...")
            
            if st.button("📥 Importar Dados", help="Importar dados de um arquivo JSON"):
                st.info("🚧 Funcionalidade em desenvolvimento...")
                
        with col2:
            st.markdown("**Limpeza:**")
            
            if st.button(
                "🧹 Limpar Cache", 
                help="Limpar dados temporários da aplicação"
            ):
                # Limpar algumas chaves do session_state 
                keys_to_clear = [
                    'expense_filters', 'revenue_filters', 'account_filters'
                ]
                for key in keys_to_clear:
                    st.session_state.pop(key, None)
                
                st.toast("🧹 Cache limpo com sucesso!")
                time.sleep(2)
            
            if st.button(
                "⚠️ Reset Completo",
                help="Resetar todas as configurações (não afeta dados da API)",
                type="secondary"
            ):
                st.warning("Esta ação irá resetar todas as configurações locais!")
                
    def _apply_theme(self, theme: str) -> None:
        """
        Aplica o tema selecionado.
        
        Parameters
        ----------
        theme : str
            Nome do tema ('dark' ou 'light')
        """
        # Salva o tema no session_state
        st.session_state['theme'] = theme
        
        # Atualiza as cores no arquivo de configuração
        self._update_theme_colors(theme)
        
        # Aplica o tema via JavaScript
        theme_js = f"""
        <script>
        document.documentElement.setAttribute('data-theme', '{theme}');
        </script>
        """
        
        st.markdown(theme_js, unsafe_allow_html=True)
        
        # Feedback para o usuário
        theme_name = "Escuro (Dracula)" if theme == 'dark' else "Claro"
        st.toast(f"🎨 Tema {theme_name} aplicado com sucesso!")
        time.sleep(2)
        
        # Força uma atualização da página
        st.rerun()
    
    def _update_theme_colors(self, theme: str) -> None:
        """
        Atualiza a seção [theme] do arquivo config.toml usando as configurações de settings.py.
        
        Parameters
        ----------
        theme : str
            Nome do tema ('dark' ou 'light')
        """
        config_path = Path(".streamlit/config.toml")
        
        # Obter configuração do tema de settings.py
        theme_config = None
        if theme == 'dark':
            theme_config = db_categories.DARK_THEME
        elif theme == 'light':
            theme_config = db_categories.LIGHT_THEME
        
        if not theme_config:
            st.error(f"Configuração do tema '{theme}' não encontrada")
            return
        
        try:
            # Ler o arquivo existente
            with open(config_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Encontrar a seção [theme] e substituí-la
            new_lines = []
            in_theme_section = False
            theme_section_replaced = False
            
            for line in lines:
                stripped_line = line.strip()
                
                # Verificar se estamos na seção [theme]
                if stripped_line == '[theme]':
                    in_theme_section = True
                    # Adicionar a nova configuração do tema
                    new_lines.append(f"# Tema {'Escuro' if theme == 'dark' else 'Claro'}\n")
                    new_lines.append(theme_config)
                    new_lines.append("\n")
                    theme_section_replaced = True
                    continue
                
                # Verificar se saímos da seção [theme]
                if in_theme_section and stripped_line.startswith('[') and stripped_line != '[theme]':
                    in_theme_section = False
                
                # Pular linhas da seção [theme] antiga
                if in_theme_section:
                    continue
                else:
                    # Manter linhas fora da seção [theme]
                    new_lines.append(line)
            
            # Se a seção [theme] não foi encontrada, adicionar no início
            if not theme_section_replaced:
                theme_section = f"# Tema {'Escuro' if theme == 'dark' else 'Claro'}\n{theme_config}\n\n"
                new_lines.insert(0, theme_section)
            
            # Escrever o arquivo atualizado
            with open(config_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
                
        except Exception as e:
            st.error(f"Erro ao atualizar configuração do tema: {e}")
    
    def _apply_initial_theme(self) -> None:
        """
        Aplica o tema inicial baseado no session_state.
        """
        theme = st.session_state.get('theme', 'dark')
        
        # Aplica o tema via JavaScript
        theme_js = f"""
        <script>
        document.documentElement.setAttribute('data-theme', '{theme}');
        </script>
        """
        
        st.markdown(theme_js, unsafe_allow_html=True)