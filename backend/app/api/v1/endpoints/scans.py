"""
Scan endpoints untuk API
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.scan import Scan, ScanResult, Recommendation
from app.schemas.scan import ScanCreate, ScanResponse, ScanResultResponse
from app.services.scan_service import ScanService
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create new scan"""
    scan_service = ScanService(db)
    scan = await scan_service.create_scan(scan_data)
    
    # Start scan in background
    background_tasks.add_task(scan_service.run_scan, scan.id)
    
    return scan


@router.get("/", response_model=List[ScanResponse])
async def get_scans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all scans"""
    scan_service = ScanService(db)
    return await scan_service.get_scans(skip=skip, limit=limit)


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    """Get specific scan"""
    scan_service = ScanService(db)
    scan = await scan_service.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/results", response_model=List[ScanResultResponse])
async def get_scan_results(scan_id: int, db: Session = Depends(get_db)):
    """Get scan results"""
    scan_service = ScanService(db)
    results = await scan_service.get_scan_results(scan_id)
    return results


@router.post("/{scan_id}/stop")
async def stop_scan(scan_id: int, db: Session = Depends(get_db)):
    """Stop running scan"""
    scan_service = ScanService(db)
    success = await scan_service.stop_scan(scan_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop scan")
    return {"message": "Scan stopped successfully"}


@router.delete("/{scan_id}")
async def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    """Delete scan and all its results"""
    scan_service = ScanService(db)
    success = await scan_service.delete_scan(scan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"message": "Scan deleted successfully"}


@router.get("/{scan_id}/recommendations")
async def get_recommendations(scan_id: int, db: Session = Depends(get_db)):
    """Get automated recommendations for scan"""
    scan_service = ScanService(db)
    scan = await scan_service.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Generate recommendations
    recommendation_engine = RecommendationEngine(db)
    recommendations = await recommendation_engine.generate_recommendations(scan_id)
    
    return recommendations
