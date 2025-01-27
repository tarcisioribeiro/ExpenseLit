from screens.configuration.change_theme import ChangeTheme
from screens.configuration.database_backup import Backup
import streamlit as st


class Configuration:
    """
    Classe com métodos para mudança da aparência do sistema e backup dos dados.
    """

    def main_menu(self):
        """
        Menu principal.
        """
        menu_options = {
            "Aparência": ChangeTheme(),
            "Backup de Dados": Backup(),
        }

        col1, col2, col3 = st.columns(3)

        with col1:
            st.header(body=":wrench: Configurações")

        with col2:

            selected_option = st.selectbox(
                label="Menu", options=menu_options.keys())

        st.divider()

        if selected_option:
            option = menu_options[selected_option]
            option.main_menu()
