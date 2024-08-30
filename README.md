# Finances Controller

* Primeiramente, assegure-se de ter os seguintes pacotes instalados em sua distro **Linux**:

        python3-pip
        p7zip-full
        p7zip-rar


* Para poder utilizar o sistema, faça a instalação dos pacotes pip necessários através do usuário **root**, pelos comandos abaixo:

        sudo su
        pip install -r requirements.txt


* Crie um arquivo **.env** com os dados abaixo:

        touch .env
        echo DB_PORT='port' >> .env
        echo DB_HOSTNAME='host' >> .env
        echo DB_USER=root >> .env
        echo DB_NAME=financas >> .env
        echo DB_PASSWORD='password' >> .env


* Copie o executável do programa:

        cd services
        sudo cp fcscript.sh /usr/bin/
        sudo nano /usr/bin/fcscript.sh

    * Troque a variável **$USER** pelo nome do usuário.

* Faça a criação do serviço como **systemd**:

        sudo cp fcscript.service /lib/systemd/system
        sudo systemctl daemon-reload
        sudo systemctl enable fcscript.service
        sudo systemctl start fcscript.service
