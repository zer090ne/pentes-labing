"""
Main API router untuk v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import scans, tools, reports, auth, ai

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai-analysis"])
