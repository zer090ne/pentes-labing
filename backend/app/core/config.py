"""
Configuration settings untuk aplikasi
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "Pentest Lab Otomatis"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "sqlite:///./pentest_lab.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    LOGS_DIR: str = "logs"
    
    # Tool settings
    NMAP_PATH: str = "/usr/bin/nmap"
    NIKTO_PATH: str = "/usr/bin/nikto"
    HYDRA_PATH: str = "/usr/bin/hydra"
    SQLMAP_PATH: str = "/usr/bin/sqlmap"
    GOBUSTER_PATH: str = "/usr/bin/gobuster"
    
    # VM settings
    KALI_VM_IP: str = "192.168.56.10"
    METASPLOITABLE_VM_IP: str = "192.168.56.20"
    VM_NETWORK: str = "192.168.56.0/24"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/pentest_lab.log"
    
    # AI Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-8b-8192"
    OPENAI_API_KEY: str = ""
    AI_ENABLED: bool = True
    AI_ANALYSIS_DEPTH: str = "detailed"  # basic, detailed, comprehensive
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Create directories if they don't exist
for directory in [settings.UPLOAD_DIR, settings.REPORTS_DIR, settings.LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)
