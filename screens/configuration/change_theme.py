from dictionary.vars import absolute_app_path, dark_theme, server_config, light_theme, fonts_dictionary
from time import sleep
import streamlit as st


class ChangeTheme:
    """
    Classe com métodos para a mudança da aparência da aplicação (fontes e tema).
    """

    def change_theme(self, theme_option: str, font_option: str):
        """
        Realiza a troca do tema e fonte da aplicação.

        Parameters
        ----------
        theme_option : str
            O tema selecionado pelo usuário.
        font_option : str
            A fonte selecionada pelo usuário.
        """

        config_archive: str = absolute_app_path + "/.streamlit/config.toml"
        style_archive: str = absolute_app_path + "/dictionary/style.py"

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

        if font_option != "Selecione uma opção":
            font_archive = fonts_dictionary[font_option]

            with open(style_archive, "w") as new_style_archive:
                new_style_archive.write(
                    'system_font = "{}"'.format(font_archive))

    def main_menu(self):
        """
        Menu principal.
        """

        col4, col5, col6 = st.columns(3)

        with col4:

            st.subheader(body=":computer: Opções")

            with st.expander(label="Aparência", expanded=True):
                selected_theme = st.radio(
                    label="Tema", options=["Escuro", "Claro"])
                font_option = st.selectbox(label="Fonte", options=[
                                           "Selecione uma opção", "sans serif", "serif", "monospace"])

            theme_confirm_option = st.button(
                label=":white_check_mark: Confirmar opção")

        if selected_theme != "" and theme_confirm_option:
            with col5:
                with st.spinner(text="Aguarde..."):
                    sleep(2.5)
                self.change_theme(selected_theme, font_option)
                sleep(2.5)
                st.rerun()
