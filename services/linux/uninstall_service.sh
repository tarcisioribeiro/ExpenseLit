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

FOLDER=$(pwd)

#!/bin/bash

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
        sleep 5
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
clear

while true; do
    blue "\nDigte a senha do banco de dados: "
    read -s password
    sleep 1
    blue "\nRepita a senha: "
    read -s confirmation
    sleep 1

    if [ "$password" = "$confirmation" ]; then
        green "\nSenhas coincidem. Realizando o backup do banco de dados..."
        sleep 5
        mysqldump -uroot -p "$password" --databases financas >> backup_financas.sql
        break
    else
        red "\nAs senhas não coincidem. Tente novamente."
        sleep 1
    fi
done

sleep 1
clear

cd $FOLDER
blue "\nDesativando ambiente virtual..."
sleep 5
deactive
blue "\nRemovendo ambiente virtual..."
sleep 5
rm -r venv

sleep 1
clear

green "\nDesinstalação concluída."