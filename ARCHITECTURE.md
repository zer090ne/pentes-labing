# 🏗️ Arsitektur Pentest Lab Otomatis

## Gambaran Umum Sistem

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   Backend API   │    │   Tool Engine   │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   (Python)      │
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

## Komponen Utama

### 1. Frontend (Web UI)
- **Framework**: React dengan TypeScript
- **UI Library**: Material-UI atau Ant Design
- **Real-time**: WebSocket untuk live updates
- **Features**:
  - Dashboard dengan metrics real-time
  - Form untuk konfigurasi scan
  - Tabel hasil scan dengan filtering
  - Grafik dan visualisasi data
  - Report generator
  - Log viewer dengan syntax highlighting

### 2. Backend API
- **Framework**: FastAPI (Python)
- **Features**:
  - RESTful API endpoints
  - WebSocket untuk real-time communication
  - JWT Authentication
  - Background task processing
  - File upload/download
  - API documentation (Swagger)

### 3. Tool Engine
- **Language**: Python
- **Architecture**: Modular wrapper system
- **Tools Supported**:
  - Nmap (port scanning, OS detection)
  - Nikto (web vulnerability scanner)
  - Hydra (brute force attacks)
  - SQLMap (SQL injection testing)
  - Gobuster/Dirb (directory enumeration)
  - OpenVAS (vulnerability assessment)
  - Custom scripts

### 4. Database Layer
- **Primary**: PostgreSQL
- **Cache**: Redis
- **Storage**: File system untuk reports dan logs

### 5. VM Management
- **Containerization**: Docker
- **VM Integration**: VirtualBox API
- **Isolation**: Network segmentation

## Alur Kerja (Workflow)

### 1. Scan Initiation
```
User Input → Web UI → API Validation → Task Queue → Tool Execution
```

### 2. Real-time Monitoring
```
Tool Output → Parser → Database → WebSocket → UI Update
```

### 3. Automated Recommendations
```
Scan Results → Analysis Engine → Rule Engine → Recommendations → UI Display
```

## Struktur Direktori

```
pentes-labing/
├── frontend/                 # React Web UI
│   ├── src/
│   │   ├── components/      # UI Components
│   │   ├── pages/          # Page Components
│   │   ├── services/       # API Services
│   │   └── utils/          # Utilities
│   └── package.json
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API Routes
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── tools/          # Tool wrappers
│   ├── requirements.txt
│   └── main.py
├── tools/                  # Tool implementations
│   ├── nmap_wrapper.py
│   ├── nikto_wrapper.py
│   ├── hydra_wrapper.py
│   └── sqlmap_wrapper.py
├── docker/                 # Docker configurations
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docs/                   # Documentation
├── tests/                  # Test files
└── README.md
```

## Fitur Utama

### 1. Automated Scanning
- Port scanning dengan Nmap
- Web vulnerability scanning
- Directory enumeration
- Service fingerprinting

### 2. Intelligent Recommendations
- Analisis hasil scan otomatis
- Saran langkah selanjutnya
- Prioritas vulnerability
- Mitigation strategies

### 3. Real-time Monitoring
- Live output dari tools
- Progress tracking
- Error handling
- Status notifications

### 4. Report Generation
- HTML/PDF reports
- Executive summary
- Technical details
- Remediation steps

### 5. Security Features
- User authentication
- Role-based access
- Audit logging
- Network isolation

## Teknologi Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: Reliable database
- **Redis**: Caching dan message queue
- **Celery**: Background task processing
- **Pydantic**: Data validation

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

## Keamanan

### 1. Network Security
- Isolasi VM dalam network terpisah
- Firewall rules
- VPN access untuk remote testing

### 2. Application Security
- JWT authentication
- Input validation
- SQL injection prevention
- XSS protection

### 3. Data Security
- Encrypted storage
- Secure file handling
- Audit trails
- Data retention policies
