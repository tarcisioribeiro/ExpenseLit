if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Este script deve ser executado como Administrador. Feche o PowerShell e execute novamente com privilégios administrativos." -ForegroundColor Red
    exit
}

Write-Host "Iniciando a instalação do WSL com Ubuntu 22.04..." -ForegroundColor Green
try {
    wsl --install -d Ubuntu-22.04
    Write-Host "A instalação do WSL com Ubuntu 22.04 foi iniciada. Siga as instruções na tela para completar a configuração." -ForegroundColor Green
} catch {
    Write-Host "Houve um erro ao tentar instalar o WSL com Ubuntu 22.04: $_" -ForegroundColor Red
    exit
}

Start-Sleep -Seconds 10

Write-Host "Definindo o Ubuntu 22.04 como a distribuição padrão no WSL..." -ForegroundColor Green
try {
    wsl --set-default Ubuntu-22.04
    Write-Host "O Ubuntu 22.04 foi configurado como a distribuição padrão no WSL." -ForegroundColor Green
} catch {
    Write-Host "Houve um erro ao tentar configurar o Ubuntu 22.04 como padrão: $_" -ForegroundColor Red
}
