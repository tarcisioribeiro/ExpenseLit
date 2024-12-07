# ExpenseLit

Um aplicativo de controle financeiro feito em **Python**, através do framework **Streamlit**. Integrado ao banco de dados **MySQL**, permite o controle de receitas e despesas.

* Primeiramente, assegure-se de ter os seguintes pacotes instalados em sua distro **Linux**:
        
        build-essential git neofetch curl wget mysql-server python3-venv python3-tk python3-pip python3.10-full python3.10-dev dkms perl gcc make default-libmysqlclient-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev llvm xz-utils tk-dev libffi-dev liblzma-dev python3-openssl

* Para poder utilizar o sistema, faça a instalação do serviço, através do usuário **root**, pelos comandos abaixo:

        git clone https://github.com/tarcisioribeiro/ExpenseLit_.git
        cd Finances_Controller/
        sudo ./services/install_service.sh
