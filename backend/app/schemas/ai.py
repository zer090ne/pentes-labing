"""
Pydantic schemas untuk AI analysis
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class AIAnalysisRequest(BaseModel):
    """Schema untuk AI analysis request"""
    scan_id: int
    analysis_depth: str = Field(default="detailed", description="basic, detailed, comprehensive")
    include_recommendations: bool = Field(default=True)
    include_risk_assessment: bool = Field(default=True)
    include_attack_vectors: bool = Field(default=True)


class VulnerabilityAnalysis(BaseModel):
    """Schema untuk vulnerability analysis"""
    vulnerability: str
    severity: str
    description: str
    affected_services: List[str] = []
    exploitability: str
    impact: str


class AttackVector(BaseModel):
    """Schema untuk attack vector"""
    vector: str
    likelihood: str
    impact: str
    description: str
    mitigation: str


class AIRecommendation(BaseModel):
    """Schema untuk AI recommendation"""
    priority: str
    category: str
    title: str
    description: str
    action_items: List[str] = []
    estimated_effort: str
    business_impact: str


class NextStep(BaseModel):
    """Schema untuk next step"""
    step: str
    tool: str
    command: str
    rationale: str


class ComplianceNote(BaseModel):
    """Schema untuk compliance note"""
    standard: str
    requirement: str
    status: str
    notes: str


class RiskAssessment(BaseModel):
    """Schema untuk risk assessment"""
    overall_risk_level: str
    risk_score: int = Field(ge=0, le=100)
    summary: str


class AIAnalysisData(BaseModel):
    """Schema untuk AI analysis data"""
    risk_assessment: RiskAssessment
    vulnerability_analysis: List[VulnerabilityAnalysis] = []
    attack_vectors: List[AttackVector] = []
    recommendations: List[AIRecommendation] = []
    next_steps: List[NextStep] = []
    compliance_notes: List[ComplianceNote] = []


class AIAnalysisResponse(BaseModel):
    """Schema untuk AI analysis response"""
    scan_id: int
    analysis: Dict[str, Any]
    generated_at: str
    ai_model: str
    confidence_score: Optional[float] = None


class AIInsights(BaseModel):
    """Schema untuk AI insights"""
    risk_level: str
    risk_score: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    immediate_actions: int
    top_recommendation: Dict[str, Any] = {}
    ai_confidence: int


class AIInsightsResponse(BaseModel):
    """Schema untuk AI insights response"""
    scan_id: int
    insights: Dict[str, Any]
    generated_at: str


class AIReportRequest(BaseModel):
    """Schema untuk AI report request"""
    scan_id: int
    report_type: str = Field(default="html", description="html, pdf, json")
    include_charts: bool = Field(default=True)
    include_executive_summary: bool = Field(default=True)
    include_technical_details: bool = Field(default=True)


class AIReportResponse(BaseModel):
    """Schema untuk AI report response"""
    scan_id: int
    report_content: str
    generated_at: str
    report_type: str
    file_size: Optional[int] = None
