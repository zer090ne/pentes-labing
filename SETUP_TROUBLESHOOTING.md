# 🔧 Setup Troubleshooting Guide

Panduan untuk mengatasi masalah instalasi dan setup Pentest Lab Otomatis.

## 🚨 Common Issues & Solutions

### 1. **psycopg2-binary Installation Error**

**Error:**
```
ERROR: Failed building wheel for psycopg2-binary
fatal error: libpq-fe.h: No such file or directory
```

**Solutions:**

#### Option A: Install System Dependencies (Recommended)
```bash
# Install PostgreSQL development headers
sudo apt-get update
sudo apt-get install -y \
    postgresql-server-dev-all \
    libpq-dev \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev

# Then install Python packages
pip install -r requirements.txt
```

#### Option B: Use Alternative Database Driver
```bash
# Install minimal requirements first
pip install -r requirements-minimal.txt

# The app will use asyncpg instead of psycopg2
```

#### Option C: Use SQLite for Development
```bash
# Set environment variable
export DATABASE_URL="sqlite:///./test.db"

# Install minimal requirements
pip install -r requirements-minimal.txt
```

### 2. **Missing Pentest Tools**

**Error:**
```
ModuleNotFoundError: No module named 'nmap'
```

**Solution:**
```bash
# Install pentest tools
sudo apt-get install -y \
    nmap \
    nikto \
    hydra \
    sqlmap \
    gobuster \
    dirb \
    dirbuster \
    wapiti \
    w3af \
    skipfish
```

### 3. **Groq API Key Not Set**

**Error:**
```
AI service not available
```

**Solution:**
```bash
# Set your Groq API key
export GROQ_API_KEY="your-groq-api-key-here"

# Or add to .env file
echo "GROQ_API_KEY=your-groq-api-key-here" >> .env
```

### 4. **Port Already in Use**

**Error:**
```
ERROR: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

### 5. **Permission Denied**

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix file permissions
chmod +x backend/entrypoint.sh
chmod +x backend/install_dependencies.sh

# Fix directory permissions
sudo chown -R $USER:$USER .
```

## 🚀 Quick Start Options

### Option 1: Full Setup (Recommended)
```bash
# 1. Install system dependencies
cd backend
chmod +x install_dependencies.sh
./install_dependencies.sh

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements.txt

# 4. Set environment variables
cp ../env.example .env
# Edit .env with your settings

# 5. Start server
uvicorn main:app --reload
```

### Option 2: Minimal Setup (Quick Test)
```bash
# 1. Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate

# 2. Install minimal requirements
pip install -r requirements-minimal.txt

# 3. Use development runner
python run_dev.py
```

### Option 3: Docker Setup (Easiest)
```bash
# 1. Install Docker
sudo apt-get install docker.io docker-compose

# 2. Start all services
docker-compose up -d

# 3. Access application
# Web UI: http://localhost:3000
# API: http://localhost:8000
```

## 🔍 Debugging Commands

### Check System Dependencies
```bash
# Check Python version
python --version

# Check pip version
pip --version

# Check installed packages
pip list

# Check system packages
dpkg -l | grep postgresql
dpkg -l | grep python3-dev
```

### Check Application Status
```bash
# Test API endpoint
curl http://localhost:8000/health

# Check database connection
python -c "
from app.core.database import engine
print('Database connected:', engine.execute('SELECT 1').scalar())
"

# Check AI service
python -c "
from app.services.ai_service import AIService
ai = AIService()
print('AI available:', ai.client is not None)
"
```

### Check Logs
```bash
# Application logs
tail -f logs/pentest_lab.log

# Docker logs
docker-compose logs -f backend

# System logs
journalctl -u docker
```

## 🛠️ Environment-Specific Solutions

### Kali Linux
```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install development tools
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    postgresql-client

# Install pentest tools (usually pre-installed)
sudo apt install -y \
    nmap \
    nikto \
    hydra \
    sqlmap \
    gobuster
```

### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install development headers
sudo apt install -y \
    postgresql-server-dev-all \
    libpq-dev \
    python3-dev
```

### CentOS/RHEL
```bash
# Install PostgreSQL
sudo yum install -y postgresql-server postgresql-devel

# Install development tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel
```

## 📞 Getting Help

### Check Application Health
```bash
# Health check endpoint
curl -X GET "http://localhost:8000/health" \
  -H "accept: application/json"

# API documentation
open http://localhost:8000/docs
```

### Common Error Messages
- **"ModuleNotFoundError"**: Install missing Python packages
- **"Connection refused"**: Check if service is running
- **"Permission denied"**: Fix file/directory permissions
- **"Port already in use"**: Kill existing process or use different port
- **"Database connection failed"**: Check database service and credentials

### Log Files Location
- Application logs: `logs/pentest_lab.log`
- Docker logs: `docker-compose logs`
- System logs: `/var/log/syslog`

## 🎯 Success Indicators

### Backend Running Successfully
```bash
# Should show:
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Running Successfully
```bash
# Should show:
webpack compiled with 0 errors
Local:            http://localhost:3000
On Your Network:  http://192.168.1.100:3000
```

### AI Service Available
```bash
# API response should show:
{
  "ai_enabled": true,
  "model": "groq-llama3-8b-8192",
  "status": "available"
}
```

---

**💡 Tip**: Jika masih mengalami masalah, coba jalankan dengan `python run_dev.py` untuk mode development yang lebih toleran terhadap missing dependencies.
