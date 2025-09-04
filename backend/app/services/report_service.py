"""
Report service untuk generated reports
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import json
from loguru import logger

from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse


class ReportService:
    """Service untuk mengelola reports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_report(self, report_data: ReportCreate) -> ReportResponse:
        """Create new report"""
        try:
            # Generate report content based on scan results
            content = await self._generate_report_content(report_data.scan_id, report_data.report_type)
            
            # Generate file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{report_data.scan_id}_{timestamp}.{report_data.report_type}"
            file_path = os.path.join("reports", filename)
            
            # Create report record
            report = Report(
                scan_id=report_data.scan_id,
                report_type=report_data.report_type.value,
                title=report_data.title,
                file_path=file_path,
                content=content
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            # Save report to file
            await self._save_report_to_file(file_path, content, report_data.report_type)
            
            logger.info(f"Created report: {report.id} - {report.title}")
            
            return ReportResponse.from_orm(report)
            
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            self.db.rollback()
            raise
    
    async def get_reports(self, skip: int = 0, limit: int = 100) -> List[ReportResponse]:
        """Get all reports"""
        try:
            reports = self.db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
            return [ReportResponse.from_orm(report) for report in reports]
        except Exception as e:
            logger.error(f"Error getting reports: {e}")
            return []
    
    async def get_report(self, report_id: int) -> Optional[ReportResponse]:
        """Get specific report"""
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if report:
                return ReportResponse.from_orm(report)
            return None
        except Exception as e:
            logger.error(f"Error getting report {report_id}: {e}")
            return None
    
    async def get_scan_reports(self, scan_id: int) -> List[ReportResponse]:
        """Get all reports for a specific scan"""
        try:
            reports = self.db.query(Report).filter(Report.scan_id == scan_id).all()
            return [ReportResponse.from_orm(report) for report in reports]
        except Exception as e:
            logger.error(f"Error getting scan reports for {scan_id}: {e}")
            return []
    
    async def delete_report(self, report_id: int) -> bool:
        """Delete report"""
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return False
            
            # Delete file if exists
            if report.file_path and os.path.exists(report.file_path):
                os.remove(report.file_path)
            
            # Delete report record
            self.db.delete(report)
            self.db.commit()
            
            logger.info(f"Deleted report {report_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting report {report_id}: {e}")
            self.db.rollback()
            return False
    
    async def _generate_report_content(self, scan_id: int, report_type: str) -> str:
        """Generate report content based on scan results"""
        try:
            # Get scan and results
            from app.models.scan import Scan, ScanResult, Recommendation
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return "Scan not found"
            
            results = self.db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
            recommendations = self.db.query(Recommendation).filter(Recommendation.scan_id == scan_id).all()
            
            if report_type == "html":
                return await self._generate_html_report(scan, results, recommendations)
            elif report_type == "json":
                return await self._generate_json_report(scan, results, recommendations)
            else:
                return await self._generate_text_report(scan, results, recommendations)
                
        except Exception as e:
            logger.error(f"Error generating report content: {e}")
            return f"Error generating report: {e}"
    
    async def _generate_html_report(self, scan, results, recommendations) -> str:
        """Generate HTML report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pentest Report - {scan.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .vulnerability {{ background-color: #ffe6e6; padding: 10px; margin: 10px 0; border-left: 4px solid #ff0000; }}
                .recommendation {{ background-color: #e6f3ff; padding: 10px; margin: 10px 0; border-left: 4px solid #0066cc; }}
                .info {{ background-color: #f0f8f0; padding: 10px; margin: 10px 0; border-left: 4px solid #00cc00; }}
                .code {{ background-color: #f5f5f5; padding: 10px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Pentest Report</h1>
                <h2>{scan.name}</h2>
                <p><strong>Target:</strong> {scan.target}</p>
                <p><strong>Scan Type:</strong> {scan.scan_type}</p>
                <p><strong>Date:</strong> {scan.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Status:</strong> {scan.status}</p>
            </div>
            
            <div class="section">
                <h3>Scan Results</h3>
        """
        
        for result in results:
            html += f"""
                <div class="info">
                    <h4>{result.tool.upper()} Results</h4>
                    <p><strong>Command:</strong> <code>{result.command}</code></p>
                    <p><strong>Status:</strong> {result.status}</p>
                    <p><strong>Output:</strong></p>
                    <div class="code">{result.output[:1000]}{'...' if len(result.output) > 1000 else ''}</div>
                </div>
            """
        
        html += """
            </div>
            
            <div class="section">
                <h3>Recommendations</h3>
        """
        
        for rec in recommendations:
            priority_class = "vulnerability" if rec.priority in ["high", "critical"] else "recommendation"
            html += f"""
                <div class="{priority_class}">
                    <h4>{rec.title}</h4>
                    <p><strong>Priority:</strong> {rec.priority.upper()}</p>
                    <p><strong>Description:</strong> {rec.description}</p>
                    <p><strong>Action:</strong> {rec.action}</p>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def _generate_json_report(self, scan, results, recommendations) -> str:
        """Generate JSON report"""
        report_data = {
            "scan": {
                "id": scan.id,
                "name": scan.name,
                "target": scan.target,
                "scan_type": scan.scan_type,
                "status": scan.status,
                "created_at": scan.created_at.isoformat(),
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None
            },
            "results": [
                {
                    "id": result.id,
                    "tool": result.tool,
                    "command": result.command,
                    "status": result.status,
                    "output": result.output,
                    "parsed_data": result.parsed_data,
                    "created_at": result.created_at.isoformat(),
                    "completed_at": result.completed_at.isoformat() if result.completed_at else None
                }
                for result in results
            ],
            "recommendations": [
                {
                    "id": rec.id,
                    "type": rec.type,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "action": rec.action,
                    "created_at": rec.created_at.isoformat()
                }
                for rec in recommendations
            ]
        }
        
        return json.dumps(report_data, indent=2)
    
    async def _generate_text_report(self, scan, results, recommendations) -> str:
        """Generate text report"""
        text = f"""
PENTEST REPORT
==============

Scan Information:
- Name: {scan.name}
- Target: {scan.target}
- Type: {scan.scan_type}
- Status: {scan.status}
- Date: {scan.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Scan Results:
=============
"""
        
        for result in results:
            text += f"""
{result.tool.upper()} Results:
- Command: {result.command}
- Status: {result.status}
- Output: {result.output[:500]}{'...' if len(result.output) > 500 else ''}
"""
        
        text += """
Recommendations:
===============
"""
        
        for rec in recommendations:
            text += f"""
- {rec.title} ({rec.priority.upper()})
  Description: {rec.description}
  Action: {rec.action}
"""
        
        return text
    
    async def _save_report_to_file(self, file_path: str, content: str, report_type: str):
        """Save report content to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved report to file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving report to file {file_path}: {e}")
            raise
