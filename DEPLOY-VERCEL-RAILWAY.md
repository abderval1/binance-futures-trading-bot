# 🚀 DEPLOY COMPLETO - VERCEL + RAILWAY

## 📋 SUMÁRIO

- **Frontend:** Vercel (GRATIS)
- **Backend:** Railway (GRATIS inicial)
- **Database:** Railway PostgreSQL (GRATIS 1GB)
- **Domain:** Você pode usar domínio próprio ou .vercel.app

---

## 🎯 PASSO 1: DEPLOY BACKEND NO RAILWAY

### 1.1. Criar Conta Railway
1. Acesse: https://railway.app
2. Sign up with GitHub
3. Grant permissions

### 1.2. Instalar Railway CLI
```bash
npm install -g @railway/cli
```

### 1.3. Login
```bash
railway login
# Abre browser, autorize
```

### 1.4. Inicializar Projeto
```bash
cd bot/backend
railway init
```

**Prompt:**
- Project name: `binance-bot-backend`
- Environment: `Python`
- Region: `US East` (ou mais perto)
- Does your project contain a Dockerfile? **No**

Railway cria `railway.json` automaticamente.

### 1.5. Adicionar Variáveis de Ambiente

No Railway dashboard:
1. Vá em seu projeto → Variables
2. Adicione:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://bot_user:password@localhost:5432/binance_bot` (Railway vai fornecer) |
| `SECRET_KEY` | `0618976714e6d1cd42c78c7775320a4d169060740ddc959a1a4b9efc27d58614` |
| `ENCRYPTION_KEY` | `d8a73ce762a9d34e9942cf45137bb64729cf8e27691a7b17c702d05410b733e0` |
| `REDIS_URL` | `redis://localhost:6379/0` (opcional) |
| `BINANCE_API_KEY` | `sua_chave_aqui` |
| `BINANCE_SECRET_KEY` | `sua_secret_aqui` |
| `APP_ENV` | `production` |
| `CORS_ORIGINS` | `https://seu-frontend.vercel.app` |

**Importante:** Railway oferece PostgreSQL gratuito. Crie um plugin:
- No projeto → Plugins → Add Plugin → PostgreSQL
- Copie a `DATABASE_URL` gerada

### 1.6. Deploy
```bash
railway deploy
```

Aguarde (5-10 min). Após concluir, você terá URL:
```
https://bot-backend.up.railway.app
```

**Teste:**
```bash
curl https://bot-backend.up.railway.app/health
# Deve retornar: {"status":"healthy","service":"trading-bot"}
```

---

## 🎯 PASSO 2: DEPLOY FRONTEND NO VERCEL

### 2.1. Instalar Vercel CLI
```bash
npm install -g vercel
```

### 2.2. Login
```bash
vercel login
# Abre browser, autorize
```

### 2.3. Deploy
```bash
cd bot/frontend
vercel --prod
```

