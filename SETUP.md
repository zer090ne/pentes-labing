# 🚀 Setup Guide - Pentest Lab Otomatis

Panduan lengkap untuk setup dan konfigurasi Pentest Lab Otomatis.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, atau Windows dengan WSL2
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 10GB free space
- **Network**: Akses internet untuk download dependencies

### Software Requirements
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: Version 2.0+
- **Python**: Version 3.11+ (untuk development)
- **Node.js**: Version 18+ (untuk development)

## 🐳 Docker Setup (Recommended)

### 1. Install Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS
# Download Docker Desktop dari https://www.docker.com/products/docker-desktop

# Windows
# Download Docker Desktop dari https://www.docker.com/products/docker-desktop
```

### 2. Install Docker Compose
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker compose version
```

### 3. Clone Repository
```bash
git clone <repository-url>
cd pentes-labing
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env
```

**Konfigurasi penting di .env:**
```bash
# Security - GANTI INI!
SECRET_KEY=your-very-secure-secret-key-here

# Database
DATABASE_URL=postgresql://pentest:password@postgres:5432/pentest_lab

# VM Network (sesuaikan dengan setup VirtualBox Anda)
KALI_VM_IP=192.168.56.10
METASPLOITABLE_VM_IP=192.168.56.20
VM_NETWORK=192.168.56.0/24
```

### 5. Start Services
```bash
# Build dan start semua services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 6. Initialize Database
```bash
# Run database migrations
docker compose exec backend alembic upgrade head

# Create admin user (optional)
docker compose exec backend python -c "
from app.services.auth_service import AuthService
from app.core.database import SessionLocal
from app.schemas.user import UserCreate

db = SessionLocal()
auth_service = AuthService(db)

user_data = UserCreate(
    username='admin',
    email='admin@pentestlab.local',
    password='admin123'
)

user = auth_service.create_user(user_data)
print(f'Admin user created: {user.username}')
"
```

## 🖥️ Manual Setup (Development)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install pentest tools
sudo apt-get update
sudo apt-get install nmap nikto hydra sqlmap gobuster

# Setup database
createdb pentest_lab
# atau
mysql -u root -p -e "CREATE DATABASE pentest_lab;"

# Run migrations
alembic upgrade head

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Database Setup

#### PostgreSQL
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database dan user
sudo -u postgres psql
CREATE DATABASE pentest_lab;
CREATE USER pentest WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE pentest_lab TO pentest;
\q
```

#### MySQL (Alternative)
```bash
# Install MySQL
sudo apt-get install mysql-server

# Create database dan user
sudo mysql
CREATE DATABASE pentest_lab;
CREATE USER 'pentest'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON pentest_lab.* TO 'pentest'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
```

## 🔧 VM Configuration

### VirtualBox Setup

1. **Install VirtualBox**
```bash
# Ubuntu/Debian
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
echo "deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list
sudo apt-get update
sudo apt-get install virtualbox-6.1
```

2. **Download VM Images**
```bash
# Kali Linux
wget https://cdimage.kali.org/kali-2023.3/kali-linux-2023.3-virtualbox-amd64.ova

# Metasploitable2
wget https://sourceforge.net/projects/metasploitable/files/Metasploitable2/metasploitable-linux-2.0.0.zip
```

3. **Import VMs**
```bash
# Import Kali Linux
VBoxManage import kali-linux-2023.3-virtualbox-amd64.ova

# Import Metasploitable2
unzip metasploitable-linux-2.0.0.zip
VBoxManage import Metasploitable-Linux-2.0.0.ova
```

4. **Network Configuration**
```bash
# Create Host-Only Network
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0

# Configure VM network
VBoxManage modifyvm "Kali Linux" --nic1 hostonly --hostonlyadapter1 vboxnet0
VBoxManage modifyvm "Metasploitable2" --nic1 hostonly --hostonlyadapter1 vboxnet0
```

### VM Network Settings

**Kali Linux:**
- IP: 192.168.56.10
- Gateway: 192.168.56.1
- DNS: 8.8.8.8

**Metasploitable2:**
- IP: 192.168.56.20
- Gateway: 192.168.56.1
- DNS: 8.8.8.8

## 🔐 Security Configuration

### 1. Firewall Setup
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API
sudo ufw allow 3000/tcp  # Frontend (development)
```

### 2. SSL/TLS Setup
```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Let's Encrypt (production)
sudo apt-get install certbot
sudo certbot --nginx -d yourdomain.com
```

### 3. Database Security
```bash
# PostgreSQL
sudo -u postgres psql
ALTER USER pentest PASSWORD 'strong-password-here';
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO pentest;
\q
```

## 🧪 Testing Setup

### 1. Verify Installation
```bash
# Check services
curl http://localhost:8000/health
curl http://localhost:3000

# Test database connection
docker compose exec backend python -c "
from app.core.database import engine
print('Database connected:', engine.execute('SELECT 1').scalar())
"

# Test Redis connection
docker compose exec redis redis-cli ping
```

### 2. Run Sample Scan
```bash
# Login ke aplikasi
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Create test scan
curl -X POST http://localhost:8000/api/v1/scans/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Scan",
    "target": "192.168.56.20",
    "scan_type": "nmap"
  }'
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check port usage
sudo netstat -tulpn | grep :8000
sudo lsof -i :8000

# Kill process
sudo kill -9 PID
```

2. **Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U pentest -d pentest_lab
```

3. **Docker Issues**
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

4. **Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x backend/entrypoint.sh
```

### Logs dan Debugging

```bash
# View application logs
docker compose logs -f backend
docker compose logs -f frontend

# View specific service logs
docker compose logs -f postgres
docker compose logs -f redis

# Debug mode
export DEBUG=true
docker compose up
```

## 📊 Performance Tuning

### 1. Database Optimization
```sql
-- PostgreSQL tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

### 2. Redis Optimization
```bash
# Redis configuration
echo "maxmemory 256mb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
sudo systemctl restart redis-server
```

### 3. Application Optimization
```bash
# Increase worker processes
# Edit docker-compose.yml
services:
  backend:
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔄 Backup & Recovery

### 1. Database Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U pentest pentest_lab > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U pentest pentest_lab < backup_20231201.sql
```

### 2. Application Backup
```bash
# Backup uploads dan reports
tar -czf app_backup_$(date +%Y%m%d).tar.gz uploads/ reports/ logs/

# Restore
tar -xzf app_backup_20231201.tar.gz
```

## 📈 Monitoring

### 1. Health Checks
```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "Checking services..."

# API Health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API: OK"
else
    echo "❌ API: FAILED"
fi

# Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAILED"
fi

# Database
if docker compose exec -T postgres pg_isready > /dev/null 2>&1; then
    echo "✅ Database: OK"
else
    echo "❌ Database: FAILED"
fi

# Redis
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: OK"
else
    echo "❌ Redis: FAILED"
fi
EOF

chmod +x health_check.sh
./health_check.sh
```

### 2. Log Monitoring
```bash
# Setup log rotation
sudo nano /etc/logrotate.d/pentest-lab

# Content:
/var/log/pentest-lab/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

---

**🎉 Setup Complete!** 

Aplikasi Anda sekarang siap digunakan. Akses:
- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Default Login**: admin / admin123

Untuk pertanyaan atau bantuan, silakan buka issue di repository ini.
