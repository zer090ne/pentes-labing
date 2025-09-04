"""
Recommendation engine untuk memberikan saran otomatis berdasarkan hasil scan
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

from app.models.scan import Scan, ScanResult, Recommendation
from app.schemas.scan import RecommendationResponse
from app.services.ai_service import AIService


class RecommendationEngine:
    """Engine untuk menghasilkan rekomendasi otomatis"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    async def generate_recommendations(self, scan_id: int) -> List[Dict[str, Any]]:
        """Generate recommendations based on scan results"""
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return []
            
            recommendations = []
            
            # Get all scan results
            results = self.db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
            
            # Generate recommendations based on each tool result
            for result in results:
                if result.tool == "nmap":
                    recommendations.extend(await self._analyze_nmap_results(result))
                elif result.tool == "nikto":
                    recommendations.extend(await self._analyze_nikto_results(result))
                elif result.tool == "hydra":
                    recommendations.extend(await self._analyze_hydra_results(result))
                elif result.tool == "sqlmap":
                    recommendations.extend(await self._analyze_sqlmap_results(result))
                elif result.tool == "gobuster":
                    recommendations.extend(await self._analyze_gobuster_results(result))
            
            # Generate cross-tool recommendations
            recommendations.extend(await self._generate_cross_tool_recommendations(results))
            
            # Generate AI-powered recommendations
            ai_recommendations = await self._generate_ai_recommendations(scan, results)
            recommendations.extend(ai_recommendations)
            
            # Save recommendations to database
            await self._save_recommendations(scan_id, recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for scan {scan_id}: {e}")
            return []
    
    async def _analyze_nmap_results(self, result: ScanResult) -> List[Dict[str, Any]]:
        """Analyze Nmap results and generate recommendations"""
        recommendations = []
        
        if not result.parsed_data:
            return recommendations
        
        data = result.parsed_data
        
        # Analyze open ports
        if "hosts" in data:
            for host in data["hosts"]:
                if "ports" in host:
                    for port in host["ports"]:
                        if port.get("state", {}).get("state") == "open":
                            service = port.get("service", {})
                            service_name = service.get("name", "")
                            port_num = port.get("port", "")
                            
                            # Generate service-specific recommendations
                            if service_name == "ssh":
                                recommendations.append({
                                    "type": "vulnerability",
                                    "title": "SSH Service Detected",
                                    "description": f"SSH service running on port {port_num}",
                                    "priority": "medium",
                                    "action": "Test SSH for weak credentials and configuration issues"
                                })
                            elif service_name == "ftp":
                                recommendations.append({
                                    "type": "vulnerability",
                                    "title": "FTP Service Detected",
                                    "description": f"FTP service running on port {port_num}",
                                    "priority": "high",
                                    "action": "Test FTP for anonymous access and weak credentials"
                                })
                            elif service_name == "http":
                                recommendations.append({
                                    "type": "next_step",
                                    "title": "Web Server Detected",
                                    "description": f"HTTP service running on port {port_num}",
                                    "priority": "medium",
                                    "action": "Run web vulnerability scans (Nikto, SQLMap, Gobuster)"
                                })
                            elif service_name == "mysql":
                                recommendations.append({
                                    "type": "vulnerability",
                                    "title": "MySQL Database Detected",
                                    "description": f"MySQL service running on port {port_num}",
                                    "priority": "high",
                                    "action": "Test MySQL for weak credentials and SQL injection"
                                })
        
        # Analyze OS detection
        if "hosts" in data:
            for host in data["hosts"]:
                if "os" in host and host["os"].get("matches"):
                    os_matches = host["os"]["matches"]
                    if os_matches:
                        best_match = max(os_matches, key=lambda x: int(x.get("accuracy", 0)))
                        recommendations.append({
                            "type": "information",
                            "title": "OS Detection",
                            "description": f"Detected OS: {best_match.get('name', 'Unknown')} (Accuracy: {best_match.get('accuracy', 0)}%)",
                            "priority": "low",
                            "action": "Use OS-specific exploits and techniques"
                        })
        
        return recommendations
    
    async def _analyze_nikto_results(self, result: ScanResult) -> List[Dict[str, Any]]:
        """Analyze Nikto results and generate recommendations"""
        recommendations = []
        
        if not result.parsed_data:
            return recommendations
        
        data = result.parsed_data
        
        # Analyze vulnerabilities
        if "vulnerabilities" in data:
            vulns = data["vulnerabilities"]
            
            # Count by severity
            severity_counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
            for vuln in vulns:
                severity = vuln.get("severity", "info")
                severity_counts[severity] += 1
            
            # Generate severity-based recommendations
            if severity_counts["high"] > 0:
                recommendations.append({
                    "type": "vulnerability",
                    "title": "High Severity Web Vulnerabilities",
                    "description": f"Found {severity_counts['high']} high severity vulnerabilities",
                    "priority": "critical",
                    "action": "Address high severity vulnerabilities immediately"
                })
            
            if severity_counts["medium"] > 0:
                recommendations.append({
                    "type": "vulnerability",
                    "title": "Medium Severity Web Vulnerabilities",
                    "description": f"Found {severity_counts['medium']} medium severity vulnerabilities",
                    "priority": "high",
                    "action": "Address medium severity vulnerabilities promptly"
                })
            
            # Analyze specific vulnerability types
            categories = {}
            for vuln in vulns:
                category = vuln.get("category", "other")
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            # Generate category-specific recommendations
            if categories.get("sql_injection", 0) > 0:
                recommendations.append({
                    "type": "vulnerability",
                    "title": "SQL Injection Vulnerabilities",
                    "description": f"Found {categories['sql_injection']} SQL injection vulnerabilities",
                    "priority": "critical",
                    "action": "Run SQLMap for detailed SQL injection testing"
                })
            
            if categories.get("xss", 0) > 0:
                recommendations.append({
                    "type": "vulnerability",
                    "title": "Cross-Site Scripting (XSS)",
                    "description": f"Found {categories['xss']} XSS vulnerabilities",
                    "priority": "high",
                    "action": "Implement output encoding and Content Security Policy"
                })
        
        return recommendations
    
    async def _analyze_hydra_results(self, result: ScanResult) -> List[Dict[str, Any]]:
        """Analyze Hydra results and generate recommendations"""
        recommendations = []
        
        if not result.parsed_data:
            return recommendations
        
        data = result.parsed_data
        
        # Analyze successful logins
        if "successful_logins" in data:
            successful_logins = data["successful_logins"]
            
            if successful_logins:
                recommendations.append({
                    "type": "vulnerability",
                    "title": "Weak Credentials Found",
                    "description": f"Found {len(successful_logins)} successful logins with weak credentials",
                    "priority": "critical",
                    "action": "Change all weak passwords immediately"
                })
                
                # Analyze by service
                services = {}
                for login in successful_logins:
                    service = login.get("service", "unknown")
                    if service not in services:
                        services[service] = 0
                    services[service] += 1
                
                for service, count in services.items():
                    if service == "ssh":
                        recommendations.append({
                            "type": "mitigation",
                            "title": "SSH Security Hardening",
                            "description": f"SSH brute force successful ({count} times)",
                            "priority": "high",
                            "action": "Implement SSH key-based authentication, disable password auth, use fail2ban"
                        })
                    elif service == "ftp":
                        recommendations.append({
                            "type": "mitigation",
                            "title": "FTP Security Hardening",
                            "description": f"FTP brute force successful ({count} times)",
                            "priority": "high",
                            "action": "Disable anonymous FTP, use strong passwords, consider SFTP"
                        })
        
        return recommendations
    
    async def _analyze_sqlmap_results(self, result: ScanResult) -> List[Dict[str, Any]]:
        """Analyze SQLMap results and generate recommendations"""
        recommendations = []
        
        if not result.parsed_data:
            return recommendations
        
        data = result.parsed_data
        
        # Analyze vulnerabilities
        if "vulnerabilities" in data:
            vulns = data["vulnerabilities"]
            
            if vulns:
                recommendations.append({
                    "type": "vulnerability",
                    "title": "SQL Injection Vulnerabilities Confirmed",
                    "description": f"Confirmed {len(vulns)} SQL injection vulnerabilities",
                    "priority": "critical",
                    "action": "Fix SQL injection vulnerabilities immediately using parameterized queries"
                })
                
                # Analyze vulnerability types
                for vuln in vulns:
                    vuln_type = vuln.get("type", "").lower()
                    
                    if "union query" in vuln_type:
                        recommendations.append({
                            "type": "vulnerability",
                            "title": "Union Query SQL Injection",
                            "description": "Union query SQL injection detected - allows direct data access",
                            "priority": "critical",
                            "action": "Fix immediately - this allows direct database access"
                        })
                    elif "boolean-based blind" in vuln_type:
                        recommendations.append({
                            "type": "vulnerability",
                            "title": "Boolean-Based Blind SQL Injection",
                            "description": "Boolean-based blind SQL injection detected",
                            "priority": "high",
                            "action": "Fix SQL injection and implement proper input validation"
                        })
        
        return recommendations
    
    async def _analyze_gobuster_results(self, result: ScanResult) -> List[Dict[str, Any]]:
        """Analyze Gobuster results and generate recommendations"""
        recommendations = []
        
        if not result.parsed_data:
            return recommendations
        
        data = result.parsed_data
        
        # Analyze found paths
        if "found_directories" in data or "found_files" in data:
            total_found = len(data.get("found_directories", [])) + len(data.get("found_files", []))
            
            if total_found > 0:
                recommendations.append({
                    "type": "information",
                    "title": "Directory Enumeration Results",
                    "description": f"Found {total_found} directories and files",
                    "priority": "low",
                    "action": "Review found paths for sensitive information"
                })
        
        # Analyze interesting paths
        if "summary" in data and "interesting_paths" in data["summary"]:
            interesting_paths = data["summary"]["interesting_paths"]
            
            if interesting_paths:
                # Group by keyword
                keywords = {}
                for path in interesting_paths:
                    keyword = path.get("keyword", "other")
                    if keyword not in keywords:
                        keywords[keyword] = 0
                    keywords[keyword] += 1
                
                # Generate recommendations based on keywords
                if "admin" in keywords:
                    recommendations.append({
                        "type": "next_step",
                        "title": "Admin Panel Found",
                        "description": f"Found {keywords['admin']} admin-related paths",
                        "priority": "medium",
                        "action": "Test admin panels for authentication bypass and weak credentials"
                    })
                
                if "backup" in keywords:
                    recommendations.append({
                        "type": "vulnerability",
                        "title": "Backup Files Found",
                        "description": f"Found {keywords['backup']} backup-related paths",
                        "priority": "high",
                        "action": "Check backup files for sensitive information and remove if not needed"
                    })
                
                if "config" in keywords:
                    recommendations.append({
                        "type": "vulnerability",
                        "title": "Configuration Files Found",
                        "description": f"Found {keywords['config']} configuration-related paths",
                        "priority": "high",
                        "action": "Review configuration files for sensitive information"
                    })
        
        return recommendations
    
    async def _generate_cross_tool_recommendations(self, results: List[ScanResult]) -> List[Dict[str, Any]]:
        """Generate recommendations based on multiple tool results"""
        recommendations = []
        
        # Check if we have both Nmap and Nikto results
        nmap_result = next((r for r in results if r.tool == "nmap"), None)
        nikto_result = next((r for r in results if r.tool == "nikto"), None)
        
        if nmap_result and nikto_result:
            # Check if web server was found by Nmap and vulnerabilities by Nikto
            if nmap_result.parsed_data and nikto_result.parsed_data:
                nmap_data = nmap_result.parsed_data
                nikto_data = nikto_result.parsed_data
                
                # Check for web server in Nmap results
                web_server_found = False
                if "hosts" in nmap_data:
                    for host in nmap_data["hosts"]:
                        if "ports" in host:
                            for port in host["ports"]:
                                service = port.get("service", {})
                                if service.get("name") in ["http", "https"]:
                                    web_server_found = True
                                    break
                
                # Check for vulnerabilities in Nikto results
                vulnerabilities_found = False
                if "vulnerabilities" in nikto_data and nikto_data["vulnerabilities"]:
                    vulnerabilities_found = True
                
                if web_server_found and vulnerabilities_found:
                    recommendations.append({
                        "type": "next_step",
                        "title": "Web Application Security Assessment",
                        "description": "Web server detected with vulnerabilities found",
                        "priority": "high",
                        "action": "Perform comprehensive web application security testing including manual testing"
                    })
        
        return recommendations
    
    async def _save_recommendations(self, scan_id: int, recommendations: List[Dict[str, Any]]):
        """Save recommendations to database"""
        try:
            for rec in recommendations:
                recommendation = Recommendation(
                    scan_id=scan_id,
                    type=rec["type"],
                    title=rec["title"],
                    description=rec["description"],
                    priority=rec["priority"],
                    action=rec.get("action", "")
                )
                self.db.add(recommendation)
            
            self.db.commit()
            logger.info(f"Saved {len(recommendations)} recommendations for scan {scan_id}")
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {e}")
            self.db.rollback()
    
    async def _generate_ai_recommendations(self, scan: Scan, results: List[ScanResult]) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        try:
            # Prepare scan data for AI analysis
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
            
            # Get AI analysis
            ai_analysis = await self.ai_service.analyze_scan_results(scan_data)
            
            if "error" in ai_analysis:
                logger.error(f"AI analysis failed: {ai_analysis['error']}")
                return []
            
            # Convert AI recommendations to our format
            recommendations = []
            
            # Process vulnerability analysis
            for vuln in ai_analysis.get("vulnerability_analysis", []):
                recommendations.append({
                    "type": "vulnerability",
                    "title": f"AI Detected: {vuln.get('vulnerability', 'Unknown Vulnerability')}",
                    "description": vuln.get("description", "AI-identified vulnerability"),
                    "priority": vuln.get("severity", "medium"),
                    "action": f"Address {vuln.get('vulnerability', 'vulnerability')} - {vuln.get('exploitability', 'unknown')} exploitability"
                })
            
            # Process AI recommendations
            for rec in ai_analysis.get("recommendations", []):
                recommendations.append({
                    "type": "ai_recommendation",
                    "title": rec.get("title", "AI Recommendation"),
                    "description": rec.get("description", "AI-generated recommendation"),
                    "priority": rec.get("priority", "medium"),
                    "action": "; ".join(rec.get("action_items", []))
                })
            
            # Process next steps
            for step in ai_analysis.get("next_steps", []):
                recommendations.append({
                    "type": "next_step",
                    "title": f"AI Suggests: {step.get('step', 'Next Step')}",
                    "description": step.get("rationale", "AI-recommended next step"),
                    "priority": "medium",
                    "action": f"Run: {step.get('command', 'N/A')}"
                })
            
            logger.info(f"Generated {len(recommendations)} AI recommendations for scan {scan.id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return []
