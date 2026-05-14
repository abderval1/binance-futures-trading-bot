# Script: Upload para GitHub - Automático
# Execute como Administrador no PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Upload para GitHub - Trading Bot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor White
Write-Host ""

# Verificar admin
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$adminRole = [Security.Principal.WindowsBuiltInRole]::Administrator
$isAdmin = $currentUser.Groups -contains (New-Object Security.Principal.WindowsPrincipal($currentUser)).IsInRole($adminRole)

if (-NOT $isAdmin) {
    Write-Host "⚠️  Execute como ADMINISTRADOR!" -ForegroundColor Red
    Write-Host "Clique com botão direito no PowerShell → 'Run as administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/7] Verificando Git..." -ForegroundColor Green
if (-Not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "    Git nao encontrado. Instalando via Chocolatey..." -ForegroundColor Yellow

    # Instalar Chocolatey se nao existir
    if (-Not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "    Instalando Chocolatey..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }

    # Instalar Git
    choco install git -y
    refreshenv
} else {
    Write-Host "    [OK] Git ja instalado: $(git --version)" -ForegroundColor Green
}

# Adicionar git ao PATH se necessario
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$gitPath = (Get-Command git).Source
Write-Host "    Git path: $gitPath" -ForegroundColor Gray

Write-Host ""
Write-Host "[2/7] Navegando para pasta do projeto..." -ForegroundColor Green
cd C:\Users\agostinho.rosario\Downloads\bot

Write-Host "[3/7] Inicializando Git (se necessario)..." -ForegroundColor Green
if (-Not (Test-Path .git)) {
    git init
    Write-Host "    [OK] Git inicializado" -ForegroundColor Green
} else {
    Write-Host "    [OK] Git ja inicializado" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/7] Configurando usuario..." -ForegroundColor Green
$userName = Read-Host "    Seu nome (ex: Joao Silva)"
$userEmail = Read-Host "    Seu email (ex: joao@email.com)"

git config user.name "$userName"
git config user.email "$userEmail"
Write-Host "    [OK] User configurado: $userName <$userEmail>" -ForegroundColor Green

Write-Host ""
Write-Host "[5/7] Criando arquivo .gitignore (verificando)..." -ForegroundColor Green
if (-Not (Test-Path .gitignore)) {
    Write-Host "    Criando .gitignore..."
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
.env

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
dist-ssr/
*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*.swn

# OS
.DS_Store
Thumbs.db

# Secrets
*.key
*.pem
secrets.json
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "    [OK] .gitignore criado" -ForegroundColor Green
} else {
    Write-Host "    [OK] .gitignore ja existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "[6/7] Verificando arquivos sensiveis..." -ForegroundColor Green

# Verificar se API Key.txt existe (arquivo com chaves expostas)
if (Test-Path "API Key.txt") {
    Write-Host "    [ALERTA] Arquivo 'API Key.txt' encontrado!" -ForegroundColor Red
    Write-Host "    Este arquivo contem chaves API expostas. DELETAR?" -ForegroundColor Yellow
    $resp = Read-Host "    Digite 'SIM' para deletar"
    if ($resp -eq "SIM") {
        Remove-Item "API Key.txt" -Force
        Write-Host "    [OK] Arquivo deletado" -ForegroundColor Green
    } else {
        Write-Host "    [CUIDADO] Nao deletei o arquivo. Deleted manualmente" -ForegroundColor Yellow
    }
}

# Verificar se .env tem chaves reais (deveria ter placeholders)
Write-Host "    Verificando backend/.env..."
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match "YOUR_NEW_BINANCE_API_KEY_HERE") {
        Write-Host "    [OK] .env tem placeholders (seguro)" -ForegroundColor Green
    } else {
        Write-Host "    [ALERTA] .env parece ter valores reais. Confira:" -ForegroundColor Yellow
        Write-Host "    Recomendado: substitua por placeholders antes do upload" -ForegroundColor Yellow
        $resp = Read-Host "    Continuar mesmo assim? (s/n)"
        if ($resp -ne "s") {
            Write-Host "    Abortando. Edite backend/.env e tente novamente." -ForegroundColor Red
            pause
            exit 1
        }
    }
} else {
    Write-Host "    [OK] backend/.env nao existe (usara .env.example)" -ForegroundColor Green
}

Write-Host ""
Write-Host "[7/7] Preparando commit..." -ForegroundColor Green

# Adicionar arquivos
git add -A

# Mostrar o que vai ser commitado
Write-Host ""
Write-Host "Arquivos que serao commitados:" -ForegroundColor Cyan
git status --short | Select-Object -First 20 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host ""
$commitMsg = Read-Host "Mensagem do commit (Enter para usar padrao)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Initial commit - Binance Futures Trading Bot"
}

git commit -m "$commitMsg"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no commit. Verifique os arquivos." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "    [OK] Commit criado" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UPLOAD PARA GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor White
Write-Host ""
Write-Host "Agora voce precisa:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Criar repositório no GitHub:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Gray
Write-Host "   Nome: binance-futures-trading-bot" -ForegroundColor Gray
Write-Host "   Nao marcar 'Initialize with README'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Gerar um Personal Access Token (PAT):" -ForegroundColor White
Write-Host "   https://github.com/settings/tokens" -ForegroundColor Gray
Write-Host "   Escolha: 'repo' scope" -ForegroundColor Gray
Write-Host "   Copie o token gerado" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Execute o proximo comando (substituindo):" -ForegroundColor White
Write-Host ""

# Obter remote URL
$remoteUrl = "https://github.com/USERNAME/binance-futures-trading-bot.git"
Write-Host "   git remote add origin $remoteUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Faca o push:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""

$addRemote = Read-Host "Adicionar remote agora? (s/n)"
if ($addRemote -eq "s") {
    $username = Read-Host "    Seu username do GitHub"
    $token = Read-Host "    Seu Personal Access Token (nao mostrado)" -AsSecureString
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
    $plainToken = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)

    $remoteUrlWithToken = "https://$plainToken@github.com/$username/binance-futures-trading-bot.git"
    git remote add origin "$remoteUrlWithToken"

    Write-Host ""
    Write-Host "Fazendo push..." -ForegroundColor Green
    git push -u origin main

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[SUCESSO] Codigo enviado para GitHub!" -ForegroundColor Green
        Write-Host "   https://github.com/$username/binance-futures-trading-bot" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "[ERRO] Nao foi possivel fazer push." -ForegroundColor Red
        Write-Host "Verifique:" -ForegroundColor Yellow
        Write-Host "  1. Token esta correto?" -ForegroundColor Gray
        Write-Host "  2. Repositorio foi criado no GitHub?" -ForegroundColor Gray
        Write-Host "  3. Tem permissao 'repo'?" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "OK. Quando estiver pronto, execute:" -ForegroundColor Yellow
    Write-Host "  git remote add origin https://TOKEN@github.com/USERNAME/repo.git" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Revogue as chaves expostas (Binance + GitHub antigo)" -ForegroundColor White
Write-Host "2. Configure secrets no GitHub (Settings → Secrets) para CI/CD" -ForegroundColor White
Write-Host "3. Edite backend/.env com suas chaves Binance NOVAS" -ForegroundColor White
Write-Host "4. Deploy (docker-compose up -d)" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

pause
