"""
Tools endpoints untuk menjalankan tools pentest
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.schemas.tool import ToolRequest, ToolResponse
from app.services.tool_service import ToolService

router = APIRouter()


@router.post("/nmap", response_model=ToolResponse)
async def run_nmap(
    request: ToolRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run Nmap scan"""
    tool_service = ToolService(db)
    
    # Validate request
    if not request.target:
        raise HTTPException(status_code=400, detail="Target is required")
    
    # Run Nmap
    result = await tool_service.run_nmap(
        target=request.target,
        options=request.options or "-sV -O"
    )
    
    return result


@router.post("/nikto", response_model=ToolResponse)
async def run_nikto(
    request: ToolRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run Nikto web vulnerability scan"""
    tool_service = ToolService(db)
    
    if not request.target:
        raise HTTPException(status_code=400, detail="Target is required")
    
    result = await tool_service.run_nikto(
        target=request.target,
        options=request.options or ""
    )
    
    return result


@router.post("/hydra", response_model=ToolResponse)
async def run_hydra(
    request: ToolRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run Hydra brute force attack"""
    tool_service = ToolService(db)
    
    if not request.target or not request.service:
        raise HTTPException(status_code=400, detail="Target and service are required")
    
    result = await tool_service.run_hydra(
        target=request.target,
        service=request.service,
        username=request.username or "admin",
        password_list=request.password_list or "/usr/share/wordlists/rockyou.txt"
    )
    
    return result


@router.post("/sqlmap", response_model=ToolResponse)
async def run_sqlmap(
    request: ToolRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run SQLMap SQL injection test"""
    tool_service = ToolService(db)
    
    if not request.target:
        raise HTTPException(status_code=400, detail="Target URL is required")
    
    result = await tool_service.run_sqlmap(
        url=request.target,
        options=request.options or "--forms --batch"
    )
    
    return result


@router.post("/gobuster", response_model=ToolResponse)
async def run_gobuster(
    request: ToolRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run Gobuster directory enumeration"""
    tool_service = ToolService(db)
    
    if not request.target:
        raise HTTPException(status_code=400, detail="Target URL is required")
    
    result = await tool_service.run_gobuster(
        url=request.target,
        wordlist=request.wordlist or "/usr/share/wordlists/dirb/common.txt"
    )
    
    return result


@router.get("/status/{task_id}")
async def get_tool_status(task_id: str, db: Session = Depends(get_db)):
    """Get status of running tool"""
    tool_service = ToolService(db)
    status = await tool_service.get_tool_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status


@router.get("/available")
async def get_available_tools():
    """Get list of available tools"""
    return {
        "tools": [
            {
                "name": "nmap",
                "description": "Network mapper - port scanning and service detection",
                "category": "reconnaissance"
            },
            {
                "name": "nikto",
                "description": "Web vulnerability scanner",
                "category": "web_testing"
            },
            {
                "name": "hydra",
                "description": "Brute force attack tool",
                "category": "brute_force"
            },
            {
                "name": "sqlmap",
                "description": "SQL injection testing tool",
                "category": "web_testing"
            },
            {
                "name": "gobuster",
                "description": "Directory/file brute forcer",
                "category": "web_testing"
            }
        ]
    }
