# Binance Futures Trading Bot
Multi-tenant subscription-based trading platform

## ⚠️ SECURITY WARNING

**API keys are NEVER stored in plain text or committed to git.**

1. **REVOKE compromised keys immediately** on Binance
2. Use IP-restricted API keys (trade-only, no withdrawal)
3. Store keys encrypted in database (AES-256-GCM)
4. Use `.env` for configuration - never commit secrets

## Setup

### Backend (Python + FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React + Vite + TypeScript)
```bash
cd frontend
npm install
npm run dev
```

## Architecture
- `backend/` - FastAPI REST API + Trading Engine
- `frontend/` - React TypeScript dashboard
- PostgreSQL + SQLAlchemy for data
- Redis for caching/queues
- JWT auth + role-based access (admin/trader/subscriber)
