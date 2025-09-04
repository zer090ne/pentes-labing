"""
Nikto wrapper untuk web vulnerability scanning
"""

import asyncio
import subprocess
import re
import json
from typing import Dict, Any, List
from loguru import logger


class NiktoWrapper:
    """Wrapper untuk Nikto web vulnerability scanner"""
    
    def __init__(self):
        self.tool_name = "nikto"
    
    async def scan(self, target: str, options: str = "") -> Dict[str, Any]:
        """Run Nikto scan"""
        try:
            # Build command
            command = ["nikto", "-h", target]
            if options:
                command.extend(options.split())
            
            # Add output format
            command.extend(["-Format", "txt"])
            
            logger.info(f"Running Nikto command: {' '.join(command)}")
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Nikto failed: {error_msg}")
                return {
                    "output": error_msg,
                    "parsed_data": {},
                    "error": error_msg
                }
            
            # Parse output
            output = stdout.decode()
            parsed_data = self._parse_nikto_output(output)
            
            return {
                "output": output,
                "parsed_data": parsed_data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Nikto scan error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
    
    def _parse_nikto_output(self, output: str) -> Dict[str, Any]:
        """Parse Nikto output"""
        try:
            result = {
                "target": "",
                "scan_info": {},
                "vulnerabilities": [],
                "summary": {}
            }
            
            lines = output.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse target info
                if line.startswith("- Nikto v"):
                    result["scan_info"]["version"] = line.split()[2]
                elif line.startswith("+ Target IP:"):
                    result["target"] = line.split(":")[1].strip()
                elif line.startswith("+ Target Hostname:"):
                    result["scan_info"]["hostname"] = line.split(":")[1].strip()
                elif line.startswith("+ Target Port:"):
                    result["scan_info"]["port"] = line.split(":")[1].strip()
                elif line.startswith("+ Start Time:"):
                    result["scan_info"]["start_time"] = line.split(":", 1)[1].strip()
                elif line.startswith("+ End Time:"):
                    result["scan_info"]["end_time"] = line.split(":", 1)[1].strip()
                
                # Parse vulnerabilities
                elif line.startswith("+ "):
                    vuln = self._parse_vulnerability_line(line)
                    if vuln:
                        result["vulnerabilities"].append(vuln)
            
            # Generate summary
            result["summary"] = self._generate_summary(result["vulnerabilities"])
            
            return result
            
        except Exception as e:
            logger.error(f"Nikto output parsing error: {e}")
            return {"error": f"Output parsing failed: {e}"}
    
    def _parse_vulnerability_line(self, line: str) -> Dict[str, Any]:
        """Parse individual vulnerability line"""
        try:
            # Remove the "+ " prefix
            content = line[2:]
            
            # Extract URL and description
            if " - " in content:
                url, description = content.split(" - ", 1)
                url = url.strip()
                description = description.strip()
            else:
                url = ""
                description = content
            
            # Determine severity based on keywords
            severity = self._determine_severity(description)
            
            # Extract CVE if present
            cve_match = re.search(r'CVE-\d{4}-\d{4,7}', description)
            cve = cve_match.group() if cve_match else None
            
            return {
                "url": url,
                "description": description,
                "severity": severity,
                "cve": cve,
                "category": self._categorize_vulnerability(description)
            }
            
        except Exception as e:
            logger.error(f"Vulnerability parsing error: {e}")
            return None
    
    def _determine_severity(self, description: str) -> str:
        """Determine vulnerability severity"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in [
            "critical", "remote code execution", "rce", "buffer overflow",
            "sql injection", "xss", "cross-site scripting"
        ]):
            return "high"
        elif any(keyword in description_lower for keyword in [
            "information disclosure", "directory traversal", "path traversal",
            "authentication bypass", "privilege escalation"
        ]):
            return "medium"
        elif any(keyword in description_lower for keyword in [
            "information", "version", "banner", "header"
        ]):
            return "low"
        else:
            return "info"
    
    def _categorize_vulnerability(self, description: str) -> str:
        """Categorize vulnerability type"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in [
            "sql injection", "sqlmap", "database"
        ]):
            return "sql_injection"
        elif any(keyword in description_lower for keyword in [
            "xss", "cross-site scripting", "script"
        ]):
            return "xss"
        elif any(keyword in description_lower for keyword in [
            "directory", "path", "traversal"
        ]):
            return "directory_traversal"
        elif any(keyword in description_lower for keyword in [
            "authentication", "login", "password"
        ]):
            return "authentication"
        elif any(keyword in description_lower for keyword in [
            "ssl", "tls", "certificate", "https"
        ]):
            return "ssl_tls"
        elif any(keyword in description_lower for keyword in [
            "server", "version", "banner"
        ]):
            return "information_disclosure"
        else:
            return "other"
    
    def _generate_summary(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scan summary"""
        summary = {
            "total_vulnerabilities": len(vulnerabilities),
            "severity_counts": {
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            },
            "category_counts": {},
            "cve_count": 0,
            "recommendations": []
        }
        
        # Count by severity
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "info")
            summary["severity_counts"][severity] += 1
            
            # Count by category
            category = vuln.get("category", "other")
            if category not in summary["category_counts"]:
                summary["category_counts"][category] = 0
            summary["category_counts"][category] += 1
            
            # Count CVEs
            if vuln.get("cve"):
                summary["cve_count"] += 1
        
        # Generate recommendations
        summary["recommendations"] = self._generate_recommendations(summary)
        
        return summary
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        # High severity recommendations
        if summary["severity_counts"]["high"] > 0:
            recommendations.append({
                "priority": "critical",
                "title": "High Severity Vulnerabilities Found",
                "description": f"Found {summary['severity_counts']['high']} high severity vulnerabilities. Immediate attention required.",
                "action": "Review and patch high severity vulnerabilities immediately"
            })
        
        # SQL Injection recommendations
        if summary["category_counts"].get("sql_injection", 0) > 0:
            recommendations.append({
                "priority": "high",
                "title": "SQL Injection Vulnerabilities",
                "description": "SQL injection vulnerabilities detected. This can lead to data breach.",
                "action": "Implement parameterized queries and input validation"
            })
        
        # XSS recommendations
        if summary["category_counts"].get("xss", 0) > 0:
            recommendations.append({
                "priority": "high",
                "title": "Cross-Site Scripting (XSS)",
                "description": "XSS vulnerabilities detected. This can lead to session hijacking.",
                "action": "Implement output encoding and Content Security Policy (CSP)"
            })
        
        # SSL/TLS recommendations
        if summary["category_counts"].get("ssl_tls", 0) > 0:
            recommendations.append({
                "priority": "medium",
                "title": "SSL/TLS Issues",
                "description": "SSL/TLS configuration issues detected.",
                "action": "Update SSL/TLS configuration and certificates"
            })
        
        # Information disclosure recommendations
        if summary["category_counts"].get("information_disclosure", 0) > 0:
            recommendations.append({
                "priority": "low",
                "title": "Information Disclosure",
                "description": "Server information is being disclosed.",
                "action": "Hide server version and banner information"
            })
        
        return recommendations
