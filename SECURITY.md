# 🔐 SEGURANÇA - CHECKLIST OBRIGATÓRIA

## CRÍTICO: Chaves Ex postas

Você compartilhou chaves no chat. Ação imediata:

1. **Binance:** Revogue as chaves expostas
2. **GitHub:** Revogue token antigo, crie novo
3. **NUNCA** use token exposto

---

## MELHORES PRÁTICAS

- API keys: Trade-only, Withdrawal OFF
- Senhas: únicas, 2FA habilitado
- Banco: senha forte, backups diários
- Servidor: firewall, fail2ban, updates
- HTTPS obrigatório em produção

---

## GERAÇÃO DE SECRETS

```python
import secrets, os
print(secrets.token_hex(32))  # SECRET_KEY
print(os.urandom(32).hex())   # ENCRYPTION_KEY
```

---

## ARMAZENAMENTO

- `.env` no .gitignore (nunca commitar)
- Usar secrets manager em produção
- Rotacionar chaves periodicamente
