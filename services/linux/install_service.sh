#!/usr/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt install nala toilet -y
clear

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
title "ExpenseLit - Instalação"
echo ""

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
        blue "\nInstalando dependências..."
        sleep 5
        apt install build-essential openssh-server git neofetch curl net-tools wget python3-venv python3-tk python3-pip python3.10-full python3.10-dev dkms perl gcc make default-libmysqlclient-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev llvm xz-utils tk-dev libffi-dev liblzma-dev python3-openssl -y
        ufw enable
        ufw allow 8501
        ufw allow OpenSSH
        break
    else
        red "\nSenha de root incorreta. Saindo..."
        sleep 1
        exit 1
    fi
done

sleep 1
clear

title_blue "Instalação e configuração do banco de dados"

if ! command -v mysql &> /dev/null; then
    red "O banco de dados MySQL não está instalado. Instalando agora...\n"
    sleep 2
    sudo apt update && sudo apt install -y mysql-server
    if [ $? -ne 0 ]; then
        red "\nErro ao instalar o MySQL. Saindo."
        exit 1
    fi
    green "\nMySQL instalado com sucesso."
fi

blue "\nAgora, defina uma senha para o banco de dados, executando estes comando no console do MySQL:\n"
sleep 1
sleep 1
echo ""
echo "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'senha'; FLUSH PRIVILEGES;"
echo ""
sleep 1
blue "\nCopie o comando acima e troque 'senha' pela senha que deseja definir, mantendo as aspas simples.\n"
sleep 1
blue "\nApós definir a senha, saia do console do MySQL pelo comando exit.\n"
sleep 1
read -p "Pressione ENTER para confirmar e prosseguir."
sl
sudo mysql

while true; do
    blue "\nDigite a senha do banco de dados que foi definida anteriormente: "
    read -s password
    blue "\nRepita a senha: "
    read -s confirmation
    if [ "$password" = "$confirmation" ]; then
        db_script="documentation/database/implantation_financas.sql"
        if [ -f "$db_script" ]; then
            blue "\nExecutando script de implantação do banco de dados..."
            mysql -u root -p"$password" < "$db_script"
            if [ $? -eq 0 ]; then
                green "\nScript de implantação executado com sucesso."
            else
                red "\nErro ao executar o script de implantação."
            fi
        else
            red "\nScript de implantação não encontrado em '$db_script'."
        fi
        break
    else
        red "\nAs senhas não coincidem. Tente novamente."
    fi
done

sleep 1
clear

echo ""
title_blue "Ambiente Virtual"
echo ""

cd $FOLDER
blue "\nCriando ambiente virtual..."
sleep 1
python3 -m venv venv
blue "\nAtivando ambiente virtual..."
sleep 1
source venv/bin/activate
pip install streamlit mysql-connector-python python-dotenv matplotlib bcrypt fpdf psutil pdoc
sleep 1
clear

echo "#!/bin/bash" >> expenselit.sh
echo "cd $FOLDER" >> expenselit.sh
echo "source venv/bin/activate" >> expenselit.sh
echo "streamlit run main.py --server.port 8501" >> expenselit.sh
chmod u+x expenselit.sh
sudo mv expenselit.sh /usr/bin/

echo "[Unit]" >> expenselit.service
echo "Description=ExpenseLit - Controle Financeiro" >> expenselit.service
echo "[Service]" >> expenselit.service
echo "ExecStart=/usr/bin/expenselit.sh" >> expenselit.service
echo "[Install]" >> expenselit.service
echo "WantedBy=multi-user.target" >> expenselit.service
sudo mv expenselit.service /lib/systemd/system

sudo systemctl enable expenselit.service
sudo systemctl daemon-reload
sudo systemctl start expenselit.service

cp documentation/images/default.png library/images/accounts/

green "\nInstalação concluída."

link=$(python3 services/linux/get_ipv4.py)

sleep 5

blue "Você pode realizar o acesso a aplicação através dos seguintes links:\n"
green "$link"

echo ""
read -p "Pressione ENTER para confirmar e sair."
