# 🚀 UPLOAD PARA GITHUB - GUIA COMPLETO

## 📋 PRÉ-REQUISITOS

1. **Conta no GitHub** (crie em github.com)
2. **Git instalado** no Windows
3. **Novo token GitHub** (não use o exposto!)

---

## 🔧 PASSO 1: INSTALAR GIT (se ainda não tem)

1. Baixe: https://git-scm.com/download/win
2. Execute o instalador (mantenha opções padrão)
3. No passo "Configuring the line ending conversions":
   - Selecione: **"Checkout Windows-style, commit Unix-style line endings"**
4. Complete a instalação

**Verifique:**
```powershell
git --version
# Deve mostrar: git version 2.xx.x
```

---

## 🔑 PASSO 2: CRIAR NOVO GITHUB TOKEN

1. Acesse: https://github.com/settings/tokens
2. Clique: **"Develop settings"** → **"Personal access tokens"** → **"Tokens (classic)"
**
3. Clique: **"Generate new token"**
4. Dê um nome: `Trading Bot Deploy`
5. **Selecione apenas:** `repo` (full control of private repos)
6. Role até o final → **"Generate token"**
7. **COPIE O TOKEN** (aparece apenas uma vez!)
   - Exemplo: `ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
8. Guarde este token em lugar seguro (será usado como senha)

---

## 📁 PASSO 3: CRIAR REPOSITÓRIO NO GITHUB

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name:** `binance-futures-trading-bot`
   - **Description:** Multi-tenant trading bot for Binance Futures with subscription management
   - **Public** ou **Private** (recomendado: Private)
   - **❌ NÃO** marque "Initialize this repository with a README"
3. Clique: **"Create repository"**

---

## 💻 PASSO 4: CONFIGURAR GIT LOCAL (no PowerShell)

```powershell
# Navegue até a pasta do projeto
cd C:\Users\agostinho.rosario\Downloads\bot

# Inicialize git (se ainda não feito)
git init

# Configure seu usuário (substitua com seus dados)
git config user.name "Seu Nome"
git config user.email "seu@email.com"

# Verifique configuração
git config --list
```

---

## 🔐 PASSO 5: ADICIONAR REMOTE E FAZER PUSH

### Opção A: Usando Token na URL (Mais Fácil - MAS MENOS SEGURO)

```powershell
# No diretório do projeto (bot/)
git remote add origin https://SEU_TOKEN_AQUI@github.com/SEU_USERNAME/binance-futures-trading-bot.git

# Exemplo:
# git remote add origin https://ghp_abc123...@github.com/johndoe/binance-futures-trading-bot.git

# Adicione todos os arquivos
git add -A

# Faça commit
git commit -m "Initial commit - Multi-tenant Binance Futures Trading Bot

- Backend: FastAPI + PostgreSQL + Binance Futures API
- Frontend: React + TypeScript + Vite + TailwindCSS
- Features: User management, API key encryption, trading engine
- Security: AES-256-GCM encrypted keys, trade-only permissions
- Subscription plans: Basic/Pro/Enterprise multi-tenant support"

# Envie para GitHub
git push -u origin main
```

**O token fica salvo no config do git** - não compartilhe este arquivo.

---

### Opção B: Usando Credentials Helper (Mais Seguro)

```powershell
# 1. Adicione remote SEM token
git remote add origin https://github.com/SEU_USERNAME/binance-futures-trading-bot.git

# 2. Configure credential helper para armazenar token
git config --global credential.helper manager-core
# (no Windows, isso usa o Windows Credential Manager)

# 3. Primeiro push (vai pedir usuário e senha)
git push -u origin main

# Quando pedir:
#   Username: SEU_USERNAME (ou seu email do GitHub)
#   Password: COLE O TOKEN que você gerou (não sua senha!)
```

O Windows salvará o token e não pedirá novamente.

---

## ✅ PASSO 6: VERIFICAR UPLOAD

1. Acesse: https://github.com/SEU_USERNAME/binance-futures-trading-bot
2. Veja todos os arquivos lá
3. Verifique que **NÃO** tem:
   - `backend/.env` (está no .gitignore)
   - `API Key.txt` (contém chaves expostas - delete isso!)

---

## 🗑️ PASSO 7: DELETAR ARQUIVO COM CHAVES EXPOSTAS

**IMPORTANTE:** Você tem um arquivo `API Key.txt` com as chaves expostas. **Delete isso ANTES de fazer upload ou DELETE do GitHub após upload.**

```powershell
# No diretório do projeto:
Remove-Item "C:\Users\agostinho.rosario\Downloads\bot\API Key.txt" -Force
```

Se já fez upload:
1. Vá no GitHub → repository → `API Key.txt`
2. Clique no arquivo → "Delete this file"
3. Faça commit da deletion

---

## 🔄 COMANDOS ÚTEIS

### Ver status
```powershell
git status
```

### Ver o que mudou
```powershell
git diff
```

### Desfazer último commit (se errou)
```powershell
git reset --hard HEAD~1
```

### Clonar em outro lugar
```powershell
git clone https://github.com/SEU_USERNAME/binance-futures-trading-bot.git
```

---

## 🐛 TROUBLESHOOTING

### Erro: "fatal: not a git repository"
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot
git init
git remote add origin https://...
```

### Erro: "remote: Repository not found"
- Verifique se o repositório foi criado no GitHub
- Verifique o nome do usuário no URL
- Use HTTPS (não SSH) para simplificar

