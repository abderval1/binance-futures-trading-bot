# 🚀 EXECUTAR O BOT - GUIA RÁPIDO

## ✅ CONFIGURAÇÃO COMPLETA

Backend configurado:
- Dependências instaladas
- Banco SQLite criado
- Admin: admin@tradingbot.com / ChangeMeNow123!
- Secrets gerados

---

## 🎯 EXECUTAR

```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\backend
.\venv\Scripts\Activate.ps1
python start.py
```

Acesse: http://localhost:8000/docs

---

## ⚠️ ANTES DE USAR

1. Revogue chaves expostas (Binance + GitHub)
2. Adicione NOVAS chaves no backend/.env
3. Teste no Binance testnet primeiro

---

## 📂 ESTRUTURA

```
backend/.env         ← Coloque suas chaves Binance
backend/trading_bot.db
backend/start.py     ← Inicia servidor
frontend/            ← React dashboard
```

---

## 🧪 TESTE

```powershell
Invoke-WebRequest http://localhost:8000/health
```

---

## 📚 DOCS COMPLETAS

- GETTING-STARTED.md - Tutorial completo
- SECURITY.md - Checklist segurança
- DEPLOYMENT.md - Deploy produção
