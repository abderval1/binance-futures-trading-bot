# 🚀 DEPLOY AUTOMÁTICO - VERCEL + RAILWAY

## ⚡ EXECUÇÃO AUTOMÁTICA (Recomendado)

Este script guia você through o deploy completo.

---

## 📋 PRÉ-REQUISITOS

1. **Contas criadas:**
   - GitHub: ✅ (você tem)
   - Railway: https://railway.app
   - Vercel: https://vercel.com

2. **Git instalado** ✅ (já fizemos)

3. **Node.js instalado** (para Vercel CLI)
   - Baixe: https://nodejs.org/en/download/

---

## 🎯 PASSO A PASSO MANUAL (Mais Confiável)

### **Passo 1: Deploy Backend no Railway**

1. **Abra PowerShell como Administrador**

2. **Instale Railway CLI** (se não tiver):
```powershell
npm install -g @railway/cli
```

3. **Login no Railway:**
```powershell
railway login
```
- Abre browser → autorize
- Volte para PowerShell

4. **Navegue até backend:**
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\backend
```

5. **Inicialize projeto Railway:**
```powershell
railway init
```
- ** Project name:** `binance-bot-backend`
- ** Environment:** `Python`
- ** Region:** `US East` (ou mais próximo)
- ** Dockerfile?** `No`

6. **Adicione PostgreSQL:**
   - No Railway dashboard (browser):
   - Vá em seu projeto → Plugins → Add Plugin
   - Escolha **PostgreSQL**
   - Railway cria automático

7. **Configure Variáveis de Ambiente:**
   No Railway dashboard → Variables → Add:

```
KEY                       VALUE
────────────────────────────────────────────────────────
DATABASE_URL              (copie do plugin PostgreSQL)
SECRET_KEY                0618976714e6d1cd42c78c7775320a4d169060740ddc959a1a4b9efc27d58614
ENCRYPTION_KEY            d8a73ce762a9d34e9942cf45137bb64729cf8e27691a7b17c702d05410b733e0
BINANCE_API_KEY           SUA_CHAVE_AQUI
BINANCE_SECRET_KEY        SUA_SECRET_AQUI
REDIS_URL                 (opcional, deixe vazio se não usar)
APP_ENV                   production
CORS_ORIGINS              https://seu-frontend.vercel.app
```

8. **Deploy Backend:**
```powershell
railway deploy
```
Aguarde 5-10 min.

**Resultado:** URL tipo `https://bot-backend.up.railway.app`

9. **Teste:**
```powershell
curl https://bot-backend.up.railway.app/health
```
Deve retornar: `{"status":"healthy","service":"trading-bot"}`

---

### **Passo 2: Deploy Frontend no Vercel**

1. **Instale Vercel CLI:**
```powershell
npm install -g vercel
```

2. **Login Vercel:**
```powershell
vercel login
```
- Abre browser → autorize

3. **Navegue até frontend:**
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\frontend
```

4. **Deploy:**
```powershell
vercel --prod
```

- **Set up and deploy?** `Y`
- **Which scope?** `Your account`
- **Link to existing project?** `N`
- **Project name:** `binance-bot-frontend`
- **Directory:** `./` (Enter)
- **Configure settings?** `N`

Aguarde build (2-5 min).

**Resultado:** URL tipo `https://binance-bot-frontend.vercel.app`

5. **Configure Variável de Ambiente:**
   - Vá no Vercel dashboard → projeto → Settings → Environment Variables
   - Add:
     ```
     Key: VITE_API_URL
     Value: https://bot-backend.up.railway.app
     ```
   - Clique "Save"

6. **Redeploy** (para pegar nova variável):
```powershell
vercel --prod --force
```
Ou no dashboard → Deploy → Redeploy latest

---

### **Passo 3: Testar Tudo Junto**

1. **Acesse frontend:**
```
https://binance-bot-frontend.vercel.app
```

2. **Faça login:**
- Email: `admin@tradingbot.com`
- Senha: `ChangeMeNow123!`

3. **Adicione API Key:**
- Use sua chave Binance REAL (não testnet)
- Ou crie chave testnet e marque "Testnet"

4. **Faça uma ordem de teste:**
- Symbol: `BTCUSDT`
- Quantity: `0.001`
- Clique Buy

5. **Verifique posição** aparecer na tabela.

---

## 🐛 SE DER ERRO:

### Backend não inicia no Railway
- Logs: Railway dashboard → Logs
- Common issues:
  - `DATABASE_URL` ausente → adicione
  - `SECRET_KEY` muito curta → min 32 chars
  - Dependências faltando → `requirements.txt` deve ter tudo

### Frontend não conecta
- Erro CORS? Verifique `CORS_ORIGINS` no Railway inclui frontend URL
- Erro 404? Verifique `VITE_API_URL` no Vercel

### Frontend build falha
- Node.js version: Railway usa Node 18 por padrão (frontend requer 18+)
- `npm install`可能 falhou - rode manualmente no frontend/

---

## 🔄 ATUALIZAÇÕES FUTURAS

Sempre que fizer mudanças:

**Backend:**
```bash
cd backend
git add -A
git commit -m "msg"
git push origin main
# Railway auto-deploy (se configurado)
```

**Frontend:**
```bash
cd frontend
git add -A
git commit -m "msg"
git push origin main
vercel --prod
```

---

## 📊 CUSTOS

| Serviço | Free Tier | Quando Paga |
|---------|-----------|-------------|
| Railway (Backend) | $5 crédito inicial | ~$5/mês após |
| Railway (PostgreSQL) | 1GB grátis | ~$5/mês se expandir |
| Vercel (Frontend) | 100GB bandwidth/mes | Grátis para sempre |
| **Total inicial** | **$0** | **$5-10/mês** |

---

## 🎯 PRONTO!

Agora você tem:
- ✅ Backend rodando no Railway
- ✅ Frontend rodando no Vercel
- ✅ Database no Railway PostgreSQL
- ✅ DNS configurado (subdomínios gratuitos)

**URLs:**
- Frontend: `https://binance-bot-frontend.vercel.app`
- Backend: `https://bot-backend.up.railway.app`
- API Docs: `https://bot-backend.up.railway.app/docs`

---

## 📝 ARQUIVOS CRIADOS PARA DEPLOY

- `vercel.json` - Config Vercel (frontend)
- `railway.json` - Config Railway (backend)
- `Dockerfile.backend` - Docker (opcional)
- `DEPLOY-VERCEL-RAILWAY.md` - Este guia

---

## 🆘 PRECISA DE AJUDA?

1. Railway Docs: https://docs.railway.app
2. Vercel Docs: https://vercel.com/docs
3. Logs: Veja nos dashboards respectivos

---

**Boa sorte com o deploy!** 🚀
