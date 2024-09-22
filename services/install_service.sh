FOLDER=$(pwd)
VENV_NAME="dependencies"

echo $FOLDER
cd $HOME
echo ''
echo $(pwd)
echo ''
python3 -m venv dependencies && cd dependencies
source ./bin/activate
cd $FOLDER && cd ..
echo ''
echo $(pwd)
echo ''
pip install -r requirements.txt

echo "#!/bin/bash" >> fcscript.sh
echo "sleep 1" >> fcscript.sh
echo "if [ -z "$VIRTUAL_ENV" ]; then" >> fcscript.sh
echo "    deactivate" >> fcscript.sh
echo "fi" >> fcscript.sh
echo "cd $HOME" >> fcscript.sh
echo "python3 -m venv dependencies && cd dependencies" >> fcscript.sh
echo "source ./bin/activate" >> fcscript.sh
echo "cd $FOLDER && cd .." >> fcscript.sh
echo "pip install -r requirements.txt" >> fcscript.sh
echo "cd /home/$(whoami)/repos/Finances_Controller/" >> fcscript.sh
echo "sleep 1" >> fcscript.sh
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
