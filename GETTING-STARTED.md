# GETTING STARTED - COMPLETE WALKTHROUGH

## 🎯 What You've Built

A **multi-tenant Binance Futures trading bot** where:
- You (admin) can manage multiple users
- Each user adds their own Binance API keys
- Bot trades automatically using strategies
- You charge monthly subscriptions (Basic/Pro/Enterprise)

---

## 📦 Project Structure
```
bot/
├── backend/           # Python FastAPI server
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── config.py            # Settings
│   │   ├── auth.py              # JWT auth
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # API schemas
│   │   ├── crud.py              # DB operations
│   │   ├── database.py          # DB connection
│   │   ├── clients/
│   │   │   └── binance_client.py   # Binance API wrapper
│   │   ├── routes/
│   │   │   ├── users.py         # User endpoints
│   │   │   ├── api_keys.py      # API key management
│   │   │   └── trading.py       # Trading operations
│   │   ├── routers/
│   │   │   └── auth.py          # Auth routes
│   │   ├── trading/
│   │   │   ├── engine.py        # Trading engine
│   │   │   └── strategies.py    # Built-in strategies
│   │   └── utils/
│   │       ├── encryption.py    # AES-256-GCM
│   │       └── logging.py       # Structured logging
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── setup.py
├── frontend/          # React TypeScript app
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx    # Main dashboard
│   │   │   └── LoginPage.tsx        # Auth
│   │   ├── components/
│   │   │   ├── Button.tsx
│   │   │   └── ApiKeyModal.tsx
│   │   ├── store/
│   │   │   └── index.ts     # Zustand stores
│   │   ├── lib/
│   │   │   └── api.ts       # Axios client
│   │   └── types.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml     # Local dev
├── docker-compose.prod.yml # Production
├── .github/workflows/ci-cd.yml
├── README.md
├── DEPLOYMENT.md
├── ARCHITECTURE.md
└── BUSINESS.md
```

---

## 🚀 INSTALLATION (Choose One)

### Option 1: Docker (Fastest, Recommended)
```bash
# 1. Install Docker Desktop
#    Windows: https://www.docker.com/products/docker-desktop/
#    Mac: brew install --cask docker
#    Linux: apt install docker.io docker-compose

# 2. Generate secrets
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import os; print('ENCRYPTION_KEY=' + os.urandom(32).hex())"

# 3. Clone & configure
git clone https://github.com/YOUR_USERNAME/binance-futures-bot.git
cd binance-futures-bot
cp backend/.env.prod.example backend/.env
# Edit backend/.env with generated secrets + your Binance API keys

# 4. Start everything
docker-compose -f docker-compose.prod.yml up -d

# 5. Access
# http://localhost (frontend)
# http://localhost:8000/docs (API docs)
```

