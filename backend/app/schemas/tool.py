"""
Pydantic schemas untuk tool data
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ToolRequest(BaseModel):
    """Schema untuk tool request"""
    target: str = Field(..., min_length=1, max_length=255)
    options: Optional[str] = None
    service: Optional[str] = None  # Untuk Hydra
    username: Optional[str] = None  # Untuk Hydra
    password_list: Optional[str] = None  # Untuk Hydra
    wordlist: Optional[str] = None  # Untuk Gobuster


class ToolResponse(BaseModel):
    """Schema untuk tool response"""
    task_id: str
    tool: str
    command: str
    status: str
    output: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class ToolStatus(BaseModel):
    """Schema untuk tool status"""
    task_id: str
    status: str
    progress: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None
