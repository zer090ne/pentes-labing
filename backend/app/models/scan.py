"""
Scan models untuk database
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Scan(Base):
    """Model untuk scan sessions"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    target = Column(String(255), nullable=False)  # IP atau domain target
    scan_type = Column(String(50), nullable=False)  # nmap, nikto, hydra, dll
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="scans")
    results = relationship("ScanResult", back_populates="scan", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="scan", cascade="all, delete-orphan")


class ScanResult(Base):
    """Model untuk hasil scan"""
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    tool = Column(String(50), nullable=False)  # nmap, nikto, hydra, dll
    command = Column(Text, nullable=False)  # Command yang dijalankan
    output = Column(Text)  # Raw output dari tool
    parsed_data = Column(JSON)  # Data yang sudah di-parse
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    scan = relationship("Scan", back_populates="results")


class Recommendation(Base):
    """Model untuk rekomendasi otomatis"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    type = Column(String(50), nullable=False)  # vulnerability, next_step, mitigation
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    action = Column(Text)  # Command atau action yang disarankan
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="recommendations")