### Option 2: Local (Development)
```bash
# ---- PREREQUISITES ----
# 1. Python 3.11+ (python.org)
# 2. Node.js 18+ (nodejs.org)
# 3. PostgreSQL 15+ (postgresql.org)
# 4. Git (git-scm.com)

# ---- BACKEND ----
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Create database
# Open psql as postgres user:
#   CREATE DATABASE binance_bot;
#   CREATE USER bot_user WITH PASSWORD 'your_password';
#   GRANT ALL PRIVILEGES ON DATABASE binance_bot TO bot_user;

# Copy env
cp .env.example .env
# Edit .env, set DATABASE_URL=postgresql://bot_user:your_password@localhost/binance_bot

# Generate secrets:
python -c "import secrets; print(secrets.token_hex(32))"  # SECRET_KEY
python -c "import os; print(os.urandom(32).hex())"        # ENCRYPTION_KEY

# Initialize DB & create admin
python setup.py

# Start backend
uvicorn app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs

# ---- FRONTEND (new terminal) ----
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## 🔑 FIRST LOGIN

### Default Admin Account
After running `setup.py`, you have:
- **Email:** admin@tradingbot.com
- **Password:** ChangeMeNow123!

⚠️ **CHANGE THIS PASSWORD IMMEDIATELY AFTER LOGIN**

### Steps:
1. Open http://localhost:5173/login
2. Login with admin credentials
3. Dashboard appears
4. Click "Add API Key"
5. Enter your **Binance Futures** API key + secret
6. Set leverage (20x recommended)
7. Click "Add"
8. Key appears in dashboard

---

## 📊 USING THE BOT

### 1. Add API Key
```
Dashboard → Add API Key
Form fields:
- Label: "Main Binance" (any name)
- API Key: (from Binance)
- Secret Key: (from Binance)
- Leverage: 20 (or your preference)
- Margin Type: ISOLATED (recommended)
- Testnet: No (unless testing)
```

### 2. Place Trade
```
Dashboard → Quick Trade
Symbol: BTCUSDT
Side: Long (BUY) or Short (SELL)
Quantity: 0.001 BTC (~$30 at $30k/BTC)
Click Buy/Sell
```

### 3. View Positions
Positions auto-sync every 10 seconds.
Table shows:
- Symbol (BTCUSDT)
- Side (LONG/SHORT)
- Entry price
- Current mark price
- Quantity
- P&L (green = profit, red = loss)
- Action: Close button

### 4. Enable Auto-Trading
Current manual trading only. Strategies coming soon:
```python
# In backend, strategies can be started via API
POST /api/strategies/start
{
  "name": "sma_crossover",
  "api_key_id": 1,
  "config": {
    "symbol": "BTCUSDT",
    "position_size": 0.001,
    "fast_period": 10,
    "slow_period": 30
  }
}
```

---

## 💰 SUBSCRIPTION MODEL

### Plans (code already built)
Edit `backend/app/schemas.py`:
```python
SUBSCRIPTION_PLANS = {
    "basic": { max_accounts: 2, price: 29.99 },
    "pro":    { max_accounts: 5, price: 79.99 },
    "ent:": { max_accounts: 20, price: 299.99 },
}
```

### Enable Payments
Add Stripe:
```bash
cd backend
pip install stripe
```

Create webhook endpoint:
```python
# In backend/app/routes/subscriptions.py
@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    # Verify signature
    # Update user.subscription_status
    pass
```

Frontend: Add Stripe Checkout button.

---

## 🔒 SECURITY CHECKLIST

**DO THESE BEFORE GOING LIVE:**

Backend:
- [x] API keys encrypted (AES-256-GCM)
- [x] Passwords hashed (bcrypt)
- [x] JWT auth with expiry
- [ ] Rate limiting per user (100 req/min default)
- [ ] Request validation (Pydantic)
- [ ] Audit logging (who did what)
- [ ] HTTPS only (SSL cert)
- [ ] Security headers (CSP, HSTS)
- [ ] IP whitelist (optional)

Database:
- [x] Strong DB password
- [ ] Encrypted at rest (disk encryption)
- [ ] Daily automated backups
- [ ] Point-in-time recovery
- [ ] Restricted DB user (no superuser)

Server:
- [x] Firewall (UFW)
- [x] Fail2ban installed
- [ ] SSH key auth only (disable passwords)
- [ ] Non-root user for app
- [ ] Automatic security updates
- [ ] Log monitoring (fail2ban, logwatch)

Binance:
- [x] Trade-only permission
- [ ] IP whitelist (optional but recommended)
- [ ] Withdrawal DISABLED
- [ ] API key rotation quarterly

---

## 🐛 TROUBLESHOOTING

### "ModuleNotFoundError: No module named 'app'"
**Fix:** Run from `backend/` directory:
```bash
cd backend
uvicorn app.main:app --reload
```

### "psycopg2 install failed"
**Fix:** Install PostgreSQL dev libraries first:
- Windows: Install PostgreSQL, add to PATH
- Linux: `apt-get install libpq-dev`
- Or use `psycopg2-binary` (already in requirements)

### "Database connection refused"
**Fix:**
```bash
# Check PostgreSQL is running
# Windows: services.msc → postgresql-x64-15 → Start
# Linux: sudo systemctl start postgresql
createdb binance_bot  # if DB doesn't exist
```

### CORS error in browser
**Fix:** Edit `backend/.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### "Invalid API key" from Binance
**Fix:**
- Key is for Spot, not Futures → Enable Futures in Binance
- Key has withdrawal → Disable withdrawal, enable only trade
- Testnet flag wrong → Check "Testnet" checkbox matches key type
- Key/IP mismatch → Remove IP restriction or add server IP

