#!/bin/bash
# Complete setup script for Ubuntu 22.04+

set -e

echo "=========================================="
echo "Binance Futures Bot - Auto Installer"
echo "=========================================="
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "→ Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install dependencies
echo "→ Installing dependencies..."
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    docker.io \
    docker-compose \
    git \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    ufw

# Start services
echo "→ Starting services..."
systemctl start postgresql
systemctl start redis
systemctl enable postgresql redis

# Create app user
echo "→ Creating bot user..."
useradd -m -s /bin/bash botuser || true
usermod -aG docker botuser

# Setup PostgreSQL database
echo "→ Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE USER bot_user WITH PASSWORD '$(openssl rand -base64 32)';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE binance_bot OWNER bot_user;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE binance_bot TO bot_user;"

# Clone repository
echo "→ Cloning repository..."
if [ ! -d "/opt/trading-bot" ]; then
    git clone https://github.com/YOUR_USERNAME/binance-futures-bot.git /opt/trading-bot
    chown -R botuser:botuser /opt/trading-bot
fi

# Setup backend
echo "→ Setting up backend..."
cd /opt/trading-bot/backend
sudo -u botuser python3.11 -m venv venv
sudo -u botuser venv/bin/pip install -r requirements.txt

# Copy environment
if [ ! -f ".env" ]; then
    cp .env.prod.example .env
    echo "⚠️  EDIT /opt/trading-bot/backend/.env with your actual values!"
fi

# Create SSL directory
mkdir -p /opt/trading-bot/ssl

# Setup nginx
echo "→ Configuring nginx..."
cp /opt/trading-bot/nginx/nginx.prod.conf /etc/nginx/nginx.conf
# Get SSL certificate (needs domain)
# certbot --nginx -d yourdomain.com

# Enable firewall
echo "→ Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Setup fail2ban
echo "→ Setting up fail2ban..."
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
maxretry = 3

[nginx-http-auth]
enabled = true
maxretry = 5

[nginx-limit-req]
enabled = true
maxretry = 10
EOF
systemctl restart fail2ban

# Create backup script
cat > /opt/trading-bot/backup.sh <<'SCRIPT'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U bot_user binance_bot | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Backup uploads/config
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" /opt/trading-bot/backend/.env

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
SCRIPT
chmod +x /opt/trading-bot/backup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/trading-bot/backup.sh") | crontab -

echo ""
echo "=========================================="
echo "✓ Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit /opt/trading-bot/backend/.env with real values"
echo "2. Initialize DB: cd /opt/trading-bot/backend && sudo -u botuser venv/bin/python setup.py"
echo "3. Get SSL cert: certbot --nginx -d yourdomain.com"
echo "4. Start services: docker-compose -f /opt/trading-bot/docker-compose.prod.yml up -d"
echo ""
echo "Services:"
echo "  Frontend:  https://yourdomain.com"
echo "  Backend:   https://api.yourdomain.com"
echo "  API Docs:  https://api.yourdomain.com/docs"
echo ""
