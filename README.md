# ExpenseLit

Um aplicativo de controle financeiro feito em **Python**, através do framework **Streamlit**. Integrado ao banco de dados **MySQL**, permite o controle de receitas e despesas.

## Instalação em ambiente GNU/Linux

Pensado a ser executado em ambientes Linux (principalmente distribuições em base Debian) em um primeiro momento, esta aplicação possui uma instalação fácil e rápida, que deve ser feita abrindo um terminal, executando os seguintes comandos:

        sudo apt update
        sudo apt upgrade
        sudo apt install git
        git clone https://github.com/tarcisioribeiro/ExpenseLit.git
        cd ExpenseLit
        sudo ./services/install_service.sh

A execução do script **install_service.sh** automaticamente realizará a instalação das dependências e configuração do ambiente da aplicação.