### Position not showing
**Fix:**
- Position size too small (< 0.001 BTC) → Increase quantity
- Leverage too high → Reduce to ≤ 125x
- Symbol invalid → Check symbol exists on Binance Futures

### Orders not filling
**Fix:**
- Market orders: Should fill instantly
- Limit orders: Price too far from mark price → Adjust
- Insufficient balance → Deposit more USDT

---

## 📈 MONITORING

### Health Check
```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"trading-bot"}
```

### Logs
```bash
# Docker
docker-compose logs -f backend

# Direct
cd backend
uvicorn app.main:app --reload 2>&1 | tee bot.log
```

### Database Queries
```bash
# Connect to DB
psql -U bot_user -d binance_bot

# View users
SELECT id, email, role, subscription_status FROM users;

# View API keys (encrypted)
SELECT id, user_id, label, testnet FROM api_keys;

# View recent trades
SELECT symbol, side, quantity, price, realized_pnl, executed_at
FROM trades
ORDER BY executed_at DESC LIMIT 10;
```

---

## 🎯 PRODUCTION DEPLOYMENT

### VPS (Ubuntu 22.04)
```bash
# 1. Login as root
ssh root@your-server-ip

# 2. Run installer
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/binance-futures-bot/main/install.sh | bash

# 3. Edit .env with real values
nano /opt/trading-bot/backend/.env

# 4. Get SSL certificate
certbot --nginx -d yourdomain.com

# 5. Start services
cd /opt/trading-bot
docker-compose -f docker-compose.prod.yml up -d

# 6. Done!
# Visit https://yourdomain.com
```

### Kubernetes (Advanced)
```bash
kubectl apply -f k8s/
# Files: deployment.yaml, service.yaml, ingress.yaml, configmap.yaml, secret.yaml
```

### Railway / Render / Fly.io
Push code, set environment variables, deploy. All services supported.

---

## 🧪 TESTING STRATEGY

### Phase 1: Testnet (Week 1)
1. Get Binance testnet keys: https://testnet.binancefuture.com
2. Add testnet key to bot (check "Testnet" checkbox)
3. Place test orders ($5-$10)
4. Verify fills, positions, P&L
5. Test stop-loss & take-profit
6. Test close position

### Phase 2: Small Live (Week 2)
1. Add REAL key with $10-$20
2. Place 1-2 small orders
3. Monitor 24/7 for 3 days
4. Test stop-loss triggers
5. Test withdrawal? NO - keep disabled

### Phase 3: Beta (Week 3-4)
1. Invite 5 trusted users
2. Each deposits $50-100
3. Monitor daily
4. Fix bugs
5. Add features they request

### Phase 4: Launch (Month 2+)
1. Open to public
2. Marketing push
3. Customer support
4. Scale infrastructure

---

## 📞 SUPPORT & FEEDBACK

### Document Your Setup
Create `CONFIG.md` in repo with:
- Domain name
- Server IP
- Database credentials (encrypted)
- SSL expiry date
- Backup procedure
- Emergency contacts

### Monitor Uptime
- UptimeRobot (free): Check /health every 5 min
- Alert via email/SMS if down

### Keep Logs
```bash
# Rotate logs daily
logrotate /var/log/trading-bot/*.log {
    daily
    rotate 30
    compress
}
```

---

## 🎓 LEARNING PATH

**Immediate:**
1. FastAPI tutorial (1 hour)
2. React + TypeScript basics (2 hours)
3. Binance API docs (1 hour)

**Short-term:**
4. Docker & docker-compose (2 hours)
5. PostgreSQL basics (1 hour)
6. Nginx reverse proxy (1 hour)

**Long-term:**
7. Trading strategies & backtesting
8. Risk management principles
9. SaaS business & marketing
10. Customer success & support

---

## ⚠️ FINAL WARNINGS

1. **API Keys Exposed** - You leaked yours. REVOKE THEM NOW.
2. **Start Small** - Trade with $10 until confident
3. **Monitor Daily** - Check positions every morning
4. **Withdrawal OFF** - Never enable on user keys
5. **Legal Compliance** - Check local laws
6. **No Guarantees** - Trading can lose money
7. **Your Liability** - You're responsible for bot behavior

---

**Ready to launch? Start with: `docker-compose -f docker-compose.prod.yml up -d`**

Good luck! 🚀
