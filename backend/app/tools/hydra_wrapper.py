"""
Hydra wrapper untuk brute force attacks
"""

import asyncio
import subprocess
import re
import json
from typing import Dict, Any, List
from loguru import logger


class HydraWrapper:
    """Wrapper untuk Hydra brute force tool"""
    
    def __init__(self):
        self.tool_name = "hydra"
    
    async def attack(self, target: str, service: str, username: str = "admin", 
                    password_list: str = "/usr/share/wordlists/rockyou.txt") -> Dict[str, Any]:
        """Run Hydra brute force attack"""
        try:
            # Build command
            command = [
                "hydra",
                "-l", username,
                "-P", password_list,
                f"{service}://{target}",
                "-t", "4",  # Threads
                "-V",       # Verbose
                "-f"        # Stop on first success
            ]
            
            logger.info(f"Running Hydra command: {' '.join(command)}")
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Hydra returns 0 on success, 1 on failure, 2 on error
            output = stdout.decode()
            error_output = stderr.decode()
            
            # Parse results
            parsed_data = self._parse_hydra_output(output, error_output)
            
            return {
                "output": output,
                "error_output": error_output,
                "parsed_data": parsed_data,
                "success": process.returncode == 0,
                "return_code": process.returncode
            }
            
        except Exception as e:
            logger.error(f"Hydra attack error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
    
    def _parse_hydra_output(self, output: str, error_output: str) -> Dict[str, Any]:
        """Parse Hydra output"""
        try:
            result = {
                "target": "",
                "service": "",
                "username": "",
                "successful_logins": [],
                "failed_attempts": 0,
                "summary": {}
            }
            
            # Parse successful logins from output
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for successful login pattern
                # Example: [80][http-post-form] host: 192.168.1.100   login: admin   password: admin
                login_match = re.search(r'\[(\d+)\]\[([^\]]+)\]\s+host:\s+([^\s]+)\s+login:\s+([^\s]+)\s+password:\s+(.+)', line)
                if login_match:
                    port, service_type, host, username, password = login_match.groups()
                    result["successful_logins"].append({
                        "port": port,
                        "service": service_type,
                        "host": host,
                        "username": username,
                        "password": password
                    })
            
            # Parse error output for additional info
            error_lines = error_output.split('\n')
            for line in error_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extract target info
                if "Hydra" in line and "starting" in line:
                    # Extract target from line like "Hydra v9.1 starting at 2023-01-01 12:00:00"
                    pass
                
                # Count failed attempts
                if "failed" in line.lower() or "error" in line.lower():
                    result["failed_attempts"] += 1
            
            # Generate summary
            result["summary"] = self._generate_summary(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Hydra output parsing error: {e}")
            return {"error": f"Output parsing failed: {e}"}
    
    def _generate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate attack summary"""
        summary = {
            "total_attempts": len(result["successful_logins"]) + result["failed_attempts"],
            "successful_logins": len(result["successful_logins"]),
            "failed_attempts": result["failed_attempts"],
            "success_rate": 0,
            "vulnerable_services": [],
            "recommendations": []
        }
        
        # Calculate success rate
        if summary["total_attempts"] > 0:
            summary["success_rate"] = (summary["successful_logins"] / summary["total_attempts"]) * 100
        
        # Identify vulnerable services
        for login in result["successful_logins"]:
            service = login["service"]
            if service not in summary["vulnerable_services"]:
                summary["vulnerable_services"].append(service)
        
        # Generate recommendations
        summary["recommendations"] = self._generate_recommendations(result)
        
        return summary
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on attack results"""
        recommendations = []
        
        # Successful login recommendations
        if result["successful_logins"]:
            recommendations.append({
                "priority": "critical",
                "title": "Weak Credentials Found",
                "description": f"Found {len(result['successful_logins'])} successful logins with weak credentials.",
                "action": "Change all default/weak passwords immediately"
            })
            
            # Service-specific recommendations
            for login in result["successful_logins"]:
                service = login["service"]
                if service == "ssh":
                    recommendations.append({
                        "priority": "high",
                        "title": "SSH Brute Force Successful",
                        "description": f"SSH login successful with username: {login['username']}",
                        "action": "Implement SSH key-based authentication, disable password auth, use fail2ban"
                    })
                elif service == "ftp":
                    recommendations.append({
                        "priority": "high",
                        "title": "FTP Brute Force Successful",
                        "description": f"FTP login successful with username: {login['username']}",
                        "action": "Disable anonymous FTP, use strong passwords, consider SFTP"
                    })
                elif service == "http-post-form":
                    recommendations.append({
                        "priority": "high",
                        "title": "Web Login Brute Force Successful",
                        "description": f"Web login successful with username: {login['username']}",
                        "action": "Implement account lockout, CAPTCHA, rate limiting"
                    })
                elif service == "mysql":
                    recommendations.append({
                        "priority": "critical",
                        "title": "Database Brute Force Successful",
                        "description": f"MySQL login successful with username: {login['username']}",
                        "action": "Change database passwords, restrict database access, use strong authentication"
                    })
        
        # General recommendations
        if result["failed_attempts"] > 100:
            recommendations.append({
                "priority": "medium",
                "title": "High Number of Failed Attempts",
                "description": f"Detected {result['failed_attempts']} failed login attempts.",
                "action": "Implement account lockout policies and monitoring"
            })
        
        return recommendations
    
    async def attack_with_custom_wordlist(self, target: str, service: str, 
                                        username_list: str, password_list: str) -> Dict[str, Any]:
        """Run Hydra with custom username and password lists"""
        try:
            command = [
                "hydra",
                "-L", username_list,  # Username list
                "-P", password_list,  # Password list
                f"{service}://{target}",
                "-t", "4",
                "-V",
                "-f"
            ]
            
            logger.info(f"Running Hydra with custom lists: {' '.join(command)}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode()
            error_output = stderr.decode()
            
            parsed_data = self._parse_hydra_output(output, error_output)
            
            return {
                "output": output,
                "error_output": error_output,
                "parsed_data": parsed_data,
                "success": process.returncode == 0,
                "return_code": process.returncode
            }
            
        except Exception as e:
            logger.error(f"Hydra custom attack error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
