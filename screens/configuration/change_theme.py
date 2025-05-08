from dictionary.vars import (
    ABSOLUTE_APP_PATH,
    DARK_THEME,
    SERVER_CONFIG,
    LIGHT_THEME,
    FONTS_DICTIONARY
)
from screens.homepage import Home
from time import sleep
import streamlit as st


class ChangeTheme:
    """
    Classe com métodos para a mudança da aparência da aplicação,
    (fontes e tema).
    """

    def search_theme_image(self, color_theme: str, font_option: str):
        """
        Realiza a busca da imagem demonstrativa do tema,
        cor e fonte selecionado pelo usuário.

        Parameters
        ----------
        color_theme : str
            O esquema de cores selecionado.
        font_option : str
            A fonte selecionada.

        Returns
        -------
        theme_image : str
            O caminho da imagem do tema.
        """
        color_dict = {
            "Escuro": "dark",
            "Claro": "light"
        }
        font_option = font_option.replace(" ", "_")

        theme_image = "{}/reference/images/themes/{}/{}_{}.png".format(
            ABSOLUTE_APP_PATH, color_dict[color_theme],
            color_dict[color_theme],
            font_option
        )
        return theme_image

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
        config_archive: str = ABSOLUTE_APP_PATH + "/.streamlit/config.toml"
        style_archive: str = ABSOLUTE_APP_PATH + "/dictionary/style.py"

        if theme_option == "Escuro":
            with open(config_archive, "w") as archive:
                archive.write(DARK_THEME)
                if font_option == "sans serif":
                    pass
                else:
                    archive.write("\n")
                    archive.write('font = "{}"'.format(font_option))
                archive.write("\n")
                archive.write(SERVER_CONFIG)

        elif theme_option == "Claro":
            with open(config_archive, "w") as archive:
                archive.write(LIGHT_THEME)
                if font_option == "sans serif":
                    pass
                else:
                    archive.write("\n")
                    archive.write('font = "{}"'.format(font_option))
                archive.write("\n")
                archive.write(SERVER_CONFIG)

        if font_option != "sans serif":
            font_archive = FONTS_DICTIONARY[font_option]
            with open(style_archive, "w") as new_style_archive:
                new_style_archive.write(
                    'system_font = "{}"'.format(font_archive)
                )

    def main_menu(self):
        """
        Menu principal.
        """
        themes_options = {
            "Claro": ["sans serif", "serif", "monospace"],
            "Escuro": ["sans serif", "serif", "monospace"]
        }

        col4, col5, col6 = st.columns(3)

        with col4:
            st.subheader(body=":page_with_curl: Opções")
            with st.expander(label="Aparência", expanded=True):
                selected_theme = st.radio(
                    label="Tema",
                    options=themes_options.keys()
                )
                font_option = st.selectbox(
                    label="Fonte",
                    options=themes_options[selected_theme]
                )
            theme_confirm_option = st.checkbox(label="Confirmar opção")

        if theme_confirm_option:
            with col5:
                with st.spinner(text="Aguarde..."):
                    sleep(1.5)
                theme_image = self.search_theme_image(
                    selected_theme,
                    font_option
                )
                st.subheader(body=":camera: Prévia do Tema")
                with st.expander(label="Visualização", expanded=True):
                    st.image(theme_image)

            with col6:
                with st.spinner(text="Aguarde..."):
                    sleep(1.5)
                st.subheader(body=":white_check_mark: Confirmação")
                with st.expander(label="Votação", expanded=True):
                    st.write("Confirmar a mudança de tema?")
                    selected_option = st.radio(
                        label="Opções",
                        options=["Sim", "Não"]
                    )

                confirm_vote = st.button(
                    label=":floppy_disk: Confirmar mudança de tema"
                )

                if confirm_vote:
                    if selected_option == "Sim":
                        self.change_theme(selected_theme, font_option)
                        sleep(1.5)
                        st.rerun()
                        sleep(1.5)
                        Home().main_menu()
                    elif selected_option == "Não":
                        pass
