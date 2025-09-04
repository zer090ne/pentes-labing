# 🛡️ Pentest Lab Otomatis

Web UI untuk monitoring dan menjalankan tools pentest dengan sistem rekomendasi otomatis.

## 🚀 Fitur Utama

### 🔍 Automated Scanning
- **Nmap**: Port scanning dan service detection
- **Nikto**: Web vulnerability scanning
- **Hydra**: Brute force attacks
- **SQLMap**: SQL injection testing
- **Gobuster**: Directory enumeration

### 🤖 AI-Powered Intelligence
- **Groq AI Integration**: Analisis mendalam dengan Llama3-8B model
- **Intelligent Recommendations**: Saran berbasis AI dengan prioritas akurat
- **Risk Assessment**: Scoring risiko otomatis dengan confidence level
- **Vulnerability Analysis**: Deteksi pattern dan threat intelligence
- **Smart Reporting**: AI-generated reports dengan insights mendalam

### 📊 Real-time Monitoring
- Live output dari tools
- Progress tracking
- WebSocket untuk real-time updates
- Status notifications

### 📋 Report Generation
- HTML/PDF/JSON reports
- Executive summary
- Technical details
- Remediation steps

### 🔐 Security Features
- User authentication dengan JWT
- Role-based access control
- Audit logging
- Network isolation

## 🏗️ Arsitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   Backend API   │    │   Tool Engine   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Python)      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST API      │    │ • Nmap Wrapper  │
│ • Real-time     │    │ • WebSocket     │    │ • Nikto Wrapper │
│ • Reports       │    │ • Auth          │    │ • Hydra Wrapper │
│ • Monitoring    │    │ • Queue         │    │ • SQLMap Wrapper│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Message       │    │   VM Manager    │
│   (PostgreSQL)  │    │   Queue         │    │   (Docker)      │
│                 │    │   (Redis)       │    │                 │
│ • Scan Results  │    │ • Task Queue    │    │ • Kali Linux    │
│ • Reports       │    │ • Notifications │    │ • Metasploitable│
│ • Config        │    │ • Status        │    │ • Isolation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Teknologi Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: Reliable database
- **Redis**: Caching dan message queue
- **Celery**: Background task processing
- **Pydantic**: Data validation
- **Groq AI**: Advanced AI analysis dengan Llama3-8B

### Frontend
- **React**: UI framework
- **TypeScript**: Type safety
- **Material-UI**: Component library
- **Socket.io**: Real-time communication
- **Chart.js**: Data visualization

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container setup
- **Nginx**: Reverse proxy
- **Git**: Version control

## 📦 Instalasi

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start

1. **Clone repository**
```bash
git clone <repository-url>
cd pentes-labing
```

2. **Setup environment**
```bash
cp env.example .env
# Edit .env file sesuai kebutuhan
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Access application**
- Web UI: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Flower (Celery): http://localhost:5555

### Manual Installation

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows

pip install -r requirements.txt
uvicorn main:app --reload
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

3. **Database Setup**
```bash
# PostgreSQL
createdb pentest_lab
# atau gunakan Docker
docker run -d --name postgres -e POSTGRES_DB=pentest_lab -e POSTGRES_USER=pentest -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
```

## 🎯 Penggunaan

### 1. Dashboard
- Overview scan statistics
- Quick scan form
- Recent scans monitoring

### 2. Scans Management
- Create new scans
- Monitor running scans
- View scan results
- Stop/delete scans

### 3. Tools
- Run individual tools
- Configure tool parameters
- View real-time output
- Save results

### 4. Reports
- Generate comprehensive reports
- Download in multiple formats
- View scan recommendations
- Track remediation progress

### 5. AI Analysis
- AI-powered vulnerability assessment
- Intelligent risk scoring
- Smart recommendations
- Advanced threat analysis
- AI-generated reports

## 🔧 Konfigurasi

### Environment Variables
```bash
# Application
APP_NAME=Pentest Lab Otomatis
DEBUG=false

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://pentest:password@localhost:5432/pentest_lab
REDIS_URL=redis://localhost:6379/0

# VM Settings
KALI_VM_IP=192.168.56.10
METASPLOITABLE_VM_IP=192.168.56.20
VM_NETWORK=192.168.56.0/24

# AI Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama3-8b-8192
AI_ENABLED=true
AI_ANALYSIS_DEPTH=detailed
```

### Tool Configuration
```bash
# Tool paths (adjust sesuai instalasi)
NMAP_PATH=/usr/bin/nmap
NIKTO_PATH=/usr/bin/nikto
HYDRA_PATH=/usr/bin/hydra
SQLMAP_PATH=/usr/bin/sqlmap
GOBUSTER_PATH=/usr/bin/gobuster
```

## 🔒 Keamanan

### Network Security
- Isolasi VM dalam network terpisah
- Firewall rules
- VPN access untuk remote testing

### Application Security
- JWT authentication
- Input validation
- SQL injection prevention
- XSS protection

### Data Security
- Encrypted storage
- Secure file handling
- Audit trails
- Data retention policies

## 📊 Monitoring

### Health Checks
- API health endpoint: `/health`
- Database connectivity
- Redis connectivity
- Tool availability

### Logging
- Application logs: `logs/pentest_lab.log`
- Access logs
- Error tracking
- Performance metrics

## 🧪 Testing

### Unit Tests
```bash
cd backend
pytest tests/
```

### Integration Tests
```bash
# Test API endpoints
pytest tests/integration/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Setup
1. **Environment Configuration**
```bash
# Set production environment variables
export DEBUG=false
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:pass@prod-db:5432/pentest_lab
```

2. **Docker Production**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **SSL/TLS Setup**
```bash
# Configure Nginx with SSL
# Update nginx.conf with SSL certificates
```

### Scaling
- Horizontal scaling dengan multiple backend instances
- Load balancing dengan Nginx
- Database clustering
- Redis clustering untuk high availability

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 🆘 Support

- Documentation: [Wiki](wiki-url)
- Issues: [GitHub Issues](issues-url)
- Discussions: [GitHub Discussions](discussions-url)

## 🔄 Roadmap

### v1.1
- [ ] Additional tools (OpenVAS, Burp Suite integration)
- [ ] Advanced reporting features
- [ ] Multi-user collaboration
- [ ] API rate limiting

### v1.2
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Integration dengan SIEM
- [ ] Automated remediation

### v2.0
- [ ] AI-powered vulnerability assessment
- [ ] Machine learning untuk threat detection
- [ ] Advanced threat modeling
- [ ] Compliance reporting

---

**⚠️ Disclaimer**: Tool ini hanya untuk tujuan edukasi dan testing keamanan yang sah. Pastikan Anda memiliki izin yang tepat sebelum melakukan testing pada sistem yang bukan milik Anda.
