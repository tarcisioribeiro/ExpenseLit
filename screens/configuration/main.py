from dictionary.vars import (
    absolute_app_path,
    dark_theme,
    light_theme,
    server_config,
    operational_system,
    db_password,
    db_database,
    db_user,
    today,
    absolute_app_path
)
from functions.get_actual_time import GetActualTime
from pathlib import Path
from time import sleep
import streamlit as st
import subprocess
import os


class Configuration:
    """
    Classe que representa a tela de configurações do sistema.

    Attributes
    ----------
    change_theme(theme_option)
        Realiza a troca do tema de cores do sistema.
    main_menu()
        Apresenta o menu principal das configurações.
    """

    def change_theme(self, theme_option: str, font_option: str):
        """
        Realiza a troca do tema de cores do sistema.

        Parameters
        ----------
        theme_option: str
            O tema escolhido para o usuário.
        """

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

    def make_backup(
        self, backup_path: str, operational_system: str = operational_system
    ):
        """
        Realiza o backup do banco de dados da aplicação, salvando o arquivo no diretório informado pelo usuário.

        Parameters
        ----------
        backup_path: str
            O diretório escolhido pelo usuário.
        operational_system: str
            O sistema operacional que está sendo utilizado, que é definido automaticamente pela importação e utilização do módulo **os**.
        """
        time = GetActualTime()
        actual_time = time.get_actual_time()
        actual_time = actual_time.replace(":", "_")

        directory_command = "cd " + backup_path
        backup_archive_name = "backup_{}_{}_{}.sql".format(
            db_database, today, actual_time
        )
        backup_command = "mysqldump -u{} -p{} --databases {} >> {}".format(
            db_user, db_password, db_database, backup_archive_name
        )

        if operational_system == "posix":
            backup_shell_script_name = absolute_app_path + "/services/temp_backup.sh"
            with open(backup_shell_script_name, "w") as backup_archive:
                backup_archive.write("#!/bin/bash")
                backup_archive.write("\n")
                backup_archive.write(directory_command)
                backup_archive.write("\n")
                backup_archive.write("sleep 1")
                backup_archive.write("\n")
                backup_archive.write(backup_command)
                backup_archive.write("\n")
                backup_archive.write("sleep 1")
            
            modified_archive = Path(backup_shell_script_name)
            modified_archive.chmod(0o777)

            with st.spinner(text="Navegando ao diretório {}...".format(backup_path)):
                sleep(2)
            with st.spinner(
                text="Realizando o backup do arquivo {}...".format(backup_archive_name)
            ):
                sleep(2)
            try:
                subprocess.run(["bash", backup_shell_script_name], check=True, text=True, capture_output=True)
                os.remove(backup_shell_script_name)
                absolute_backup_archive_path = backup_path + "/" + backup_archive_name
                modified_backup_archive = Path(absolute_backup_archive_path)
                modified_backup_archive.chmod(0o777)
                st.info(body="O arquivo {} foi salvo no diretório {}.".format(backup_archive_name, backup_path))
                
            except subprocess.CalledProcessError as error:
                st.error(body="Erro ao executar o script: {}".format(error.stderr), icon="🚨")


    def main_menu(self):
        """
        Apresenta o menu principal das configurações.
        """

        col1, col2, col3 = st.columns(3)

        with col1:
            st.header(body=":wrench: Configurações")

        st.divider()

        col4, col5, col6 = st.columns(3)

        with col4:
            with st.expander(label="Aparência", expanded=True):
                selected_theme = st.radio(label="Tema", options=["Escuro", "Claro"])
                font_option = st.selectbox(label="Fonte", options=["Selecione uma opção", "sans serif", "serif", "monospace"])

            theme_confirm_option = st.button(label=":white_check_mark: Confirmar opção")

        with col4:
            if operational_system == "posix":
                placeholder_text = "Ex: /home/'usuario'/Downloads"
            elif operational_system == "nt":
                placeholder_text = "Ex: C:\\Users\\usuario\\Downloads"

            with st.expander(label=":floppy_disk: Backup de dados", expanded=True):
                backup_directory = st.text_input(
                    label="Diretório de backup", placeholder=placeholder_text
                )

            backup_confirm_button = st.button(
                label=":white_check_mark: Confirmar diretório"
            )

        if selected_theme != "" and theme_confirm_option:
            with col5:
                with st.spinner(text="Aguarde..."):
                    sleep(2.5)
                self.change_theme(selected_theme, font_option)
                sleep(2.5)
                st.rerun()
        else:
            ...

        if backup_confirm_button:
            with col5:
                with st.spinner(text="Aguarde..."):
                    sleep(2.5)
                if backup_directory != "":
                    self.make_backup(backup_directory)
                elif backup_directory == "":
                    st.error(
                        body="O caminho do diretório está vazio ou não preenchido.",
                        icon="🚨",
                    )
