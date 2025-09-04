"""
Gobuster wrapper untuk directory enumeration
"""

import asyncio
import subprocess
import re
import json
from typing import Dict, Any, List
from loguru import logger


class GobusterWrapper:
    """Wrapper untuk Gobuster directory enumeration tool"""
    
    def __init__(self):
        self.tool_name = "gobuster"
    
    async def scan(self, url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> Dict[str, Any]:
        """Run Gobuster directory enumeration"""
        try:
            # Build command
            command = [
                "gobuster",
                "dir",
                "-u", url,
                "-w", wordlist,
                "-t", "50",  # Threads
                "-q"        # Quiet mode
            ]
            
            logger.info(f"Running Gobuster command: {' '.join(command)}")
            
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
            parsed_data = self._parse_gobuster_output(output, error_output)
            
            return {
                "output": output,
                "error_output": error_output,
                "parsed_data": parsed_data,
                "success": process.returncode == 0,
                "return_code": process.returncode
            }
            
        except Exception as e:
            logger.error(f"Gobuster scan error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
    
    def _parse_gobuster_output(self, output: str, error_output: str) -> Dict[str, Any]:
        """Parse Gobuster output"""
        try:
            result = {
                "target": "",
                "wordlist": "",
                "found_directories": [],
                "found_files": [],
                "status_codes": {},
                "summary": {}
            }
            
            lines = output.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse found directories/files
                # Format: /admin (Status: 200) [Size: 1234]
                if line.startswith('/'):
                    match = re.search(r'^([^\s]+)\s+\(Status:\s+(\d+)\)\s+\[Size:\s+(\d+)\]', line)
                    if match:
                        path, status_code, size = match.groups()
                        
                        item = {
                            "path": path,
                            "status_code": int(status_code),
                            "size": int(size),
                            "type": "directory" if path.endswith('/') else "file"
                        }
                        
                        if item["type"] == "directory":
                            result["found_directories"].append(item)
                        else:
                            result["found_files"].append(item)
                        
                        # Count status codes
                        status_code = int(status_code)
                        if status_code not in result["status_codes"]:
                            result["status_codes"][status_code] = 0
                        result["status_codes"][status_code] += 1
            
            # Generate summary
            result["summary"] = self._generate_summary(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Gobuster output parsing error: {e}")
            return {"error": f"Output parsing failed: {e}"}
    
    def _generate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scan summary"""
        summary = {
            "total_found": len(result["found_directories"]) + len(result["found_files"]),
            "directories_found": len(result["found_directories"]),
            "files_found": len(result["found_files"]),
            "interesting_paths": [],
            "recommendations": []
        }
        
        # Identify interesting paths
        all_paths = result["found_directories"] + result["found_files"]
        interesting_keywords = [
            "admin", "login", "dashboard", "config", "backup", "test", "dev",
            "api", "upload", "download", "files", "images", "css", "js",
            "php", "asp", "jsp", "cgi", "bin", "etc", "var", "tmp"
        ]
        
        for item in all_paths:
            path_lower = item["path"].lower()
            for keyword in interesting_keywords:
                if keyword in path_lower:
                    summary["interesting_paths"].append({
                        "path": item["path"],
                        "status_code": item["status_code"],
                        "size": item["size"],
                        "type": item["type"],
                        "keyword": keyword
                    })
                    break
        
        # Generate recommendations
        summary["recommendations"] = self._generate_recommendations(result, summary)
        
        return summary
    
    def _generate_recommendations(self, result: Dict[str, Any], summary: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        # Admin panel recommendations
        admin_paths = [item for item in summary["interesting_paths"] if "admin" in item["path"].lower()]
        if admin_paths:
            recommendations.append({
                "priority": "high",
                "title": "Admin Panel Found",
                "description": f"Found {len(admin_paths)} admin-related paths.",
                "action": "Test admin panels for authentication bypass and weak credentials"
            })
        
        # Backup file recommendations
        backup_paths = [item for item in summary["interesting_paths"] if "backup" in item["path"].lower()]
        if backup_paths:
            recommendations.append({
                "priority": "high",
                "title": "Backup Files Found",
                "description": f"Found {len(backup_paths)} backup-related paths.",
                "action": "Check backup files for sensitive information and remove if not needed"
            })
        
        # Configuration file recommendations
        config_paths = [item for item in summary["interesting_paths"] if "config" in item["path"].lower()]
        if config_paths:
            recommendations.append({
                "priority": "high",
                "title": "Configuration Files Found",
                "description": f"Found {len(config_paths)} configuration-related paths.",
                "action": "Review configuration files for sensitive information and secure access"
            })
        
        # Upload directory recommendations
        upload_paths = [item for item in summary["interesting_paths"] if "upload" in item["path"].lower()]
        if upload_paths:
            recommendations.append({
                "priority": "medium",
                "title": "Upload Directories Found",
                "description": f"Found {len(upload_paths)} upload-related paths.",
                "action": "Test upload functionality for file upload vulnerabilities"
            })
        
        # API endpoint recommendations
        api_paths = [item for item in summary["interesting_paths"] if "api" in item["path"].lower()]
        if api_paths:
            recommendations.append({
                "priority": "medium",
                "title": "API Endpoints Found",
                "description": f"Found {len(api_paths)} API-related paths.",
                "action": "Test API endpoints for authentication and authorization issues"
            })
        
        # General recommendations
        if summary["total_found"] > 50:
            recommendations.append({
                "priority": "low",
                "title": "Many Directories Found",
                "description": f"Found {summary['total_found']} directories/files. This may indicate information disclosure.",
                "action": "Review directory listing configuration and remove unnecessary files"
            })
        
        return recommendations
    
    async def scan_with_extensions(self, url: str, wordlist: str, extensions: List[str]) -> Dict[str, Any]:
        """Run Gobuster with specific file extensions"""
        try:
            # Build command with extensions
            command = [
                "gobuster",
                "dir",
                "-u", url,
                "-w", wordlist,
                "-x", ",".join(extensions),  # File extensions
                "-t", "50",
                "-q"
            ]
            
            logger.info(f"Running Gobuster with extensions: {' '.join(command)}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode()
            error_output = stderr.decode()
            
            parsed_data = self._parse_gobuster_output(output, error_output)
            
            return {
                "output": output,
                "error_output": error_output,
                "parsed_data": parsed_data,
                "success": process.returncode == 0,
                "return_code": process.returncode
            }
            
        except Exception as e:
            logger.error(f"Gobuster extension scan error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
