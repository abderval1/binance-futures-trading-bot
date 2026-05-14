# 🏃‍♂️ COMO MANTER O BOT RODANDO 24/7

## 📡 Opção 1: Desktop (Windows) - Para Testes

Simples: abra PowerShell e rode os comandos. Funciona enquanto o PC estiver ligado.

```powershell
cd C:\Users\agostinho.rosario\Downloads\bot\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Para deixar rodando em segundo plano (sem bloquear terminal):**
```powershell
# Abra novo PowerShell (não feche o anterior!)
cd backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000"
```

---

## 🖥️ Opção 2: Serviço Windows (Recomendado para Produção)

Transforme o backend em serviço do Windows (inicia automaticamente):

### Usando NSSM (Non-Sucking Service Manager)

1. Baixe: https://nssm.cc/download/nssm-2.24.zip
2. Extraia em `C:\nssm`
3. Abra PowerShell como **Administrador**

```powershell
# Instalar serviço
C:\nssm\nssm.exe install BinanceTradingBot "C:\Users\agostinho.rosario\Downloads\bot\backend\venv\Scripts\uvicorn.exe"
# Arguments:
# app.main:app --reload --host 0.0.0.0 --port 8000

# Abra o NSSM GUI para configurar:
# - Path: C:\Users\...\uvicorn.exe
# - Arguments: app.main:app --reload --host 0.0.0.0 --port 8000
# - Startup directory: C:\Users\...\bot\backend
# - Environment: adicione PATH com venv\Scripts

# Iniciar serviço
Start-Service BinanceTradingBot

# Verificar status
Get-Service BinanceTradingBot

# Parar
Stop-Service BinanceTradingBot
```

---

## ☁️ Opção 3: VPS (Linux) - Para Produção Real

### Ubuntu 22.04 Exemplo

```bash
# 1. Conecte no servidor
ssh root@seu-servidor-ip

# 2. rode o install.sh automatico
curl -fsSL https://raw.githubusercontent.com/YOUR_USER/binance-futures-bot/main/install.sh | sudo bash

# 3. Configure .env
nano /opt/trading-bot/backend/.env
# Cole suas chaves Binance

# 4. Inicie
cd /opt/trading-bot
docker-compose -f docker-compose.prod.yml up -d

# 5. Verifique
docker-compose ps
docker-compose logs -f backend
```

Serviços sobem automaticamente com Docker.

---

## 🐳 Opção 4: Docker (Mais Fácil em Qualquer Lugar)

Se Docker Desktop instalado no Windows:

```powershell
cd C:\Users\agostinho.rosario\Downloads\bot

# Build e start (primeira vez)
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose logs -f backend

# Parar
docker-compose down

# Reiniciar
docker-compose -f docker-compose.prod.yml restart
```

**Vantagem:** Tudo em containers, fácil de migrar.

---

## 📊 Monitoramento

### Health Check automático
```powershell
# A cada 1 minuto
while ($true) {
    try {
        $r = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 5
        Write-Host "$(Get-Date): [OK] $($r.Content)"
    } catch {
        Write-Host "$(Get-Date): [FAIL] Bot offline!" -ForegroundColor Red
        # Envia alerta (email, telegram, etc)
    }
    Start-Sleep -Seconds 60
}
```

### Logs em arquivo
Se usar `uvicorn` diretamente, logs vão para console. Para salvar:

```powershell
uvicorn app.main:app --reload 2>&1 | Tee-Object -FilePath bot.log
```

Ou configure `logging.py` para escrever em arquivo também.

---

## 🔄 Auto-Restart em Caso de Crash

### Windows Task Scheduler (ou use serviço NSSM)
Crie tarefa que verifica se processo está rodando e reinicia.

### Linux (systemd)
```bash
# /etc/systemd/system/trading-bot.service
[Unit]
Description=Binance Trading Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/trading-bot/backend
Environment="PATH=/opt/trading-bot/backend/venv/bin"
ExecStart=/opt/trading-bot/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

