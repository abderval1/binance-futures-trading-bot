# Trading Bot Documentation

## Architecture Overview

```
┌─────────────────┐
│   React Frontend │ ← Dashboard, Trading Panel
│   (Port 5173)   │
└────────┬────────┘
         │ HTTP/API
         ▼
┌─────────────────┐
│  FastAPI Backend │ ← Trading Engine, Users, API Keys
│  (Port 8000)    │
└────────┬────────┘
         │
         ├────────────┐
         │            ▼
         │   ┌──────────────┐
         │   │ PostgreSQL   │ ← Users, Keys, Trades, Positions
         │   └──────────────┘
         │
         │   ┌──────────────┐
         │   │    Redis     │ ← Caching, Queues
         │   └──────────────┘
         │
         ▼
┌─────────────────┐
│ Binance Futures │ ← Trading via REST API + WebSocket
│     API         │
└─────────────────┘
```

## Multi-Tenant Design

### Users & Roles
- **Admin**: Full access, unlimited keys, manage users
- **Trader**: Create API keys, execute trades, view analytics
- **Subscriber**: View-only or limited trading (tiered plans)

### Subscription Plans
| Plan | Max Accounts | Daily Trades | Price |
|------|-------------|--------------|-------|
| Basic | 2 | 100 | $29.99/mo |
| Pro | 5 | 500 | $79.99/mo |
| Enterprise | 20 | Unlimited | $299.99/mo |

### API Key Security
1. **Encryption at rest**: AES-256-GCM with per-key derived key
2. **Trade-only permissions**: Withdrawal disabled in Binance
3. **IP restrictions**: Recommended on Binance side
4. **No plaintext exposure**: Never logged or cached in plaintext

## Features

### Trading Engine
- Market orders (instant execution)
- Limit orders (pending execution)
- Stop-loss orders (risk management)
- Take-profit orders (automated exits)
- Position tracking & sync (10s intervals)
- Leverage & margin configuration (1-125x, Isolated/Cross)

### Dashboard
- Real-time P&L display
- Open positions table (symbol, side, entry, mark, quantity, P&L)
- Quick trade panel (one-click orders)
- API key management (add/remove/configure)
- Subscription status display

### Risk Management (Built-in)
- Position size calculation based on risk % (future enhancement)
- Automatic stop-loss placement (configurable)
- Automatic take-profit placement (configurable)
- Leverage limits per key

## Trading Strategies

### Built-in Strategies
1. **SMA Crossover**: Simple moving average cross signals
2. **Grid Trading**: Buy low, sell high on a price grid

### Adding Custom Strategies
```python
# backend/app/trading/strategies.py
class MyStrategy(BaseStrategy):
    async def on_tick(self, data):
        # Implement your logic
        pass
```

## Installation

### Quick Start (Docker)
```bash
# Clone & navigate
cd bot

# Start all services
docker-compose up -d

# Backend runs at http://localhost:8000
# Frontend runs at http://localhost:5173
```

### Manual Setup
See `backend/SETUP.md` and `frontend/SETUP.md`

## API Reference

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create account |
| `/api/auth/token` | POST | Login (OAuth2) |
| `/api/auth/me` | GET | Current user |

### API Keys
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/api-keys/` | GET | List your keys |
| `/api/api-keys/` | POST | Add new key |
| `/api/api-keys/{id}` | DELETE | Remove key |

### Trading
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trading/positions` | GET | List open positions |
| `/api/trading/balance/{key_id}` | GET | Get balance |
| `/api/trading/order` | POST | Place order |
| `/api/trading/close-position/{symbol}` | POST | Close position |

## Security Checklist

- [ ] Change default database credentials
- [ ] Generate strong SECRET_KEY (32+ chars)
- [ ] Generate strong ENCRYPTION_KEY (32 chars hex)
- [ ] Enable HTTPS in production (use nginx/Traefik)
- [ ] Set up firewall (allow only 80/443)
- [ ] Configure Binance API IP whitelist
- [ ] Enable withdrawal disabled on Binance keys
- [ ] Set up rate limiting (nginx or cloudflare)
- [ ] Enable audit logging
- [ ] Regular backups of database

## Troubleshooting

### "Could not validate credentials"
- Token expired (default 7 days) - login again
- Backend restarted - token invalidated

### "Binance API error"
- Check API key permissions (trade-only)
- Verify testnet/mainnet selection
- Check leverage settings (too high?)

### "Position not syncing"
- Verify API key is active
- Check Binance rate limits
- Review backend logs

### "Cannot place order"
- Insufficient margin/balance
- Symbol not in whitelist
- Price deviation too large (protections)

## Production Deployment

### Using Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Using VPS (Ubuntu)
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Clone repo
git clone <your-repo>
cd bot

# Create .env with production values
cp backend/.env.prod.example backend/.env
# Edit backend/.env with real values

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Using Kubernetes
```bash
kubectl apply -f k8s/
```

## Support
- Issues: Submit GitHub issues
- Security: security@yourdomain.com