**Prompt:**
- Set up and deploy? **Y**
- Which scope? **Your account**
- Link to existing project? **N**
- Project name: `binance-bot-frontend`
- In which directory is your code located? **./**
- Want to override settings? **N**

Vercel vai buildar e deployed.

URL: `https://binance-bot-frontend.vercel.app` (ou similar)

### 2.4. Configurar Variáveis de Ambiente

No Vercel dashboard:
1. Vá no projeto → Settings → Environment Variables
2. Adicione:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://bot-backend.up.railway.app` |

**IMPORTANTE:** O nome da variável deve começar com `VITE_` para o Vite expor ao frontend.

### 2.5. Redeploy
```bash
vercel --prod
```
(ou no dashboard, clicar "Deploy")

---

## 🔗 PASSO 3: CONECTAR FRONTEND + BACKEND

O frontend já está configurado para usar `import.meta.env.VITE_API_URL` (veja `frontend/src/lib/api.ts`).

Após definir `VITE_API_URL` no Vercel, o frontend vai fazer requisições para o backend no Railway.

**Teste:**
1. Acesse frontend: `https://seu-frontend.vercel.app`
2. Faça login: `admin@tradingbot.com` / `ChangeMeNow123!`
3. Adicione uma API key (sua chave Binance real)
4. Faça uma ordem de teste

---

## 🗄️ PASSO 4: DATABASE (RAILWAY POSTGRES)

Já criamos o plugin PostgreSQL no Railway. Agora:

1. Pegue a `DATABASE_URL` do Railway (no dashboard do backend)
2. No Railway backend project → Variables → edite `DATABASE_URL`
3. Cole a URL completa (ex: `postgresql://...`)

4. rode migrations (criar tabelas):
   - Railway tem console:项目中 → Console → Run command:
   ```bash
   python -c "from app.database import engine, Base; from app import models; Base.metadata.create_all(bind=engine)"
   ```

   Ou crie um script de inicialização.

---

## 🔐 PASSO 5: SEGURANÇA

### 5.1. Revogar Tokens Antigos
- Binance: revogue chaves antigas
- GitHub: revogue token `ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

### 5.2. Gerar Novos Secrets
```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "import os; print(os.urandom(32).hex())"
```

Atualize no Railway variables.

### 5.3. Configurar Domain Custom (Opcional)
- Railway: Domínio custom → `api.yourdomain.com`
- Vercel: Domínio custom → `yourdomain.com`
- Configure SSL (automático em ambos)

---

## 🧪 TESTE FINAL

1. **Backend Health:**
```
https://bot-backend.up.railway.app/health
```
   Deve retornar `{"status":"healthy"}`

2. **Frontend:**
```
https://binance-bot-frontend.vercel.app
```
   Deve mostrar login

3. **API Docs:**
```
https://bot-backend.up.railway.app/docs
```
   Deve mostrar Swagger UI

4. **Fluxo completo:**
   - Login
   - Adicionar API key (testnet first!)
   - Fazer order
   - Ver posição

---

## 📊 MONITORAMENTO

### Railway
- Logs: Railway dashboard → Logs
- Metrics: CPU, Memory, Requests
- Alerts: Configure para erro 500

### Vercel
- Analytics: Vercel dashboard → Analytics
- Logs: Vercel dashboard → Functions (se usar serverless)

---

## 🔄 ATUALIZAÇÕES FUTURAS

### Backend (Railway)
Qualquer push no `main` branch do GitHub:
- Railway detecta automaticamente
- Rebuild e deploy

### Frontend (Vercel)
Push em `main`:
- Vercel auto-deploy
- Ou `vercel --prod`

---

## 💰 CUSTOS ESTIMADOS

| Serviço | Plano | Custo/mês |
|---------|-------|-----------|
| Railway (Backend) | Free | $0 (até $5 crédito) |
| Railway (PostgreSQL) | Free | $0 |
| Vercel (Frontend) | Free | $0 |
| **Total** | | **$0-5** |

Após créditos: ~$5-10/mês (backend + DB)

---

## 🆘 TROUBLESHOOTING

### Erro: "ModuleNotFoundError"
No Railway, certifique-se que `requirements.txt` está na pasta `backend/` e contém todas dependências.

### Erro CORS
No `backend/.env` (Railway variables), `CORS_ORIGINS` deve incluir `https://seu-frontend.vercel.app`

### Erro DB connection
`DATABASE_URL` no Railway deve ser a do plugin PostgreSQL (não localhost).

### Frontend não conecta
Verifique `VITE_API_URL` no Vercel está correta (sem trailing slash).

---

## 📝 ALTERAÇÕES FEITAS NESTE DEPLOY

1. **`vercel.json`** - Configuração Vercel para servir frontend estático
2. **`railway.json`** - Configuração Railway para backend Python
3. **`Dockerfile.backend`** - Dockerfile para Railway (opcional, Railway usa Python buildpack por padrão)
4. **`frontend/src/lib/api.ts`** - Já usa `import.meta.env.VITE_API_URL`
5. **`.env.example`** - Atualizado para produção

---

## 🎯 PRONTO PARA DEPLOY!

Agora execute:

```bash
# Backend
cd backend
railway login
railway init
railway deploy

# Frontend
cd frontend
vercel login
vercel --prod
```

**Esperado:**
- Backend: https://bot-backend.up.railway.app
- Frontend: https://binance-bot-frontend.vercel.app

---

## 📞 DÚVIDAS?

Consulte:
- `GETTING-STARTED.md` - Tutorial completo
- `DEPLOYMENT.md` - Outras opções de deploy
- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
