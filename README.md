# ExpenseLit

Um aplicativo de controle financeiro feito em **Python**, através do framework **Streamlit**. Integrado ao banco de dados **MySQL**, permite o controle de receitas e despesas.

## Instalação em ambiente GNU/Linux

Pensado a ser executado em ambientes Linux (principalmente distribuições em base Debian) em um primeiro momento, esta aplicação possui uma instalação fácil e rápida, que deve ser feita abrindo um terminal, executando os seguintes comandos:

        sudo apt update
        sudo apt upgrade
        sudo apt install git
        git clone https://github.com/tarcisioribeiro/ExpenseLit.git
        cd ExpenseLit
        sudo ./services/linux/install_service.sh

A execução do script **install_service.sh** automaticamente realizará a instalação das dependências e configuração do ambiente da aplicação.

## Instalação em ambientes Microsoft Windows

Para utilizar o ExpenseLit em ambiente **Windows**, execute o **Windows PowerShell** como **administrador**, executando em sequência os comandos abaixo:

        Set-ExecutionPolicy Unrestricted
        winget install -e --id Git.Git
        cd ~
        git clone https://github.com/tarcisioribeiro/ExpenseLit.git
        .\ExpenseLit\services\windows\InstallWSL.ps1

Após executar os comandos acima, reinicie a máquina, executando o Windows PowerShell com permissões de administrador novamente, executando o seguinte comando:

        .\ExpenseLit\services\windows\InstallWSL_Ubuntu22.04.ps1

A execução do script **InstallWSL.ps1** automaticamente realizará a instalação do **WSL**, que é o Subsistema Linux para Windows. O script **InstallWSL_Ubuntu22.04.ps1** realizará a instalação do **Ubuntu 22.04** sobre o WSL.

### Configuração da aplicação através do WSL

Para instalar a aplicação no WSL pelo Ubuntu 22.04, execute a aplicação do Ubuntu 22.04 que foi instalada anteriormente, e siga o passo a passo a baixo:

* Ao executar o Ubuntu 22.04, será necessário definir um nome de usuário, o qual deve ser **serveruser**, para que a aplicação possa ser instalada;

OBS.: Defina uma senha que possa lembrar, e a armazene, pois ela será utilizada algumas vezes durante a instalação.

* Após definir uma senha, execute os seguintes comandos na aplicação do Ubuntu 22.04:
        
        cd ~
        sudo apt update
        sudo apt upgrade -y
        sudo apt install build-essential git curl wget neofetch net-tools unzip -y
        mkdir repos Downloads
        cd repos
        git clone https://github.com/tarcisioribeiro/ExpenseLit.git
        cd ExpenseLit
        sudo ./services/linux/install_service.sh

* Após executar os comandos acima, será disponibilizado através do terminal o link de acesso, o qual deve ser copiado e colado em seu navegador de preferência.
