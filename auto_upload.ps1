#!/usr/bin/env powershell
# UPLOAD AUTOMÁTICO PARA GITHUB
# Executa como Administrator

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTO-UPLOAD PARA GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor White
Write-Host ""

# 1. Verificar Admin
Write-Host "[1/8] Verificando privilegios de administrador..." -ForegroundColor Green
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$adminRole = [Security.Principal.WindowsBuiltInRole]::Administrator
$isAdmin = $currentUser.Groups -contains (New-Object Security.Principal.WindowsPrincipal($currentUser)).IsInRole($adminRole)

if (-NOT $isAdmin) {
    Write-Host "    [ERRO] Este script precisa ser executado como ADMINISTRADOR!" -ForegroundColor Red
    Write-Host "    Clique com botão direito no PowerShell → 'Run as administrator'" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "    [OK] Executando como administrador" -ForegroundColor Green

# 2. Instalar Chocolatey (se necessário)
Write-Host "[2/8] Verificando Chocolatey..." -ForegroundColor Green
if (-Not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "    Instalando Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
    Write-Host "    [OK] Chocolatey instalado" -ForegroundColor Green
} else {
    Write-Host "    [OK] Chocolatey ja instalado" -ForegroundColor Green
}

# 3. Instalar Git
Write-Host "[3/8] Instalando Git..." -ForegroundColor Green
if (-Not (Get-Command git -ErrorAction SilentlyContinue)) {
    choco install git -y
    refreshenv
    Write-Host "    [OK] Git instalado" -ForegroundColor Green
} else {
    Write-Host "    [OK] Git ja instalado: $(git --version)" -ForegroundColor Green
}

# 4. Configurar Git
Write-Host "[4/8] Configurando Git..." -ForegroundColor Green
git config --global user.name "abderval1"
git config --global user.email "abderval1@users.noreply.github.com"
Write-Host "    [OK] User: abderval1" -ForegroundColor Green

# 5. Ir para pasta do projeto
Write-Host "[5/8] Acessando pasta do projeto..." -ForegroundColor Green
Set-Location "C:\Users\agostinho.rosario\Downloads\bot"

# 6. Inicializar Git e fazer commit
Write-Host "[6/8] Preparando commit..." -ForegroundColor Green
if (-Not (Test-Path .git)) {
    git init
    Write-Host "    [OK] Git inicializado" -ForegroundColor Green
}

# Verificar se há arquivos para adicionar
git add -A
$commitMsg = "Initial commit - Binance Futures Trading Bot

- Backend: FastAPI + JWT auth + encrypted API keys
- Frontend: React + TypeScript + Vite + TailwindCSS
- Trading Engine for Binance Futures
- Multi-tenant subscription model
- Strategies: SMA Crossover, Grid Trading
- Docker + CI/CD + Security features"

git commit -m "$commitMsg"
Write-Host "    [OK] Commit criado" -ForegroundColor Green

# 7. Criar repositório no GitHub (se não existir) e fazer push
Write-Host "[7/8] Conectando ao GitHub..." -ForegroundColor Green

$token = "SEU_TOKEN_AQUI"
$username = "abderval1"
$repoName = "binance-futures-trading-bot"
$remoteUrl = "https://$token@github.com/$username/$repoName.git"

# Verificar se repo já existe
Write-Host "    Verificando se repositório existe..." -ForegroundColor Gray
try {
    $repoCheck = Invoke-RestMethod -Uri "https://api.github.com/repos/$username/$repoName" -Headers @{
        Authorization = "token $token"
        "User-Agent" = "PowerShell"
    } -Method Get -ErrorAction Stop
    Write-Host "    Repositório já existe: $($repoCheck.html_url)" -ForegroundColor Yellow
} catch {
    Write-Host "    Criando repositório..." -ForegroundColor Yellow
    $body = @{
        name = $repoName
        description = "Multi-tenant Binance Futures trading bot with subscription management"
        private = $false
        auto_init = $false
    } | ConvertTo-Json

    try {
        $createRepo = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers @{
            Authorization = "token $token"
            "User-Agent" = "PowerShell"
        } -Body $body -ContentType "application/json"
        Write-Host "    [OK] Repositório criado: $($createRepo.html_url)" -ForegroundColor Green
    } catch {
        Write-Host "    [AVISO] Erro ao criar repo (pode já existir): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Configurar remote
Write-Host "[8/8] Fazendo push para GitHub..." -ForegroundColor Green

# Remover remote antigo se existir
git remote remove origin 2>$null

# Adicionar remote com token
git remote add origin "$remoteUrl"

# Push
Write-Host "    Enviando arquivos..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅  UPLOAD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor White
    Write-Host ""
    Write-Host "📦 Repositório: https://github.com/abderval1/binance-futures-trading-bot" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔗 Ações necessárias AGORA:" -ForegroundColor Yellow
    Write-Host "1. Revogue este token (segurança!)" -ForegroundColor White
    Write-Host "   https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "2. Delete o arquivo 'API Key.txt' (se existir)" -ForegroundColor White
    Write-Host "3. Configure Secrets no GitHub (Settings → Secrets) para CI/CD:" -ForegroundColor White
    Write-Host "   - SECRET_KEY" -ForegroundColor Gray
    Write-Host "   - ENCRYPTION_KEY" -ForegroundColor Gray
    Write-Host "   - DATABASE_URL" -ForegroundColor Gray
    Write-Host "   - BINANCE_API_KEY" -ForegroundColor Gray
    Write-Host "   - BINANCE_SECRET_KEY" -ForegroundColor Gray
    Write-Host "4. Edite backend/.env com suas chaves Binance REAIS" -ForegroundColor White
    Write-Host "5. Inicie o bot: python backend/start.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ ERRO NO PUSH" -ForegroundColor Red
    Write-Host "Verifique:" -ForegroundColor Yellow
    Write-Host "1. Token tem permissao 'repo'?" -ForegroundColor Gray
    Write-Host "2. Internet funcionando?" -ForegroundColor Gray
    Write-Host "3. Repositorio nao foi criado?" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Tente manualmente:" -ForegroundColor White
    Write-Host "git push -u origin main" -ForegroundColor Cyan
}

pause
