#!/bin/bash

FOLDER=$(pwd)

echo "#!/bin/bash" >> fcscript.sh
echo "cd $FOLDER && cd .." >> fcscript.sh
echo "streamlit run main.py --server.port 8501" >> fcscript.sh
chmod +x fcscript.sh
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
