"""
Service untuk mengelola scan sessions
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import asyncio
from loguru import logger

from app.models.scan import Scan, ScanResult
from app.schemas.scan import ScanCreate, ScanResponse, ScanResultResponse
from app.services.tool_service import ToolService
from app.core.websocket import manager


class ScanService:
    """Service untuk mengelola scan sessions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tool_service = ToolService(db)
    
    async def create_scan(self, scan_data: ScanCreate) -> ScanResponse:
        """Create new scan"""
        try:
            # Create scan record
            scan = Scan(
                name=scan_data.name,
                target=scan_data.target,
                scan_type=scan_data.scan_type.value,
                status="pending",
                user_id=1  # TODO: Get from current user
            )
            
            self.db.add(scan)
            self.db.commit()
            self.db.refresh(scan)
            
            logger.info(f"Created scan: {scan.id} - {scan.name}")
            
            return ScanResponse.from_orm(scan)
            
        except Exception as e:
            logger.error(f"Error creating scan: {e}")
            self.db.rollback()
            raise
    
    async def get_scans(self, skip: int = 0, limit: int = 100) -> List[ScanResponse]:
        """Get all scans"""
        try:
            scans = self.db.query(Scan).order_by(desc(Scan.created_at)).offset(skip).limit(limit).all()
            return [ScanResponse.from_orm(scan) for scan in scans]
        except Exception as e:
            logger.error(f"Error getting scans: {e}")
            return []
    
    async def get_scan(self, scan_id: int) -> Optional[ScanResponse]:
        """Get specific scan"""
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                return ScanResponse.from_orm(scan)
            return None
        except Exception as e:
            logger.error(f"Error getting scan {scan_id}: {e}")
            return None
    
    async def get_scan_results(self, scan_id: int) -> List[ScanResultResponse]:
        """Get scan results"""
        try:
            results = self.db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
            return [ScanResultResponse.from_orm(result) for result in results]
        except Exception as e:
            logger.error(f"Error getting scan results for {scan_id}: {e}")
            return []
    
    async def run_scan(self, scan_id: int):
        """Run scan in background"""
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                logger.error(f"Scan {scan_id} not found")
                return
            
            # Update scan status
            scan.status = "running"
            scan.started_at = datetime.now()
            self.db.commit()
            
            # Send WebSocket update
            await manager.send_scan_update(str(scan_id), "running", {"message": "Scan started"})
            
            logger.info(f"Starting scan {scan_id}: {scan.name}")
            
            # Run tools based on scan type
            if scan.scan_type == "nmap":
                await self._run_nmap_scan(scan)
            elif scan.scan_type == "nikto":
                await self._run_nikto_scan(scan)
            elif scan.scan_type == "comprehensive":
                await self._run_comprehensive_scan(scan)
            else:
                await self._run_single_tool_scan(scan)
            
            # Update scan status
            scan.status = "completed"
            scan.completed_at = datetime.now()
            self.db.commit()
            
            # Send WebSocket update
            await manager.send_scan_update(str(scan_id), "completed", {"message": "Scan completed"})
            
            logger.info(f"Completed scan {scan_id}: {scan.name}")
            
        except Exception as e:
            logger.error(f"Error running scan {scan_id}: {e}")
            
            # Update scan status to failed
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = "failed"
                scan.completed_at = datetime.now()
                self.db.commit()
                
                # Send WebSocket update
                await manager.send_scan_update(str(scan_id), "failed", {"error": str(e)})
    
    async def _run_nmap_scan(self, scan: Scan):
        """Run Nmap scan"""
        try:
            # Create scan result record
            result = ScanResult(
                scan_id=scan.id,
                tool="nmap",
                command=f"nmap -sV -O {scan.target}",
                status="running"
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            # Run Nmap
            tool_result = await self.tool_service.run_nmap(scan.target, "-sV -O")
            
            # Update result
            result.output = tool_result.output
            result.parsed_data = tool_result.parsed_data
            result.status = "completed" if tool_result.status == "completed" else "failed"
            result.completed_at = datetime.now()
            self.db.commit()
            
            # Send WebSocket update
            await manager.send_tool_output(str(scan.id), "nmap", tool_result.output)
            
        except Exception as e:
            logger.error(f"Error running Nmap scan: {e}")
            if 'result' in locals():
                result.status = "failed"
                result.completed_at = datetime.now()
                self.db.commit()
    
    async def _run_nikto_scan(self, scan: Scan):
        """Run Nikto scan"""
        try:
            # Create scan result record
            result = ScanResult(
                scan_id=scan.id,
                tool="nikto",
                command=f"nikto -h {scan.target}",
                status="running"
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            # Run Nikto
            tool_result = await self.tool_service.run_nikto(scan.target)
            
            # Update result
            result.output = tool_result.output
            result.parsed_data = tool_result.parsed_data
            result.status = "completed" if tool_result.status == "completed" else "failed"
            result.completed_at = datetime.now()
            self.db.commit()
            
            # Send WebSocket update
            await manager.send_tool_output(str(scan.id), "nikto", tool_result.output)
            
        except Exception as e:
            logger.error(f"Error running Nikto scan: {e}")
            if 'result' in locals():
                result.status = "failed"
                result.completed_at = datetime.now()
                self.db.commit()
    
    async def _run_comprehensive_scan(self, scan: Scan):
        """Run comprehensive scan with multiple tools"""
        try:
            # Run Nmap first
            await self._run_nmap_scan(scan)
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Run Nikto
            await self._run_nikto_scan(scan)
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Run Gobuster if web server detected
            await self._run_gobuster_scan(scan)
            
        except Exception as e:
            logger.error(f"Error running comprehensive scan: {e}")
    
    async def _run_single_tool_scan(self, scan: Scan):
        """Run single tool scan"""
        try:
            if scan.scan_type == "hydra":
                await self._run_hydra_scan(scan)
            elif scan.scan_type == "sqlmap":
                await self._run_sqlmap_scan(scan)
            elif scan.scan_type == "gobuster":
                await self._run_gobuster_scan(scan)
        except Exception as e:
            logger.error(f"Error running single tool scan: {e}")
    
    async def _run_hydra_scan(self, scan: Scan):
        """Run Hydra scan"""
        try:
            result = ScanResult(
                scan_id=scan.id,
                tool="hydra",
                command=f"hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://{scan.target}",
                status="running"
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            tool_result = await self.tool_service.run_hydra(scan.target, "ssh")
            
            result.output = tool_result.output
            result.parsed_data = tool_result.parsed_data
            result.status = "completed" if tool_result.status == "completed" else "failed"
            result.completed_at = datetime.now()
            self.db.commit()
            
            await manager.send_tool_output(str(scan.id), "hydra", tool_result.output)
            
        except Exception as e:
            logger.error(f"Error running Hydra scan: {e}")
            if 'result' in locals():
                result.status = "failed"
                result.completed_at = datetime.now()
                self.db.commit()
    
    async def _run_sqlmap_scan(self, scan: Scan):
        """Run SQLMap scan"""
        try:
            result = ScanResult(
                scan_id=scan.id,
                tool="sqlmap",
                command=f"sqlmap -u {scan.target} --forms --batch",
                status="running"
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            tool_result = await self.tool_service.run_sqlmap(scan.target)
            
            result.output = tool_result.output
            result.parsed_data = tool_result.parsed_data
            result.status = "completed" if tool_result.status == "completed" else "failed"
            result.completed_at = datetime.now()
            self.db.commit()
            
            await manager.send_tool_output(str(scan.id), "sqlmap", tool_result.output)
            
        except Exception as e:
            logger.error(f"Error running SQLMap scan: {e}")
            if 'result' in locals():
                result.status = "failed"
                result.completed_at = datetime.now()
                self.db.commit()
    
    async def _run_gobuster_scan(self, scan: Scan):
        """Run Gobuster scan"""
        try:
            result = ScanResult(
                scan_id=scan.id,
                tool="gobuster",
                command=f"gobuster dir -u {scan.target} -w /usr/share/wordlists/dirb/common.txt",
                status="running"
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            tool_result = await self.tool_service.run_gobuster(scan.target)
            
            result.output = tool_result.output
            result.parsed_data = tool_result.parsed_data
            result.status = "completed" if tool_result.status == "completed" else "failed"
            result.completed_at = datetime.now()
            self.db.commit()
            
            await manager.send_tool_output(str(scan.id), "gobuster", tool_result.output)
            
        except Exception as e:
            logger.error(f"Error running Gobuster scan: {e}")
            if 'result' in locals():
                result.status = "failed"
                result.completed_at = datetime.now()
                self.db.commit()
    
    async def stop_scan(self, scan_id: int) -> bool:
        """Stop running scan"""
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return False
            
            if scan.status == "running":
                scan.status = "cancelled"
                scan.completed_at = datetime.now()
                self.db.commit()
                
                # Send WebSocket update
                await manager.send_scan_update(str(scan_id), "cancelled", {"message": "Scan cancelled"})
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping scan {scan_id}: {e}")
            return False
    
    async def delete_scan(self, scan_id: int) -> bool:
        """Delete scan and all its results"""
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return False
            
            # Delete scan (cascade will delete results)
            self.db.delete(scan)
            self.db.commit()
            
            logger.info(f"Deleted scan {scan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting scan {scan_id}: {e}")
            self.db.rollback()
            return False
