"""
Report models untuk generated reports
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Report(Base):
    """Model untuk generated reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    report_type = Column(String(50), nullable=False)  # html, pdf, json
    title = Column(String(255), nullable=False)
    file_path = Column(String(500))  # Path ke file report
    content = Column(Text)  # Content report (untuk HTML)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan")