---

## 🚨 Alertas

Configure notificação se o bot cair:

**UptimeRobot (grátis):**
- https://uptimerobot.com
- Monitor: http://localhost:8000/health
- Alerta por email/SMS se offline > 5 min

**Telegram Bot:**
```python
# Adicione em main.py ou trading engine
import requests
def send_telegram(msg):
    requests.get(f"https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>&text={msg}")
```

---

## 📈 Escalando

### Múltiplos Workers (Uvicorn)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
Cada worker é um processo separado. Use apenas se tiver múltiplos CPUs.

### Load Balancer (Vários servidores)
```
[User] → [Load Balancer (nginx)] → [Server 1] [Server 2] [Server 3]
```
Cada server tem seu próprio banco? Não, compartilham PostgreSQL central.

---

## 🗄️ Backup Automático

### Windows Task Scheduler
```powershell
# backup.ps1
pg_dump -U bot_user binance_bot | Out-File "C:\backups\bot_$(Get-Date -Format yyyyMMdd).sql"
Compress-Archive "C:\backups\bot_$(Get-Date -Format yyyyMMdd).sql" "C:\backups\bot_$(Get-Date -Format yyyyMMdd).zip"
Remove-Item "C:\backups\bot_*.sql" -Force
```

Agende diário às 02:00.

### Linux (crontab - já no install.sh)
```bash
0 2 * * * /opt/trading-bot/backup.sh
```

---

## 🛠️ Manutenção

### Atualizar código
```powershell
cd C:\Users\agostinho.rosario\Downloads\bot
git pull origin main

cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Reinicie o servidor

cd ../frontend
npm install
npm run build  # se usar Docker, rebuild imagem
```

### Verificar logs
```powershell
# Windows: se usar NSSM, logs em %NSSM%
# Ou se redirecionou para arquivo:
Get-Content bot.log -Tail 50 -Wait
```

### Limpar logs antigos
```powershell
Get-ChildItem *.log | Where-Object LastWriteTime -lt (Get-Date).AddDays(-7) | Remove-Item
```

---

## 🎯 Checklist "Bot está funcionando?"

Todo dia, verifique:

- [ ] Serviço rodando (porta 8000 aberta)
- [ ] Health check retorna `{"status":"healthy"}`
- [ ] Logs sem erros recentes
- [ ] Posições sincronizando (tabela atualizada)
- [ ] API keys ativas (não revogadas)
- [ ] Saldo suficiente nas contas
- [ ] stop-loss sendo respeitado
- [ ] Sem ordens pendentes presas
- [ ] Backup do dia anterior executed

---

## 🆘 Emergência

### Bot fazendo trades errados?
```powershell
# 1. Pare o bot imediatamente (Ctrl+C)
# 2. Revogue a API key no painel (ou Delete via API)
# 3. Feche todas as posições manualmente no Binance
# 4. Investigar logs
```

### Servidor caiu?
```powershell
# Reinicie o serviço
Restart-Service BinanceTradingBot

# Se não for serviço, abra PowerShell e rode de novo
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Banco corrompido?
```powershell
cd backend
# Backup do .db atual
Copy-Item trading_bot.db trading_bot.db.backup

# Recrie
Remove-Item trading_bot.db
python -c "from app.database import engine, Base; from app import models; Base.metadata.create_all(bind=engine)"
# Recrie admin se necessário
python create_admin.py
```

---

## 📞 Contatos de Emergência

- **Binance Support:** https://www.binance.com/en/support
- **Hacked?** Revoke keys immediately + change all passwords
- **Server Issues:** Contrate hosting com suporte 24/7 (DigitalOcean, AWS)

---

**Lembre-se:** Você é responsável pelo bot. Monitore diariamente. Comece com valores pequenos.

Boa sorte! 🚀
