"""
SQLMap wrapper untuk SQL injection testing
"""

import asyncio
import subprocess
import json
import re
from typing import Dict, Any, List
from loguru import logger


class SqlmapWrapper:
    """Wrapper untuk SQLMap SQL injection testing tool"""
    
    def __init__(self):
        self.tool_name = "sqlmap"
    
    async def test(self, url: str, options: str = "--forms --batch") -> Dict[str, Any]:
        """Run SQLMap SQL injection test"""
        try:
            # Build command
            command = ["sqlmap", "-u", url]
            if options:
                command.extend(options.split())
            
            # Add JSON output
            command.extend(["--output-dir", "/tmp/sqlmap_output"])
            
            logger.info(f"Running SQLMap command: {' '.join(command)}")
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode()
            error_output = stderr.decode()
            
            # Parse results
            parsed_data = self._parse_sqlmap_output(output, error_output)
            
            return {
                "output": output,
                "error_output": error_output,
                "parsed_data": parsed_data,
                "success": "vulnerable" in output.lower() or "injection" in output.lower(),
                "return_code": process.returncode
            }
            
        except Exception as e:
            logger.error(f"SQLMap test error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
    
    def _parse_sqlmap_output(self, output: str, error_output: str) -> Dict[str, Any]:
        """Parse SQLMap output"""
        try:
            result = {
                "target": "",
                "vulnerabilities": [],
                "injection_points": [],
                "database_info": {},
                "summary": {}
            }
            
            lines = output.split('\n')
            current_vulnerability = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse target URL
                if line.startswith("[INFO] testing URL:"):
                    result["target"] = line.split(":", 1)[1].strip()
                
                # Parse vulnerability detection
                elif "sqlmap identified the following injection point(s)" in line.lower():
                    current_vulnerability = {"type": "injection_point", "details": []}
                    result["vulnerabilities"].append(current_vulnerability)
                
                # Parse injection point details
                elif current_vulnerability and "Parameter:" in line:
                    param_match = re.search(r'Parameter: ([^(]+)', line)
                    if param_match:
                        current_vulnerability["parameter"] = param_match.group(1).strip()
                
                elif current_vulnerability and "Type:" in line:
                    type_match = re.search(r'Type: ([^(]+)', line)
                    if type_match:
                        current_vulnerability["type"] = type_match.group(1).strip()
                
                elif current_vulnerability and "Title:" in line:
                    title_match = re.search(r'Title: ([^(]+)', line)
                    if title_match:
                        current_vulnerability["title"] = title_match.group(1).strip()
                
                # Parse database information
                elif "web server operating system:" in line.lower():
                    os_match = re.search(r'web server operating system: (.+)', line, re.IGNORECASE)
                    if os_match:
                        result["database_info"]["web_server_os"] = os_match.group(1).strip()
                
                elif "web application technology:" in line.lower():
                    tech_match = re.search(r'web application technology: (.+)', line, re.IGNORECASE)
                    if tech_match:
                        result["database_info"]["web_technology"] = tech_match.group(1).strip()
                
                elif "back-end DBMS:" in line.lower():
                    dbms_match = re.search(r'back-end DBMS: (.+)', line, re.IGNORECASE)
                    if dbms_match:
                        result["database_info"]["dbms"] = dbms_match.group(1).strip()
                
                # Parse injection types
                elif "Payload:" in line:
                    payload_match = re.search(r'Payload: (.+)', line)
                    if payload_match:
                        if "injection_points" not in current_vulnerability:
                            current_vulnerability["injection_points"] = []
                        current_vulnerability["injection_points"].append(payload_match.group(1).strip())
            
            # Generate summary
            result["summary"] = self._generate_summary(result)
            
            return result
            
        except Exception as e:
            logger.error(f"SQLMap output parsing error: {e}")
            return {"error": f"Output parsing failed: {e}"}
    
    def _generate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        summary = {
            "total_vulnerabilities": len(result["vulnerabilities"]),
            "vulnerability_types": [],
            "risk_level": "low",
            "recommendations": []
        }
        
        # Analyze vulnerability types
        for vuln in result["vulnerabilities"]:
            vuln_type = vuln.get("type", "unknown")
            if vuln_type not in summary["vulnerability_types"]:
                summary["vulnerability_types"].append(vuln_type)
        
        # Determine risk level
        if any("boolean-based blind" in str(vuln).lower() for vuln in result["vulnerabilities"]):
            summary["risk_level"] = "high"
        elif any("time-based blind" in str(vuln).lower() for vuln in result["vulnerabilities"]):
            summary["risk_level"] = "medium"
        elif result["vulnerabilities"]:
            summary["risk_level"] = "medium"
        
        # Generate recommendations
        summary["recommendations"] = self._generate_recommendations(result)
        
        return summary
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if result["vulnerabilities"]:
            recommendations.append({
                "priority": "critical",
                "title": "SQL Injection Vulnerabilities Found",
                "description": f"Found {len(result['vulnerabilities'])} SQL injection vulnerabilities.",
                "action": "Implement parameterized queries and input validation immediately"
            })
            
            # Specific recommendations based on vulnerability types
            for vuln in result["vulnerabilities"]:
                vuln_type = vuln.get("type", "").lower()
                
                if "boolean-based blind" in vuln_type:
                    recommendations.append({
                        "priority": "high",
                        "title": "Boolean-Based Blind SQL Injection",
                        "description": "Boolean-based blind SQL injection detected. This allows data extraction.",
                        "action": "Fix SQL injection in parameter and implement proper input validation"
                    })
                
                elif "time-based blind" in vuln_type:
                    recommendations.append({
                        "priority": "high",
                        "title": "Time-Based Blind SQL Injection",
                        "description": "Time-based blind SQL injection detected. This allows data extraction.",
                        "action": "Fix SQL injection in parameter and implement proper input validation"
                    })
                
                elif "union query" in vuln_type:
                    recommendations.append({
                        "priority": "critical",
                        "title": "Union Query SQL Injection",
                        "description": "Union query SQL injection detected. This allows direct data access.",
                        "action": "Fix SQL injection immediately and review all database queries"
                    })
        
        # Database-specific recommendations
        if result["database_info"].get("dbms"):
            dbms = result["database_info"]["dbms"].lower()
            if "mysql" in dbms:
                recommendations.append({
                    "priority": "medium",
                    "title": "MySQL Database Detected",
                    "description": "MySQL database is being used.",
                    "action": "Ensure MySQL is properly configured and updated"
                })
            elif "postgresql" in dbms:
                recommendations.append({
                    "priority": "medium",
                    "title": "PostgreSQL Database Detected",
                    "description": "PostgreSQL database is being used.",
                    "action": "Ensure PostgreSQL is properly configured and updated"
                })
        
        # General recommendations
        recommendations.append({
            "priority": "high",
            "title": "General SQL Injection Prevention",
            "description": "Implement comprehensive SQL injection prevention measures.",
            "action": "Use parameterized queries, input validation, least privilege database access, and WAF"
        })
        
        return recommendations
    
    async def test_with_forms(self, url: str, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Test SQL injection with specific form data"""
        try:
            # Build command with form data
            command = ["sqlmap", "-u", url, "--forms", "--batch"]
            
            # Add form data if provided
            if form_data:
                for key, value in form_data.items():
                    command.extend(["-p", key])
            
            logger.info(f"Running SQLMap with forms: {' '.join(command)}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode()
            error_output = stderr.decode()
            
            parsed_data = self._parse_sqlmap_output(output, error_output)
            
            return {
                "output": output,
                "error_output": error_output,
                "parsed_data": parsed_data,
                "success": "vulnerable" in output.lower(),
                "return_code": process.returncode
            }
            
        except Exception as e:
            logger.error(f"SQLMap form test error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
