# 🚀 DEPLOY RÁPIDO - TUDO AUTOMÁTICO

## ⚡ OPÇÃO 1: DEPLOY AUTOMÁTICO (Recomendado)

### Usando Railway (Backend) + Vercel (Frontend)

---

## 🎯 PASSO 1: DEPLOY BACKEND (Railway)

### 1.1 Instalar Railway CLI
```powershell
npm install -g @railway/cli
```

### 1.2 Fazer Login
```powershell
railway login
```
Abra o link no browser, autorize.

### 1.3 Deploy Backend
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\backend
railway init
```
**Responda:**
- Project name: `binance-bot-backend`
- Type: `Python`
- Region: `US East` (ou mais perto)
- Dockerfile? `No`

Depois:
```powershell
railway deploy
```

Aguarde 5 min. URL: `https://binance-bot-backend.up.railway.app`

---

### 1.4 Adicionar PostgreSQL (Grátis)

No Railway dashboard (browser):
1. Seu Projeto → **Plugins** → **Add Plugin**
2. Escolha **PostgreSQL**
3. Clique **Add Plugin**

Railway vai criar banco e dar `DATABASE_URL`.

---

### 1.5 Configurar Variáveis de Ambiente

No Railway dashboard → **Variables** → **Add Variable**:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | **(copie do plugin PostgreSQL)** |
| `SECRET_KEY` | `0618976714e6d1cd42c78c7775320a4d169060740ddc959a1a4b9efc27d58614` |
| `ENCRYPTION_KEY` | `d8a73ce762a9d34e9942cf45137bb64729cf8e27691a7b17c702d05410b733e0` |
| `BINANCE_API_KEY` | `sua_chave_binance_aqui` |
| `BINANCE_SECRET_KEY` | `sua_secret_binance_aqui` |
| `APP_ENV` | `production` |
| `CORS_ORIGINS` | `https://seu-frontend.vercel.app` |

**IMPORTANTE:** Substitua `sua_chave_binance_aqui` pela sua chave real do Binance (criada agora, trade-only!).

---

### 1.6 Testar Backend

```powershell
curl https://binance-bot-backend.up.railway.app/health
```
Resposta: `{"status":"healthy"}`

Se der erro, veja logs no Railway dashboard.

---

## 🎯 PASSO 2: DEPLOY FRONTEND (Vercel)

### 2.1 Instalar Vercel CLI
```powershell
npm install -g vercel
```

### 2.2 Login
```powershell
vercel login
```
Abra browser, autorize.

### 2.3 Deploy
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\frontend
vercel --prod
```

Responda:
- Set up? **Y**
- Scope: **Your account**
- Link project? **N**
- Project name: `binance-bot-frontend`
- Directory: `./` (Enter)
- Configure: **N**

URL: `https://binance-bot-frontend.vercel.app`

---

### 2.4 Configurar Variável de Ambiente

No Vercel dashboard:
1. Seu projeto → **Settings** → **Environment Variables**
2. Add:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://binance-bot-backend.up.railway.app`
3. Save

---

### 2.5 Redeploy (para pegar variável)

```powershell
vercel --prod --force
```

---

## 🎯 PASSO 3: TESTAR TUDO

1. **Acesse frontend:**
```
https://binance-bot-frontend.vercel.app
```

2. **Login:**
- Email: `admin@tradingbot.com`
- Senha: `ChangeMeNow123!`

3. **Adicione API Key:**
- Label: `Minha Conta Binance`
- API Key: (sua chave Binance)
- Secret: (sua secret)
- Testnet: marque se for testnet
- Click "Add Key"

4. **Faça uma ordem:**
- Symbol: `BTCUSDT`
- Side: `Long`
- Qty: `0.001`
- Click **Buy**

5. **Verifiqueposição** na tabela abaixo.

---

## 🐛 TROUBLESHOOTING RÁPIDO

### Backend dá erro 500?
- Railway → Logs → veja o erro
- Provavelmente `DATABASE_URL` errada ou falta SECRET_KEY

### Frontend não conecta?
- Verifique `VITE_API_URL` no Vercel (sem trailing `/`)
- Verifique `CORS_ORIGINS` no Railway inclui frontend URL

### CORS error?
No Railway Variables, `CORS_ORIGINS` deve ser:
```
https://binance-bot-frontend.vercel.app
```

### Banco de dados vazio?
Railway PostgreSQL plugin instalado? 
- Railway dashboard → Plugins → Add PostgreSQL
- Depois copie a `DATABASE_URL` para Variables

---

## 💰 CUSTO TOTAL

| Serviço | Plano | Custo |
|---------|-------|-------|
| Railway (Backend + DB) | Free tier | $0-5/mês |
| Vercel (Frontend) | Hobby | $0 |
| **Total** | | **GRÁTIS** |

---

## 🔄 ATUALIZAÇÕES

### Atualizar Backend:
```bash
cd backend
git add -A
git commit -m "update"
git push origin main
# Railway auto-deploy
```

### Atualizar Frontend:
```bash
cd frontend
git add -A
git commit -m "update"
git push origin main
vercel --prod
```

---

## 📊 MONITORAMENTO

- **Railway:** Dashboard → Logs + Metrics
- **Vercel:** Dashboard → Analytics + Functions

---

## 🎉 PRONTO!

Se tudo deu certo, você tem:

✅ **Backend:** https://binance-bot-backend.up.railway.app  
✅ **Frontend:** https://binance-bot-frontend.vercel.app  
✅ **Docs:** https://binance-bot-backend.up.railway.app/docs

---

## 🆘 AJUDA

- Railway: https://docs.railway.app
- Vercel: https://vercel.com/docs
- Bot docs: `GETTING-STARTED.md`

---

**Agora execute os comandos acima!** Se travar em algum passo, me avise.
