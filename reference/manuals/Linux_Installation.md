# Instalação em ambiente GNU/Linux

   Pensado a ser executado em distribuições Linux de base Debian em um primeiro momento, esta aplicação possui uma instalação fácil e rápida, que deve ser feita abrindo um terminal e executando os seguintes comandos, em sequência:

   ```bash
   sudo apt update
   sudo apt upgrade -y
   mkdir -p ~/repos
   sudo apt install git unzip wget -y
   cd ~/repos
   wget https://github.com/tarcisioribeiro/ExpenseLit/archive/refs/heads/main.zip
   unzip main.zip
   mv ExpenseLit-main ExpenseLit
   cd ExpenseLit/
   sudo ./services/linux/install_service.sh
   ```

   A execução do script **install_service.sh** automaticamente realizará a instalação das dependências e configuração do ambiente da aplicação.