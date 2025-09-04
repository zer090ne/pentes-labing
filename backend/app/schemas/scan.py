"""
Pydantic schemas untuk scan data
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    """Scan types"""
    NMAP = "nmap"
    NIKTO = "nikto"
    HYDRA = "hydra"
    SQLMAP = "sqlmap"
    GOBUSTER = "gobuster"
    COMPREHENSIVE = "comprehensive"


class ScanStatus(str, Enum):
    """Scan status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanCreate(BaseModel):
    """Schema untuk membuat scan baru"""
    name: str = Field(..., min_length=1, max_length=255)
    target: str = Field(..., min_length=1, max_length=255)
    scan_type: ScanType
    options: Optional[str] = None
    description: Optional[str] = None


class ScanUpdate(BaseModel):
    """Schema untuk update scan"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ScanStatus] = None


class ScanResultResponse(BaseModel):
    """Schema untuk response scan result"""
    id: int
    scan_id: int
    tool: str
    command: str
    output: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    """Schema untuk response scan"""
    id: int
    name: str
    target: str
    scan_type: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: Optional[int] = None
    results: List[ScanResultResponse] = []
    recommendations: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Schema untuk response recommendation"""
    id: int
    scan_id: int
    type: str
    title: str
    description: str
    priority: str
    action: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
