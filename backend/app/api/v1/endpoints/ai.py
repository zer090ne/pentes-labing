"""
AI endpoints untuk analisis dan insights
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from app.core.database import get_db
from app.models.scan import Scan, ScanResult
from app.services.ai_service import AIService
from app.services.recommendation_engine import RecommendationEngine
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse, AIInsightsResponse

router = APIRouter()


@router.post("/analyze/{scan_id}", response_model=AIAnalysisResponse)
async def analyze_scan_with_ai(
    scan_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze scan results with AI"""
    try:
        # Get scan and results
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        results = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
        
        # Prepare scan data
        scan_data = {
            "id": scan.id,
            "name": scan.name,
            "target": scan.target,
            "scan_type": scan.scan_type,
            "status": scan.status,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "results": []
        }
        
        # Add results data
        for result in results:
            result_data = {
                "tool": result.tool,
                "status": result.status,
                "command": result.command,
                "output": result.output,
                "parsed_data": result.parsed_data,
                "created_at": result.created_at.isoformat() if result.created_at else None
            }
            scan_data["results"].append(result_data)
        
        # Run AI analysis
        ai_service = AIService()
        analysis = await ai_service.analyze_scan_results(scan_data)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {analysis['error']}")
        
        return AIAnalysisResponse(
            scan_id=scan_id,
            analysis=analysis,
            generated_at=datetime.now().isoformat(),
            ai_model="groq-llama3-8b-8192"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{scan_id}", response_model=AIInsightsResponse)
async def get_ai_insights(scan_id: int, db: Session = Depends(get_db)):
    """Get AI insights for dashboard"""
    try:
        # Get scan and results
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        results = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
        
        # Prepare scan data
        scan_data = {
            "id": scan.id,
            "name": scan.name,
            "target": scan.target,
            "scan_type": scan.scan_type,
            "status": scan.status,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "results": []
        }
        
        # Add results data
        for result in results:
            result_data = {
                "tool": result.tool,
                "status": result.status,
                "command": result.command,
                "output": result.output,
                "parsed_data": result.parsed_data,
                "created_at": result.created_at.isoformat() if result.created_at else None
            }
            scan_data["results"].append(result_data)
        
        # Get AI insights
        ai_service = AIService()
        insights = await ai_service.get_ai_insights(scan_data)
        
        if "error" in insights:
            raise HTTPException(status_code=500, detail=f"AI insights failed: {insights['error']}")
        
        return AIInsightsResponse(
            scan_id=scan_id,
            insights=insights,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report/{scan_id}")
async def generate_ai_report(
    scan_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate AI-powered report"""
    try:
        # Get scan and results
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        results = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
        
        # Prepare scan data
        scan_data = {
            "id": scan.id,
            "name": scan.name,
            "target": scan.target,
            "scan_type": scan.scan_type,
            "status": scan.status,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "results": []
        }
        
        # Add results data
        for result in results:
            result_data = {
                "tool": result.tool,
                "status": result.status,
                "command": result.command,
                "output": result.output,
                "parsed_data": result.parsed_data,
                "created_at": result.created_at.isoformat() if result.created_at else None
            }
            scan_data["results"].append(result_data)
        
        # Generate AI report
        ai_service = AIService()
        report_content = await ai_service.generate_ai_report(scan_data)
        
        return {
            "scan_id": scan_id,
            "report_content": report_content,
            "generated_at": datetime.now().isoformat(),
            "report_type": "ai_html"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance-recommendations/{scan_id}")
async def enhance_recommendations_with_ai(
    scan_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enhance existing recommendations with AI analysis"""
    try:
        # Get scan
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Generate enhanced recommendations
        recommendation_engine = RecommendationEngine(db)
        recommendations = await recommendation_engine.generate_recommendations(scan_id)
        
        return {
            "scan_id": scan_id,
            "recommendations": recommendations,
            "enhanced_at": datetime.now().isoformat(),
            "ai_enhanced": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_ai_status():
    """Get AI service status"""
    try:
        ai_service = AIService()
        is_available = ai_service.client is not None
        
        return {
            "ai_enabled": is_available,
            "model": "groq-llama3-8b-8192" if is_available else None,
            "status": "available" if is_available else "unavailable",
            "features": [
                "vulnerability_analysis",
                "risk_assessment", 
                "recommendation_generation",
                "report_generation",
                "insights_extraction"
            ] if is_available else []
        }
        
    except Exception as e:
        return {
            "ai_enabled": False,
            "status": "error",
            "error": str(e)
        }
