from screens.configuration.change_theme import ChangeTheme
from screens.configuration.database_backup import Backup
import streamlit as st


class Configuration:
    def __init__(self):

        menu_options = {
            "Aparência": ChangeTheme(),
            "Backup de Dados": Backup(),
        }

        def configuration_main_menu():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.header(body=":wrench: Configurações")

            with col2:

                selected_option = st.selectbox(label="Menu", options=menu_options.keys())

            st.divider()

            if selected_option:
                option = menu_options[selected_option]
                option.main_menu()

        self.main_menu = configuration_main_menu
