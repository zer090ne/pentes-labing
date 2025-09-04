"""
Report endpoints untuk generated reports
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.report import ReportResponse, ReportCreate
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    """Create new report"""
    report_service = ReportService(db)
    report = await report_service.create_report(report_data)
    return report


@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all reports"""
    report_service = ReportService(db)
    return await report_service.get_reports(skip=skip, limit=limit)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get specific report"""
    report_service = ReportService(db)
    report = await report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/download")
async def download_report(report_id: int, db: Session = Depends(get_db)):
    """Download report file"""
    report_service = ReportService(db)
    report = await report_service.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Read file content
    try:
        with open(report.file_path, "rb") as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={report.title}"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report file not found")


@router.get("/scan/{scan_id}", response_model=List[ReportResponse])
async def get_scan_reports(scan_id: int, db: Session = Depends(get_db)):
    """Get all reports for a specific scan"""
    report_service = ReportService(db)
    reports = await report_service.get_scan_reports(scan_id)
    return reports


@router.delete("/{report_id}")
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete report"""
    report_service = ReportService(db)
    success = await report_service.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}
