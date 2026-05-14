# 🚀 EXECUTAR O BOT - GUIA PASSO-A-PASSO

## ✅ CONFIGURAÇÃO COMPLETA (FEITA)

O backend está **totalmente configurado**:
- ✅ Dependências instaladas
- ✅ Banco SQLite criado (`backend/trading_bot.db`)
- ✅ Usuário admin: `admin@tradingbot.com` / `ChangeMeNow123!`
- ✅ Secret keys geradas (SECRET_KEY, ENCRYPTION_KEY)
- ✅ Testes de importação passaram

---

## 🎯 EXECUTAR AGORA (Windows PowerShell)

### Passo 1: Abrir PowerShell
1. Pressione `Win + X` → "Windows PowerShell"
2. Ou clique Iniciar → digite "PowerShell" → abra

### Passo 2: Navegar até o projeto
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\backend
```

### Passo 3: Ativar ambiente virtual
```powershell
.\venv\Scripts\Activate.ps1
```
**Verifique:** O prompt deve mudar, mostrando `(venv)` no início.

### Passo 4: Iniciar o servidor
```powershell
python start.py
```
OU
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 O QUE VOCÊ VERÁ

Se der certo, aparecerá isso:

```
INFO:     Will watch for changes in these directories: ['C:\...\bot\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**NÃO feche esta janela!** Ela deve ficar aberta rodando o servidor.

---

## 🌐 TESTAR SE ESTÁ FUNCIONANDO

Abra **outro** PowerShell (não feche o primeiro!) e execute:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

**Resposta esperada:**
```
Content : {"status":"healthy","service":"trading-bot"}
```

Se funcionou, o bot está vivo!

---

## 📚 ACESSAR A API DOCUMENTADA

Abra no navegador:
```
http://localhost:8000/docs
```

Você verá a interface Swagger para testar os endpoints:
- POST `/auth/token` - Login
- GET `/auth/me` - Current user
- GET `/api-keys/` - List keys
- POST `/api-keys/` - Add key
- etc.

---

## 🖥️ FRONTEND (Dashboard Visual)

Para a interface React:

### Se ainda não tem Node.js:
1. Baixe: https://nodejs.org/en/download/ (Windows Installer .msi)
2. Instale (next, next, finish)
3. Abra **novo** PowerShell

### Iniciar frontend:
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\frontend
npm install
npm run dev
```

Acesse: **http://localhost:5173**

---

## 🔑 ADICIONAR SUA CHAVE BINANCE (IMPORTANTE!)

Antes de usar, **Edite o arquivo `.env`**:

```
C:\Users\agostinho.rosario\Downloads\bot\backend\.env
```

Encontre estas linhas:
```
BINANCE_API_KEY=YOUR_NEW_BINANCE_API_KEY_HERE
BINANCE_SECRET_KEY=YOUR_NEW_BINANCE_SECRET_HERE
```

**Substitua** pelas suas **novas** chaves do Binance (as antigas foram comprometidas - REVOGUE!).

Salve o arquivo.

**Reinicie o servidor** (Ctrl+C no PowerShell e execute `uvicorn...` novamente).

---

## 🧪 TESTE RÁPIDO (TESTNET RECOMENDADO)

1. Crie uma chave no **Binance Testnet**: https://testnet.binancefuture.com
2. No dashboard (frontend), adicione esta chave marcando "Testnet"
3. Faça uma ordem de teste:
   - Symbol: `BTCUSDT`
   - Side: `Long`
   - Quantity: `0.001`
4. Verifique se a posição aparece na tabela

---

## 📂 ESTRUTURA DE ARQUIVOS RELEVANTES

```
bot/
├── backend/
│   ├── start.py                   ← Script para iniciar
│   ├── .env                       ← COLOQUE SUAS CHAVES AQUI
│   ├── trading_bot.db             ← Banco (criado)
│   ├── venv/                      ← Ambiente Python
│   └── app/
│       ├── main.py               ← API
│       ├── trading/engine.py     ← Engine de trading
│       └── ...
├── frontend/
│   ├── src/
│   └── package.json
├── GETTING-STARTED.md            ← Tutorial completo
├── SECURITY.md                  ← Segurança (LEIA!)
├── DEPLOYMENT.md               ← Deploy produção
└── QUICKSTART.md              ← Este resumo
```

---

## 🐛 SE NÃO FUNCIONAR

### Erro: "uvicorn não é reconhecido"
**Solução:** Certifique-se de ativar o venv primeiro:
```powershell
.\venv\Scripts\Activate.ps1
```
O prompt deve mostrar `(venv)`.

### Erro: "Port 8000 already in use"
**Solução:** Altere a porta ou mate o processo:
```powershell
# Veja quem está usando a porta 8000
netstat -ano | findstr :8000
# Mate o processo (substitua PID pelo número)
taskkill /PID PID_AQUI /F
```

### Erro ao importar módulos
**Solução:** Reinstale dependências:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erro no banco de dados
**Solução:** Recrie o banco:
```powershell
cd backend
Remove-Item trading_bot.db -Force
python -c "from app.database import engine, Base; from app import models; Base.metadata.create_all(bind=engine)"
python create_admin.py
```

---

## 📊 VERIFICAR ESTÁ TUDO OK

Execute o script de teste:
```powershell
cd backend
python test_setup.py
```

**Saída esperada:**
```
[OK] Config loaded
[OK] Database configured
[OK] Auth functions OK
[OK] Binance client OK
[OK] Trading engine OK
[OK] Database connection OK
[OK] Admin user exists
[OK] ALL CHECKS PASSED
```

---

## 🎯 FLUXO COMPLETO RECOMENDADO

1. **Revogar** chaves expostas (Binance + GitHub) - URGENTE
2. **Criar** novas chaves Binance (Futures, Trade-only, No withdrawal)
3. **Editar** `backend/.env` com novas chaves
4. **Iniciar** backend: `uvicorn app.main:app --reload --port 8000`
5. **Testar** health: http://localhost:8000/health
6. **Abrir** docs: http://localhost:8000/docs
7. **Instalar** Node.js (se não tiver)
8. **Iniciar** frontend: `npm run dev` na pasta frontend
9. **Login** no dashboard: admin@tradingbot.com / ChangeMeNow123!
10. **Adicionar** chave API Binance (no dashboard)
11. **Testar** ordem no testnet (0.001 BTC)
12. **Monitorar** posições por 24h

---

## 📞 DIFICULDADES?

- **GETTING-STARTED.md** - Tutorial detalhado
- **SECURITY.md** - Checklist segurança
- **DEPLOYMENT.md** - Como deploy em servidor

---

## ✅ PRONTO!

O bot está configurado e **pronto para executar**. 

**Agora é só abrir PowerShell e digitar:**
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\backend
.\venv\Scripts\Activate.ps1
python start.py
```

**Boa sorte!** 🚀
