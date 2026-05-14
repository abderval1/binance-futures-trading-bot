# Quick Deployment Guide

## Step 1: Revoke Compromised Keys (URGENT)

### Binance API Keys
1. Login to Binance → API Management
2. Revoke keys with these hashes:
   - `hhapMI60dNo7jpz0l88jIVqjD5vYLWOR9aj4zYe9pRzOA6Rk6hcJnTUdPIBE4Qu5`
   - `0wRxDRCspYTIiNSVpXu85aef4d2FwEoKtccGPQ71X3cTH6k109THomIkrRGoFg2E`
3. Create NEW API keys:
   - Enable **Futures** permission
   - **Disable** Withdrawal
   - Enable **Trade-only**
   - (Optional) Restrict IP address

### GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Revoke: `SEU_TOKEN_AQUI` (o token que foi exposto)
3. Create new token:
   - Select `repo` scope
   - Copy token (you won't see it again)

---

## Step 2: Local Development Setup

### Backend
```bash
cd backend

# Create virtualenv
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
copy .env.example .env
# Edit .env:
# - DATABASE_URL=postgresql+psycopg2://user:pass@localhost/binance_bot
# - Generate SECRET_KEY: python -c "import secrets; print(secrets.token_hex(32))"
# - Generate ENCRYPTION_KEY: python -c "import os; print(os.urandom(32).hex())"
# - Add your Binance keys

# Initialize database
# Install PostgreSQL first (https://postgresql.org)
# Then: createdb binance_bot

# Run migrations (using alembic later)
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Opened at http://localhost:5173
```

---

## Step 3: Docker Deployment (Production)

```bash
# Clone repo (if not already)
git clone https://github.com/YOUR_USERNAME/binance-futures-bot.git
cd binance-futures-bot

# Create .env file
cp backend/.env.prod.example backend/.env
# Edit backend/.env with production values

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres
```

Services start:
- Backend API: http://localhost:8000
- Frontend: http://localhost:80 (nginx)
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Step 4: Testing the Bot

### 1. Register Account
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"YourPass123","full_name":"Your Name"}'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=YourPass123"
```
Save the `access_token` returned.

### 3. Add API Key (with your NEW Binance key)
```bash
curl -X POST "http://localhost:8000/api/api-keys/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Main Account",
    "api_key": "YOUR_NEW_BINANCE_API_KEY",
    "secret_key": "YOUR_NEW_BINANCE_SECRET",
    "leverage": 20,
    "margin_type": "ISOLATED",
    "testnet": false
  }'
```

### 4. Place Test Order (Testnet first!)
```bash
# Use testnet to verify everything works
curl -X POST "http://localhost:8000/api/trading/order?api_key_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 0.001
  }'
```

---

## Step 5: Set Up Subscription Plans

### Create Admin User (via Python shell)
```bash
cd backend
python -c "
from app.database import SessionLocal
from app import crud, schemas, auth
from app.database import get_db

db = SessionLocal()
admin = crud.create_user(db, schemas.UserCreate(
    email='admin@yourdomain.com',
    password='ChangeThisPassword123!',
    full_name='Admin'
))
admin.role = 'admin'
admin.subscription_status = 'active'
db.commit()
db.close()
print('Admin created!')
"
```

### Assign Plans to Users
```python
# In admin dashboard (future feature) or via SQL:
UPDATE users SET role='subscriber', subscription_status='active' WHERE id=2;
```

---

## Security Checklist (DO NOT SKIP)

- [ ] Revoked all exposed API keys (Binance + GitHub)
- [ ] Changed all passwords that used same password
- [ ] Generated new SECRET_KEY (32+ random chars)
- [ ] Generated new ENCRYPTION_KEY (32-byte hex)
- [ ] Created PostgreSQL user with strong password
- [ ] Configured firewall (ports 80, 443, 22 only)
- [ ] Set up SSL/TLS certificates (Let's Encrypt)
- [ ] Enabled fail2ban or similar intrusion prevention
- [ ] Configured log rotation
- [ ] Set up automated backups (daily)
- [ ] Enabled Cloudflare (DDoS protection + WAF)
- [ ] Restricted Binance API keys to specific IPs
- [ ] Enabled "Trade Only" on all Binance keys
- [ ] 2FA enabled on all admin accounts
- [ ] Regular security updates scheduled

---

## Environment Variables Reference

### Backend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| SECRET_KEY | Yes | JWT signing key (32+ chars) |
| ENCRYPTION_KEY | Yes | AES key for API encryption (32-byte hex) |
| REDIS_URL | No | Redis URL (optional) |
| BINANCE_API_KEY | No | Master Binance key (admin ops) |
| BINANCE_SECRET_KEY | No | Master Binance secret |
| APP_ENV | No | `development` or `production` |
| CORS_ORIGINS | Yes | Allowed frontend origins |

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
```bash
cd backend
python -c "import sys; print(sys.path)"  # Check current dir in path
# Ensure you're in backend/ when running uvicorn
```

### "psycopg2 install failed"
```bash
# Windows: Install PostgreSQL SDK first
# Or use psycopg2-binary (already in requirements)
pip install psycopg2-binary
```

### "Database connection refused"
```bash
# Check PostgreSQL is running
# Windows: services.msc → postgresql-x64-15
# Linux: sudo systemctl status postgresql
createdb binance_bot  # if DB doesn't exist
```

### CORS errors
Check `CORS_ORIGINS` in .env matches frontend URL (e.g., `http://localhost:5173`)

### "Invalid signature" from Binance
- API key/secret mismatch
- Keys not set for Futures trading
- Using testnet key on mainnet (or vice versa)

---

## Monitoring & Logs

### View Backend Logs
```bash
# Docker
docker-compose logs -f backend

# Direct
cd backend && uvicorn app.main:app --reload 2>&1 | tee bot.log
```

### Database Queries
```bash
docker-compose exec postgres psql -U bot_user -d binance_bot
# Inside psql:
SELECT * FROM users;
SELECT * FROM api_keys;
SELECT * FROM trades ORDER BY executed_at DESC LIMIT 10;
```

### Health Checks
```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"trading-bot"}
```

---

## Updating the Bot

```bash
git pull origin main

# Backend
cd backend
git pull
pip install -r requirements.txt
# Restart uvicorn (or docker-compose restart backend)

# Frontend
cd frontend
git pull
npm install
npm run build  # for production
```

---

## Support Resources

- Binance Futures Docs: https://binance-docs.github.io/apidocs/futures/en/
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev
- Security Best Practices: OWASP Top 10

---

**YOU ARE RESPONSIBLE FOR:**
1. Securing your own server/network
2. Managing API keys safely
3. Compliance with local regulations
4. Trading risks & losses
5. Regular backups

**BOT IS PROVIDED "AS IS" - USE AT YOUR OWN RISK**
