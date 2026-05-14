# Contributing to Binance Futures Trading Bot

Thank you for your interest in contributing! This is a commercial SaaS project. Please follow these guidelines.

---

## 🎯 How to Contribute

### Reporting Bugs
Before creating an issue:
1. Check existing issues (https://github.com/YOUR_USERNAME/binance-futures-bot/issues)
2. Ensure you're on latest version
3. Gather:
   - OS & versions (Python, Node, PostgreSQL)
   - Logs (redact secrets!)
   - Steps to reproduce
   - Expected vs actual behavior

Create issue with:
```
Title: [Bug] Brief description

Environment:
- OS: Ubuntu 22.04
- Python: 3.11.4
- Node: 18.17
- PostgreSQL: 15.3

Steps to Reproduce:
1. Add API key
2. Place market order
3. See error

Expected:
Order should fill

Actual:
Error 400: Invalid signature

Logs:
[PASTE LOGS HERE - NO SECRETS!]
```

### Suggesting Features
- Check if already planned in BUSINESS.md
- Describe use case (who benefits?)
- Consider technical feasibility
- Acceptance criteria: what does "done" look like?

### Pull Requests
1. Fork repository
2. Create feature branch: `git checkout -b feat/amazing-feature`
3. Make changes + tests
4. Run linters: `pylint app/` (backend), `npm run lint` (frontend)
5. Commit: `git commit -m "feat: add Bollinger Bands strategy"`
6. Push: `git push origin feat/amazing-feature`
7. Open PR against `main` branch
8. Fill PR template completely

---

## 🛠️ Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
# Install pre-commit hooks (optional)
pre-commit install
# Run
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Database
```bash
# PostgreSQL must be running
createdb binance_bot
python setup.py  # creates tables
```

---

## 📝 Code Style

### Python (PEP 8)
- 4 spaces indentation
- Max line length 100
- Type hints for all functions
- Docstrings for public functions/classes (Google style)
- Naming: `snake_case` for functions/vars, `PascalCase` for classes

Example:
```python
def calculate_position_size(
    entry_price: float,
    stop_loss: float,
    risk_percent: float
) -> float:
    """Calculate position size based on risk percentage.

    Args:
        entry_price: Entry price in USDT
        stop_loss: Stop loss price
        risk_percent: Risk per trade (e.g., 1.0 for 1%)

    Returns:
        Position size in base asset quantity
    """
    pass
```

### TypeScript/React
- Use functional components + hooks
- Props interfaces required
- 2 spaces indentation
- Semicolons optional (ESLint will enforce)
- Named exports over default

Example:
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick: () => void;
}

export function Button({ variant = 'primary', children, onClick }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

Currently minimal tests. PRs adding tests welcome!

### Frontend
```bash
cd frontend
npm test
```

---

## 🔀 Branching Strategy

```
main          - Production-ready (protected)
develop       - Integration branch (latest development)
feature/xxx  - New feature (from develop)
hotfix/xxx   - Critical bug fix (from main)
release/v1.1 - Release prep (from develop, to main + develop)
```

### Workflow
1. `git checkout develop`
2. `git pull origin develop`
3. `git checkout -b feature/my-feature`
4. Code + commit
5. `git push origin feature/my-feature`
6. Open PR → `develop`
7. After review & CI passes → merge
8. `git checkout develop && git pull`

---

## 📋 PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated (README, code comments)
- [ ] CHANGELOG.md updated
- [ ] No hardcoded secrets
- [ ] Lints pass (`pylint`, `eslint`)
- [ ] Type checking passes (`mypy`, `tsc`)
- [ ] Docker builds successfully
- [ ] Does not break existing functionality
- [ ] Follows project's code style

---

## 🏗️ Architecture Principles

When adding features:
1. **Security first** - never expose keys, validate inputs
2. **Multi-tenant awareness** - always scope queries by user_id
3. **Error handling** - meaningful messages, log details
4. **Async** - use async/await for I/O operations
5. **Cache when possible** - Redis for frequent reads
6. **Idempotency** - orders should be repeatable safely
7. **Observability** - add logs, metrics for business logic

---

## 📊 Submitting Strategy Ideas

Strategy template (`backend/app/trading/strategies.py`):
```python
class MyStrategy(BaseStrategy):
    """1-line description"""

    async def on_tick(self, data: Dict):
        """Called with latest market data"""
        # Your logic here
        # Return: None (no action) or place orders
        pass
```

Submit:
1. Strategy name & description
2. Parameters (configurable)
3. Expected markets (BTCUSDT? ETHUSDT? All?)
4. Timeframes (1m, 5m, 1h?)
5. Backtest results (if available)
6. Risk parameters (stop-loss, take-profit logic)

---

## 🐛 Bug Bounty (Future)

We'll establish bug bounty program when funded.
For now: responsible disclosure appreciated.
Report security issues to: **security@yourdomain.com** (set up later)
- Do NOT open public GitHub issue for security bugs
- We'll respond within 48 hours
- Reward: $100-1000 depending on severity

---

## 📞 Communication

- **Issues:** GitHub Issues (non-urgent)
- **Discussions:** GitHub Discussions (questions)
- **Chat:** Discord/Telegram (future)
- **Email:** support@yourdomain.com (future)

**Do NOT**:
- DM maintainers on social media for support
- Email security issues to non-secure address
- Leak other users' data

---

## 📄 License

Proprietary - All rights reserved.
You may:
- Fork for personal use
- Submit PRs to upstream
- Deploy your own instance

You may NOT:
- Resell this code as-is
- Remove license notices
- Use trademarked names (Binance) for commercial promotion without permission
- Hold us liable for trading losses

See LICENSE.md (to be created with commercial license).

---

## 🙏 Thank You!

Every contribution—code, docs, bug reports—helps make this platform better for traders worldwide.

**Happy trading! 📈**
