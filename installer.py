import os
import zipfile
import requests
import subprocess
from pathlib import Path

user_home = Path(os.path.expanduser("~"))

zip_path = user_home / "main.zip"

url = "https://github.com/tarcisioribeiro/ExpenseLit/archive/refs/heads/main.zip"

extracted_folder = user_home / "ExpenseLit"

new_folder_name = user_home / "ExpenseLit"

wsl_powershell_script = "{}\\ExpenseLit\\services\\windows\\InstallWSL.ps1".format(user_home)
wsl_ubuntu_powershell_script = "{}\\ExpenseLit\\services\\windows\\InstallWSL_Ubuntu22.04.ps1".format(user_home)

print("Baixando o arquivo...")
response = requests.get(url)
with open(zip_path, "wb") as f:
    f.write(response.content)

print("Extraindo o arquivo...")
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(user_home)

extracted_folder.rename(new_folder_name)

os.remove(zip_path)

print("Instalando o WSL...")
subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", wsl_powershell_script], check=True)

print("Instalando o WSL...")
subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", wsl_ubuntu_powershell_script], check=True)

print("Instalação concluída!")
