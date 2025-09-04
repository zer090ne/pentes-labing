"""
Pydantic schemas untuk report data
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReportType(str, Enum):
    """Report types"""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    XML = "xml"


class ReportCreate(BaseModel):
    """Schema untuk membuat report"""
    scan_id: int
    report_type: ReportType
    title: str = Field(..., min_length=1, max_length=255)


class ReportUpdate(BaseModel):
    """Schema untuk update report"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema untuk response report"""
    id: int
    scan_id: int
    report_type: str
    title: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
