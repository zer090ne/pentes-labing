"""
AI Service untuk analisis hasil scan menggunakan Groq API
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from groq import Groq
from loguru import logger
from app.core.config import settings


class AIService:
    """Service untuk analisis AI menggunakan Groq"""
    
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY and settings.AI_ENABLED:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("Groq AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
    
    async def analyze_scan_results(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisis hasil scan dengan AI"""
        if not self.client:
            return {"error": "AI service not available"}
        
        try:
            # Prepare context untuk AI
            context = self._prepare_scan_context(scan_data)
            
            # Generate AI prompt
            prompt = self._generate_analysis_prompt(context)
            
            # Call Groq API
            response = await self._call_groq_api(prompt)
            
            # Parse response
            analysis = self._parse_ai_response(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def _prepare_scan_context(self, scan_data: Dict[str, Any]) -> str:
        """Prepare context data untuk AI analysis"""
        context = {
            "scan_info": {
                "target": scan_data.get("target", ""),
                "scan_type": scan_data.get("scan_type", ""),
                "status": scan_data.get("status", ""),
                "created_at": scan_data.get("created_at", "")
            },
            "results": []
        }
        
        # Process scan results
        for result in scan_data.get("results", []):
            result_context = {
                "tool": result.get("tool", ""),
                "status": result.get("status", ""),
                "command": result.get("command", ""),
                "parsed_data": result.get("parsed_data", {}),
                "output_summary": result.get("output", "")[:1000] if result.get("output") else ""
            }
            context["results"].append(result_context)
        
        return json.dumps(context, indent=2)
    
    def _generate_analysis_prompt(self, context: str) -> str:
        """Generate prompt untuk AI analysis"""
        return f"""
Anda adalah seorang cybersecurity expert yang menganalisis hasil penetration testing. 
Berdasarkan data scan berikut, berikan analisis mendalam dan rekomendasi yang actionable.

Data Scan:
{context}

Tolong berikan analisis dalam format JSON dengan struktur berikut:
{{
    "risk_assessment": {{
        "overall_risk_level": "low|medium|high|critical",
        "risk_score": 0-100,
        "summary": "Ringkasan singkat tentang tingkat risiko"
    }},
    "vulnerability_analysis": [
        {{
            "vulnerability": "Nama vulnerability",
            "severity": "low|medium|high|critical",
            "description": "Deskripsi detail",
            "affected_services": ["service1", "service2"],
            "exploitability": "easy|moderate|difficult|impossible",
            "impact": "low|medium|high|critical"
        }}
    ],
    "attack_vectors": [
        {{
            "vector": "Nama attack vector",
            "likelihood": "low|medium|high",
            "impact": "low|medium|high|critical",
            "description": "Deskripsi cara serangan",
            "mitigation": "Cara mitigasi"
        }}
    ],
    "recommendations": [
        {{
            "priority": "immediate|high|medium|low",
            "category": "network|web|system|authentication",
            "title": "Judul rekomendasi",
            "description": "Deskripsi detail",
            "action_items": ["action1", "action2"],
            "estimated_effort": "low|medium|high",
            "business_impact": "low|medium|high"
        }}
    ],
    "next_steps": [
        {{
            "step": "Langkah selanjutnya",
            "tool": "Tool yang disarankan",
            "command": "Command yang bisa dijalankan",
            "rationale": "Alasan mengapa langkah ini penting"
        }}
    ],
    "compliance_notes": [
        {{
            "standard": "Nama standar compliance",
            "requirement": "Requirement yang relevan",
            "status": "compliant|non-compliant|partial",
            "notes": "Catatan tambahan"
        }}
    ]
}}

Fokus pada:
1. Identifikasi vulnerability yang paling kritis
2. Analisis attack surface yang paling berisiko
3. Rekomendasi yang praktis dan actionable
4. Prioritas berdasarkan business impact
5. Langkah-langkah testing selanjutnya yang efektif

Berikan analisis yang mendalam, akurat, dan praktis untuk penetration tester.
"""
    
    async def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API untuk analisis"""
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Anda adalah cybersecurity expert dengan pengalaman 10+ tahun dalam penetration testing dan vulnerability assessment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
                top_p=1,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response dan extract JSON"""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            analysis = json.loads(json_str)
            
            # Validate structure
            required_keys = ["risk_assessment", "vulnerability_analysis", "recommendations"]
            for key in required_keys:
                if key not in analysis:
                    analysis[key] = []
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return {
                "error": "Failed to parse AI analysis",
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                "error": f"Error parsing AI response: {str(e)}",
                "raw_response": response
            }
    
    async def generate_ai_report(self, scan_data: Dict[str, Any]) -> str:
        """Generate AI-powered report"""
        if not self.client:
            return "AI service not available"
        
        try:
            analysis = await self.analyze_scan_results(scan_data)
            
            if "error" in analysis:
                return f"AI Analysis Error: {analysis['error']}"
            
            # Generate report content
            report = self._format_ai_report(analysis, scan_data)
            
            return report
            
        except Exception as e:
            logger.error(f"AI report generation failed: {e}")
            return f"AI Report Generation Error: {str(e)}"
    
    def _format_ai_report(self, analysis: Dict[str, Any], scan_data: Dict[str, Any]) -> str:
        """Format AI analysis menjadi report HTML"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI-Powered Security Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #667eea; background: #f8f9fa; }}
        .risk-high {{ border-left-color: #dc3545; }}
        .risk-medium {{ border-left-color: #ffc107; }}
        .risk-low {{ border-left-color: #28a745; }}
        .vulnerability {{ background: #fff; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .recommendation {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .metric {{ display: inline-block; background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; margin: 5px; }}
        .critical {{ background: #dc3545; }}
        .high {{ background: #fd7e14; }}
        .medium {{ background: #ffc107; color: #000; }}
        .low {{ background: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI-Powered Security Analysis Report</h1>
        <h2>Target: {scan_data.get('target', 'N/A')}</h2>
        <p>Generated by AI Security Analyst • {scan_data.get('created_at', 'N/A')}</p>
    </div>
"""
        
        # Risk Assessment
        risk_assessment = analysis.get("risk_assessment", {})
        risk_level = risk_assessment.get("overall_risk_level", "unknown")
        risk_score = risk_assessment.get("risk_score", 0)
        
        html += f"""
    <div class="section risk-{risk_level}">
        <h2>📊 Risk Assessment</h2>
        <div class="metric {risk_level}">Risk Level: {risk_level.upper()}</div>
        <div class="metric">Risk Score: {risk_score}/100</div>
        <p><strong>Summary:</strong> {risk_assessment.get('summary', 'No summary available')}</p>
    </div>
"""
        
        # Vulnerability Analysis
        vulnerabilities = analysis.get("vulnerability_analysis", [])
        if vulnerabilities:
            html += """
    <div class="section">
        <h2>🔍 Vulnerability Analysis</h2>
"""
            for vuln in vulnerabilities:
                severity = vuln.get("severity", "unknown")
                html += f"""
        <div class="vulnerability">
            <h3>{vuln.get('vulnerability', 'Unknown Vulnerability')}</h3>
            <div class="metric {severity}">Severity: {severity.upper()}</div>
            <p><strong>Description:</strong> {vuln.get('description', 'No description')}</p>
            <p><strong>Affected Services:</strong> {', '.join(vuln.get('affected_services', []))}</p>
            <p><strong>Exploitability:</strong> {vuln.get('exploitability', 'Unknown')}</p>
            <p><strong>Impact:</strong> {vuln.get('impact', 'Unknown')}</p>
        </div>
"""
            html += "</div>"
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            html += """
    <div class="section">
        <h2>💡 AI Recommendations</h2>
"""
            for rec in recommendations:
                priority = rec.get("priority", "medium")
                html += f"""
        <div class="recommendation">
            <h3>{rec.get('title', 'Recommendation')}</h3>
            <div class="metric {priority}">Priority: {priority.upper()}</div>
            <p><strong>Description:</strong> {rec.get('description', 'No description')}</p>
            <p><strong>Category:</strong> {rec.get('category', 'General')}</p>
            <p><strong>Action Items:</strong></p>
            <ul>
"""
                for action in rec.get("action_items", []):
                    html += f"<li>{action}</li>"
                
                html += f"""
            </ul>
            <p><strong>Estimated Effort:</strong> {rec.get('estimated_effort', 'Unknown')}</p>
            <p><strong>Business Impact:</strong> {rec.get('business_impact', 'Unknown')}</p>
        </div>
"""
            html += "</div>"
        
        # Next Steps
        next_steps = analysis.get("next_steps", [])
        if next_steps:
            html += """
    <div class="section">
        <h2>🎯 Recommended Next Steps</h2>
        <ol>
"""
            for step in next_steps:
                html += f"""
            <li>
                <strong>{step.get('step', 'Next Step')}</strong><br>
                <em>Tool:</em> {step.get('tool', 'N/A')}<br>
                <em>Command:</em> <code>{step.get('command', 'N/A')}</code><br>
                <em>Rationale:</em> {step.get('rationale', 'No rationale provided')}
            </li>
"""
            html += """
        </ol>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        return html
    
    async def get_ai_insights(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI insights untuk dashboard"""
        if not self.client:
            return {"error": "AI service not available"}
        
        try:
            analysis = await self.analyze_scan_results(scan_data)
            
            if "error" in analysis:
                return analysis
            
            # Extract key insights
            insights = {
                "risk_level": analysis.get("risk_assessment", {}).get("overall_risk_level", "unknown"),
                "risk_score": analysis.get("risk_assessment", {}).get("risk_score", 0),
                "critical_vulnerabilities": len([v for v in analysis.get("vulnerability_analysis", []) if v.get("severity") == "critical"]),
                "high_vulnerabilities": len([v for v in analysis.get("vulnerability_analysis", []) if v.get("severity") == "high"]),
                "immediate_actions": len([r for r in analysis.get("recommendations", []) if r.get("priority") == "immediate"]),
                "top_recommendation": analysis.get("recommendations", [{}])[0] if analysis.get("recommendations") else {},
                "ai_confidence": 85  # Placeholder - bisa dihitung dari response quality
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {"error": f"AI insights failed: {str(e)}"}
