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
echo ""
title "Desinstalação do MySQL"
echo ""

blue "Parando o serviço do MySQL..."
sudo systemctl stop mysql
sleep 3

sudo apt remove --purge mysql-server mysql-client mysql-common mysql-server-core-* mysql-client-core-*
sudo apt autoremove
sudo apt autoclean
sudo rm -rf /etc/mysql /var/lib/mysql /var/log/mysql
sudo deluser mysql
sudo delgroup mysql
sudo apt update

echo ""
green "Desinstalação concluída."
echo ""

read -p "Pressione ENTER para sair."