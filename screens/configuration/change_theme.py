from dictionary.vars import absolute_app_path, dark_theme, server_config, light_theme, operational_system
from time import sleep
import streamlit as st


class ChangeTheme:
    def __init__(self):

        def change_theme(theme_option: str, font_option: str):

            config_archive: str = absolute_app_path + "/.streamlit/config.toml"

            if theme_option == "Escuro":
                with open(config_archive, "w") as archive:
                    archive.write(dark_theme)
                    if font_option == "Selecione uma opção":
                        pass
                    else:
                        archive.write("\n")
                        archive.write('font = "{}"'.format(font_option))
                    archive.write("\n")
                    archive.write(server_config)

            elif theme_option == "Claro":
                with open(config_archive, "w") as archive:
                    archive.write(light_theme)
                    if font_option == "Selecione uma opção":
                        pass
                    else:
                        archive.write("\n")
                        archive.write('font = "{}"'.format(font_option))
                    archive.write("\n")
                    archive.write(server_config)
    
        def main_menu():

            col4, col5, col6 = st.columns(3)

            with col4:

                st.subheader(body=":computer: Opções")

                with st.expander(label="Aparência", expanded=True):
                    selected_theme = st.radio(label="Tema", options=["Escuro", "Claro"])
                    font_option = st.selectbox(label="Fonte", options=["Selecione uma opção", "sans serif", "serif", "monospace"])

                theme_confirm_option = st.button(label=":white_check_mark: Confirmar opção")

            if selected_theme != "" and theme_confirm_option:
                with col5:
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)
                    change_theme(selected_theme, font_option)
                    sleep(2.5)
                    st.rerun()

        self.main_menu = main_menu