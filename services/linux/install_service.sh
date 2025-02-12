#!/usr/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt install nala toilet -y
clear

title_red() {
  clear
  echo ""
  echo -e "\033[31m$(toilet --font pagga --filter border --width 200 "$1")\033[0m"
  echo ""
  sleep 5
}

title_green() {
  clear
  echo ""
  echo -e "\033[32m$(toilet --font pagga --filter border --width 200 "$1")\033[0m"
  echo ""
  sleep 5
}

title_blue() {
  clear
  echo ""
  echo -e "\033[34m$(toilet --font pagga --filter border --width 200 "$1")\033[0m"
  echo ""
  sleep 5
}

title() {
  echo ""
  echo -e "$(toilet --font pagga --filter border --width 200 "$1")"
  echo ""
}

red() {
  echo ""
  echo -e "\033[31m$1\033[0m"
  echo ""
}
green() {
  echo ""
  echo -e "\033[32m$1\033[0m"
  echo ""
}

blue() {
  echo ""
  echo -e "\033[34m$1\033[0m"
  echo ""
}

title "ExpenseLit - Instalação"

FOLDER=$(pwd)

while true; do
  blue "Digite a senha de root:"
  read -s root_password
  blue "Digite a senha de root novamente: "
  read -s confirm_root_password

  echo "$root_password" | sudo -S echo "Senha de root aceita."

  if [ $? -eq 0 ]; then
    green "Você tem permissões de root. Continuando com o script..."
    blue "Instalando dependências..."
    apt install build-essential openssh-server git neofetch curl net-tools wget python3-venv python3-tk python3-pip python3.10-full python3.10-dev dkms perl gcc make default-libmysqlclient-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev llvm xz-utils tk-dev libffi-dev liblzma-dev python3-openssl -y
    ufw enable
    ufw allow 8501
    ufw allow OpenSSH
    break
  else
    red "Senha de root incorreta. Saindo..."
    exit 1
  fi
done

title_blue "Configuração - MySQL"

if ! command -v mysql &>/dev/null; then
  red "O banco de dados MySQL não está instalado. Instalando agora..."
  sleep 2
  sudo apt update && sudo apt install -y mysql-server
  if [ $? -ne 0 ]; then
    red "Erro ao instalar o MySQL. Saindo."
    exit 1
  fi
  green "MySQL instalado com sucesso."
fi

blue "Agora, defina uma senha para o banco de dados, executando estes comando no console do MySQL:"
echo "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'senha'; FLUSH PRIVILEGES;"
blue "Copie o comando acima e troque 'senha' pela senha que deseja definir, mantendo as aspas simples."
blue "Após definir a senha, saia do console do MySQL pelo comando exit."
read -p "Pressione ENTER para confirmar e prosseguir."
sudo mysql

while true; do
  blue "Digite a senha do banco de dados que foi definida anteriormente: "
  read -s password
  blue "Repita a senha: "
  read -s confirmation
  if [ "$password" = "$confirmation" ]; then
    db_script="documentation/database/implantation_financas.sql"
    if [ -f "$db_script" ]; then
      blue "Executando script de implantação do banco de dados..."
      mysql -u root -p"$password" <"$db_script"
      if [ $? -eq 0 ]; then
        green "Script de implantação executado com sucesso."
      else
        red "Erro ao executar o script de implantação."
      fi
    else
      red "Script de implantação não encontrado em '$db_script'."
    fi
    break
  else
    red "As senhas não coincidem. Tente novamente."
  fi
done

title_blue "Ambiente Virtual"

cd $FOLDER
blue "Criando ambiente virtual..."
python3 -m venv venv
blue "Ativando ambiente virtual..."
source venv/bin/activate
pip install streamlit mysql-connector-python python-dotenv matplotlib bcrypt fpdf psutil pdoc

echo "#!/bin/bash" >>expenselit.sh
echo "cd $FOLDER" >>expenselit.sh
echo "source venv/bin/activate" >>expenselit.sh
echo "streamlit run main.py --server.port 8501" >>expenselit.sh
chmod u+x expenselit.sh
sudo mv expenselit.sh /usr/bin/

echo "[Unit]" >>expenselit.service
echo "Description=ExpenseLit - Controle Financeiro" >>expenselit.service
echo "[Service]" >>expenselit.service
echo "ExecStart=/usr/bin/expenselit.sh" >>expenselit.service
echo "[Install]" >>expenselit.service
echo "WantedBy=multi-user.target" >>expenselit.service
sudo mv expenselit.service /lib/systemd/system

sudo systemctl enable expenselit.service
sudo systemctl daemon-reload
sudo systemctl start expenselit.service

cp documentation/images/default.png library/images/accounts/

title_green "Instalação concluída."

link=$(python3 services/linux/get_ipv4.py)

blue "Você pode realizar o acesso a aplicação através dos seguintes links:"
green "$link"

read -p "Pressione ENTER para confirmar e sair."
