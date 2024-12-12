#!/bin/bash

red() {
    echo -e "\033[31m$1\033[0m"
}
green() {
    echo -e "\033[32m$1\033[0m"
}

blue() {
    echo -e "\033[34m$1\033[0m"
}

actual_date=$(date +"%Y-%m-%d")
actual_horary=$(date +"%H_%M_%S")
database_backup_filename="backup_financas_$actual_date_$actual_horary.sql"
backup_directory_name="ExpenseLit_data_backup_$actual_date_$actual_horary"
FOLDER=$(pwd)

while true; do
    blue "\nDigite a senha de root:"
    read -s root_password
    sleep 1
    blue "\nDigite a senha de root novamente: "
    read -s confirm_root_password
    sleep 1

    echo "$root_password" | sudo -S echo "Senha de root aceita."

    if [ $? -eq 0 ]; then
        green "\nVocê tem permissões de root. Continuando com o script..."
        sleep 1
        blue "\nDesativando o serviço da aplicação..."
        sleep 2
        sudo systemctl stop expenselit.service
        sudo systemctl disable expenselit.service
        break
    else
        red "\nSenha de root incorreta. Saindo..."
        sleep 1
        exit 1
    fi
done

sleep 1

while true; do
    blue "\nDigte a senha do banco de dados: "
    read -s password
    sleep 1
    blue "\nRepita a senha: "
    read -s confirmation
    sleep 1

    if [ "$password" = "$confirmation" ]; then
        green "\nSenhas coincidem. Realizando o backup do banco de dados..."
        sleep 1
        mysqldump -uroot -p"$password" --databases financas >> $database_backup_filename
        chmod 700 $database_backup_filename
        break
    else
        red "\nAs senhas não coincidem. Tente novamente."
        sleep 1
    fi
done

cp -r "library/images/accounts/" .
chmod 777 -R "accounts/"
mkdir "$backup_directory_name"
mv "$database_backup_filename" "$backup_directory_name"
mv "accounts/" "$backup_directory_name"

sleep 1

blue "\nDesativando ambiente virtual..."
sleep 1
blue "\nRemovendo ambiente virtual..."
sleep 1
rm -r venv

sleep 1

green "\nDesinstalação concluída."
