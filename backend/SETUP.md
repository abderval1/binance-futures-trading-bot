# Backend Setup

## 1. Install Dependencies
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Database Setup
```bash
# Install PostgreSQL (if not installed)
# Then create database:
createdb binance_bot
```

## 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your values:
# - DATABASE_URL (PostgreSQL connection)
# - SECRET_KEY (32+ random chars)
# - ENCRYPTION_KEY (32 chars for AES)
# - BINANCE_API_KEY/SECRET_KEY (for master account)
```

## 4. Generate Secrets
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Use output for SECRET_KEY
python -c "import os; print(os.urandom(32).hex())"
# Use output for ENCRYPTION_KEY
```

## 5. Run Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints
- `POST /api/auth/token` - Login
- `POST /api/auth/register` - Register
- `GET  /api/auth/me` - Current user
- `GET  /api/api-keys/` - List API keys
- `POST /api/api-keys/` - Add API key
- `DELETE /api/api-keys/{id}` - Remove key
- `POST /api/trading/order` - Place order
- `GET  /api/trading/positions` - Get positions
- `POST /api/trading/close-position/{symbol}` - Close position
- `GET  /api/trading/balance/{api_key_id}` - Get balance

## Security Notes
1. **NEVER commit `.env`** - It's in .gitignore
2. Use IP-restricted Binance keys (trade-only)
3. Keys encrypted at rest (AES-256-GCM)
4. HTTPS required in production
5. Enable firewall rules for database
