"""
Service untuk menjalankan tools pentest
"""

import asyncio
import subprocess
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.schemas.tool import ToolResponse, ToolStatus
from app.tools.nmap_wrapper import NmapWrapper
from app.tools.nikto_wrapper import NiktoWrapper
from app.tools.hydra_wrapper import HydraWrapper
from app.tools.sqlmap_wrapper import SqlmapWrapper
from app.tools.gobuster_wrapper import GobusterWrapper


class ToolService:
    """Service untuk menjalankan tools pentest"""
    
    def __init__(self, db: Session):
        self.db = db
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize tool wrappers
        self.nmap = NmapWrapper()
        self.nikto = NiktoWrapper()
        self.hydra = HydraWrapper()
        self.sqlmap = SqlmapWrapper()
        self.gobuster = GobusterWrapper()
    
    async def run_nmap(self, target: str, options: str = "-sV -O") -> ToolResponse:
        """Run Nmap scan"""
        task_id = str(uuid.uuid4())
        command = f"{settings.NMAP_PATH} {options} {target}"
        
        logger.info(f"Starting Nmap scan: {command}")
        
        try:
            # Run Nmap asynchronously
            result = await self.nmap.scan(target, options)
            
            return ToolResponse(
                task_id=task_id,
                tool="nmap",
                command=command,
                status="completed",
                output=result.get("output", ""),
                parsed_data=result.get("parsed_data", {}),
                created_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Nmap scan failed: {e}")
            return ToolResponse(
                task_id=task_id,
                tool="nmap",
                command=command,
                status="failed",
                error=str(e),
                created_at=datetime.now().isoformat()
            )
    
    async def run_nikto(self, target: str, options: str = "") -> ToolResponse:
        """Run Nikto web vulnerability scan"""
        task_id = str(uuid.uuid4())
        command = f"{settings.NIKTO_PATH} -h {target} {options}"
        
        logger.info(f"Starting Nikto scan: {command}")
        
        try:
            result = await self.nikto.scan(target, options)
            
            return ToolResponse(
                task_id=task_id,
                tool="nikto",
                command=command,
                status="completed",
                output=result.get("output", ""),
                parsed_data=result.get("parsed_data", {}),
                created_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Nikto scan failed: {e}")
            return ToolResponse(
                task_id=task_id,
                tool="nikto",
                command=command,
                status="failed",
                error=str(e),
                created_at=datetime.now().isoformat()
            )
    
    async def run_hydra(self, target: str, service: str, username: str = "admin", 
                       password_list: str = "/usr/share/wordlists/rockyou.txt") -> ToolResponse:
        """Run Hydra brute force attack"""
        task_id = str(uuid.uuid4())
        command = f"{settings.HYDRA_PATH} -l {username} -P {password_list} {service}://{target}"
        
        logger.info(f"Starting Hydra attack: {command}")
        
        try:
            result = await self.hydra.attack(target, service, username, password_list)
            
            return ToolResponse(
                task_id=task_id,
                tool="hydra",
                command=command,
                status="completed",
                output=result.get("output", ""),
                parsed_data=result.get("parsed_data", {}),
                created_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Hydra attack failed: {e}")
            return ToolResponse(
                task_id=task_id,
                tool="hydra",
                command=command,
                status="failed",
                error=str(e),
                created_at=datetime.now().isoformat()
            )
    
    async def run_sqlmap(self, url: str, options: str = "--forms --batch") -> ToolResponse:
        """Run SQLMap SQL injection test"""
        task_id = str(uuid.uuid4())
        command = f"{settings.SQLMAP_PATH} -u {url} {options}"
        
        logger.info(f"Starting SQLMap test: {command}")
        
        try:
            result = await self.sqlmap.test(url, options)
            
            return ToolResponse(
                task_id=task_id,
                tool="sqlmap",
                command=command,
                status="completed",
                output=result.get("output", ""),
                parsed_data=result.get("parsed_data", {}),
                created_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"SQLMap test failed: {e}")
            return ToolResponse(
                task_id=task_id,
                tool="sqlmap",
                command=command,
                status="failed",
                error=str(e),
                created_at=datetime.now().isoformat()
            )
    
    async def run_gobuster(self, url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> ToolResponse:
        """Run Gobuster directory enumeration"""
        task_id = str(uuid.uuid4())
        command = f"{settings.GOBUSTER_PATH} dir -u {url} -w {wordlist}"
        
        logger.info(f"Starting Gobuster scan: {command}")
        
        try:
            result = await self.gobuster.scan(url, wordlist)
            
            return ToolResponse(
                task_id=task_id,
                tool="gobuster",
                command=command,
                status="completed",
                output=result.get("output", ""),
                parsed_data=result.get("parsed_data", {}),
                created_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Gobuster scan failed: {e}")
            return ToolResponse(
                task_id=task_id,
                tool="gobuster",
                command=command,
                status="failed",
                error=str(e),
                created_at=datetime.now().isoformat()
            )
    
    async def get_tool_status(self, task_id: str) -> Optional[ToolStatus]:
        """Get status of running tool"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            if task.done():
                try:
                    result = task.result()
                    return ToolStatus(
                        task_id=task_id,
                        status="completed",
                        output=result.get("output", "")
                    )
                except Exception as e:
                    return ToolStatus(
                        task_id=task_id,
                        status="failed",
                        error=str(e)
                    )
            else:
                return ToolStatus(
                    task_id=task_id,
                    status="running",
                    progress=50  # Placeholder
                )
        return None
    
    async def stop_tool(self, task_id: str) -> bool:
        """Stop running tool"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            del self.running_tasks[task_id]
            return True
        return False
