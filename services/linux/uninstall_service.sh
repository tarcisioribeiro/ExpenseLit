#!/usr/bin/bash
title_red() {
    echo -e "\033[31m$(toilet --font pagga --filter border --width 200 "$1")\033[0m"
}

title_green() {
    echo -e "\033[32m$(toilet --font pagga --filter border --width 200  "$1")\033[0m"
}

title_blue() {
    echo -e "\033[34m$(toilet --font pagga --filter border --width 200 "$1")\033[0m"
}

title() {
  echo -e "$(toilet --font pagga --filter border --width 200 "$1")"
}

red() {
    echo -e "\033[31m$1\033[0m"
}
green() {
    echo -e "\033[32m$1\033[0m"
}

blue() {
    echo -e "\033[34m$1\033[0m"
}

clear

echo ""
title_red "Desinstalação do ExpenseLit"
echo ""

actual_date=$(date +"%Y-%m-%d")
actual_horary=$(date +"%H_%M_%S")
database_backup_filename="backup_financas_${actual_date}_${actual_horary}.sql"
backup_directory_name="ExpenseLit_data_backup_${actual_date}_${actual_horary}"
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
        sudo rm /lib/systemd/system/expenselit.service
        sudo rm /usr/bin/expenselit.sh
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
        sleep 3
        mysqldump -uroot -p"$password" --databases financas >> $database_backup_filename
        chmod 700 $database_backup_filename
        red "\nApagando a base de dados...\n"
        sleep 3
        mysql -uroot -p"$password" -e "DROP DATABASE financas;"
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
mv "$backup_directory_name" $HOME
green "\nO backup da base de dados foi salvo no diretório '$HOME/$backup_directory_name'."

sleep 3

blue "\nDesativando ambiente virtual..."
sleep 3
blue "\nRemovendo ambiente virtual..."
sleep 3
rm -r venv

sleep 3

clear

green "\nDesinstalação concluída."

echo ""
read -p "Pressione ENTER para sair."