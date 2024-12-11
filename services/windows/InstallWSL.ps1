if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Este script deve ser executado como Administrador. Feche o PowerShell e execute novamente com privilégios administrativos." -ForegroundColor Red
    exit
}

Write-Host "Iniciando a instalação do WSL..." -ForegroundColor Green
try {
    wsl --install
    Write-Host "O comando 'wsl --install' foi executado. Siga as instruções na tela para completar a instalação." -ForegroundColor Green
} catch {
    Write-Host "Houve um erro ao tentar instalar o WSL: $_" -ForegroundColor Red
}