### Erro: "Authentication failed"
- Token errado → gere novo
- Token não tem permissão `repo` → edite token
- Use o token como **senha**, não login

### Erro: "Permission denied (publickey)"
- Você está usando SSH mas não configurou chave
- Use HTTPS URL em vez de SSH
- Ou configure SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

## 📝 .gitignore (JÁ CONFIGURADO)

O projeto já tem `.gitignore` que exclui:
- `backend/venv/` (ambiente virtual)
- `backend/.env` (secrets)
- `frontend/node_modules/`
- `*.log`
- `trading_bot.db` (banco)
- Arquivos do sistema

**Verifique:** Arquivos sensíveis NÃO vão pro GitHub.

---

## 🎯 CHECKLIST ANTES DO PUSH

- [ ] Git instalado (`git --version` funciona)
- [ ] Conta GitHub criada
- [ ] Novo token gerado (scope: `repo`)
- [ ] Repositório criado no GitHub
- [ ] `.gitignore` existe (está no projeto)
- [ ] Arquivo `API Key.txt` deletado (contém chaves expostas!)
- [ ] `.env` tem placeholders (não chaves reais comprometidas)
- [ ] commit message descritivo

---

## 📦 ESTRUTURA QUE SERÁ ENVIADA

```
bot/
├── .git/                    (criado pelo git)
├── .gitignore              ✅ Configurado
├── README.md
├── DEPLOYMENT.md
├── SECURITY.md
├── GETTING-STARTED.md
├── HOW_TO_RUN.md
├── PROJECT-COMPLETE.md
├── backend/
│   ├── .env.example        ✅ Template seguro
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── start.py
│   ├── test_setup.py
│   ├── app/                ✅ Todo código
│   └── ...
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   └── ...
└── docker-compose.yml
```

**NÃO enviará:**
- `backend/.env` (no .gitignore)
- `backend/venv/` (no .gitignore)
- `backend/trading_bot.db` (no .gitignore)
- `frontend/node_modules/` (no .gitignore)
- `API Key.txt` (delete antes!)

---

## 🎉 APÓS O UPLOAD

1. **Configure GitHub Pages** (opcional):
   - Settings → Pages → Source: `gh-pages` branch
   - Acesse: `https://SEU_USERNAME.github.io/binance-futures-trading-bot`

2. **Configure CI/CD** (já está no `.github/workflows/ci-cd.yml`):
   - Automático na push para `main`
   - Roda testes, lint, security scan

3. **Configure Secrets no GitHub** (para CI/CD):
   - Repository → Settings → Secrets and variables → Actions
   - Adicione:
     - `SECRET_KEY` (seu secret)
     - `ENCRYPTION_KEY` (sua encryption key)
     - `DATABASE_URL` (PostgreSQL)
     - `BINANCE_API_KEY` (admin key)
     - `BINANCE_SECRET_KEY` (admin secret)

---

## 📚 DOCUMENTAÇÃO NO GITHUB

Adicione um `README.md` bom (já tem um no projeto) que inclua:

```markdown
# Binance Futures Trading Bot

Multi-tenant subscription-based trading platform.

## Features
- User management with roles
- Encrypted API key storage
- Binance Futures trading
- Built-in strategies
- React dashboard

## Quick Start
```bash
git clone https://github.com/SEU_USER/binance-futures-trading-bot.git
cd binance-futures-trading-bot
docker-compose up -d
```

## Documentation
- [Getting Started](docs/GETTING-STARTED.md)
- [API Reference](docs/API.md)
- [Security](docs/SECURITY.md)

## License
Proprietary - All rights reserved.
```

---

## 🔄 SYNC FUTURO

Para atualizar o GitHub após mudanças locais:

```powershell
cd C:\Users\agostinho.rosario\Downloads\bot

# Veja o que mudou
git status

# Adicione mudanças
git add -A

# Commit
git commit -m "feat: add WebSocket support"

# Push
git push origin main
```

---

## 🎯 RESUMO DOS COMANDOS

```powershell
# 1. Navegar
cd C:\Users\agostinho.rosario\Downloads\bot

# 2. Inicializar (se não feito)
git init

# 3. Configurar usuário
git config user.name "Seu Nome"
git config user.email "seu@email.com"

# 4. Adicionar remote (substitua SEU_TOKEN e SEU_USERNAME)
git remote add origin https://ghp_SEU_TOKEN_AQUI@github.com/SEU_USERNAME/binance-futures-trading-bot.git

# 5. Primeiro commit
git add -A
git commit -m "Initial commit - Binance Futures Trading Bot"

# 6. Push
git push -u origin main

# 7. Verifique no browser:
# https://github.com/SEU_USERNAME/binance-futures-trading-bot
```

---

## ⚠️ IMPORTANTE

**ANTES DE FAZER UPLOAD:**
1. Delete o arquivo `API Key.txt` (contém chaves expostas!)
2. Verifique que `.env` não tem chaves reais (só exemplos)
3. Confirme que `.gitignore` protege `backend/.env`

**APÓS UPLOAD:**
1. Revogue tokens antigos no GitHub
2. Configure repositório secrets (CI/CD)
3. Habilite issues, projects, etc.
4. Convide colaboradores se houver

---

**Pronto! Agora basta executar os comandos acima.**

Se tiver problemas, me avise com o erro exato.
