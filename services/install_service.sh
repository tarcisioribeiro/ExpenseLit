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
    blue "\nDigite a senha de root novamente: "
    read -s confirm_root_password

    echo "$root_password" | sudo -S echo "Senha de root aceita."

    if [ $? -eq 0 ]; then
        green "Você tem permissões de root. Continuando com o script..."
        echo ""
        blue "Instalando dependências..."
        echo ""
	    apt install nala -y
	    sleep 1
        apt install build-essential git neofetch curl wget mysql-server python3-venv python3-tk python3-pip python3.10-full python3.10-dev dkms perl gcc make default-libmysqlclient-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev llvm xz-utils tk-dev libffi-dev liblzma-dev python3-openssl -y
        ufw enable
        ufw allow 8501
        ufw allow OpenSSH
        echo ""
        break
    else
        red "\nSenha de root incorreta. Saindo..."
        exit 1
    fi
done

while true; do
    blue "\nDefina a senha do banco de dados: "
    read -s password
    blue "\nRepita a senha: "
    read -s confirmation

    if [ "$password" = "$confirmation" ]; then
        green "\nSenhas coincidem. Configurando o banco de dados...\n"
        sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$password';"
        sleep 1
        echo ""
        cd $FOLDER
        cd documentation/
        mysql -u root -p"$password" < implantation_financas.sql
        break
    else
        red "\nAs senhas não coincidem. Tente novamente.\n"
    fi
done

cd $FOLDER
sleep 1
blue "\nCriando ambiente virtual...\n"
python3 -m venv venv
blue "\nAtivando ambiente virtual...\n"
source venv/bin/activate
pip install -r requirements.txt

echo "#!/bin/bash" >> fcscript.sh
echo "cd $FOLDER" >> fcscript.sh
echo "source venv/bin/activate" >> fcscript.sh
echo "streamlit run main.py --server.port 8501" >> fcscript.sh
chmod u+x fcscript.sh
sudo mv fcscript.sh /usr/bin/

echo "[Unit]" >> fcscript.service
echo "Description=Controle Financeiro" >> fcscript.service
echo "[Service]" >> fcscript.service
echo "ExecStart=/usr/bin/fcscript.sh" >> fcscript.service
echo "[Install]" >> fcscript.service
echo "WantedBy=multi-user.target" >> fcscript.service
sudo mv fcscript.service /lib/systemd/system

sudo systemctl enable fcscript.service
sudo systemctl daemon-reload
sudo systemctl start fcscript.service

sleep 1
green "\nInstalação concluída.\n"
