"""
Nmap wrapper untuk port scanning dan service detection
"""

import asyncio
import subprocess
import xml.etree.ElementTree as ET
import json
from typing import Dict, Any, List
from loguru import logger


class NmapWrapper:
    """Wrapper untuk Nmap tool"""
    
    def __init__(self):
        self.tool_name = "nmap"
    
    async def scan(self, target: str, options: str = "-sV -O") -> Dict[str, Any]:
        """Run Nmap scan"""
        try:
            # Build command dengan XML output
            xml_options = options.replace("-O", "-O -oX -") if "-O" in options else f"{options} -oX -"
            command = ["nmap"] + xml_options.split() + [target]
            
            logger.info(f"Running Nmap command: {' '.join(command)}")
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Nmap failed: {error_msg}")
                return {
                    "output": error_msg,
                    "parsed_data": {},
                    "error": error_msg
                }
            
            # Parse XML output
            xml_output = stdout.decode()
            parsed_data = self._parse_nmap_xml(xml_output)
            
            return {
                "output": xml_output,
                "parsed_data": parsed_data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Nmap scan error: {e}")
            return {
                "output": "",
                "parsed_data": {},
                "error": str(e)
            }
    
    def _parse_nmap_xml(self, xml_content: str) -> Dict[str, Any]:
        """Parse Nmap XML output"""
        try:
            root = ET.fromstring(xml_content)
            
            result = {
                "hosts": [],
                "scan_info": {},
                "summary": {}
            }
            
            # Parse scan info
            scan_info = root.find("scaninfo")
            if scan_info is not None:
                result["scan_info"] = {
                    "type": scan_info.get("type", ""),
                    "protocol": scan_info.get("protocol", ""),
                    "numservices": scan_info.get("numservices", ""),
                    "services": scan_info.get("services", "")
                }
            
            # Parse hosts
            for host in root.findall("host"):
                host_data = self._parse_host(host)
                result["hosts"].append(host_data)
            
            # Generate summary
            result["summary"] = self._generate_summary(result["hosts"])
            
            return result
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return {"error": f"XML parsing failed: {e}"}
    
    def _parse_host(self, host_element) -> Dict[str, Any]:
        """Parse individual host data"""
        host_data = {
            "address": "",
            "hostnames": [],
            "ports": [],
            "os": {},
            "status": {}
        }
        
        # Address
        address = host_element.find("address")
        if address is not None:
            host_data["address"] = address.get("addr", "")
            host_data["address_type"] = address.get("addrtype", "")
        
        # Hostnames
        hostnames = host_element.find("hostnames")
        if hostnames is not None:
            for hostname in hostnames.findall("hostname"):
                host_data["hostnames"].append({
                    "name": hostname.get("name", ""),
                    "type": hostname.get("type", "")
                })
        
        # Ports
        ports = host_element.find("ports")
        if ports is not None:
            for port in ports.findall("port"):
                port_data = self._parse_port(port)
                host_data["ports"].append(port_data)
        
        # OS detection
        os = host_element.find("os")
        if os is not None:
            host_data["os"] = self._parse_os(os)
        
        # Status
        status = host_element.find("status")
        if status is not None:
            host_data["status"] = {
                "state": status.get("state", ""),
                "reason": status.get("reason", "")
            }
        
        return host_data
    
    def _parse_port(self, port_element) -> Dict[str, Any]:
        """Parse port data"""
        port_data = {
            "port": port_element.get("portid", ""),
            "protocol": port_element.get("protocol", ""),
            "state": {},
            "service": {}
        }
        
        # State
        state = port_element.find("state")
        if state is not None:
            port_data["state"] = {
                "state": state.get("state", ""),
                "reason": state.get("reason", ""),
                "reason_ttl": state.get("reason_ttl", "")
            }
        
        # Service
        service = port_element.find("service")
        if service is not None:
            port_data["service"] = {
                "name": service.get("name", ""),
                "product": service.get("product", ""),
                "version": service.get("version", ""),
                "extrainfo": service.get("extrainfo", ""),
                "method": service.get("method", ""),
                "conf": service.get("conf", "")
            }
        
        return port_data
    
    def _parse_os(self, os_element) -> Dict[str, Any]:
        """Parse OS detection data"""
        os_data = {
            "matches": [],
            "accuracy": 0
        }
        
        # OS matches
        for osmatch in os_element.findall("osmatch"):
            match_data = {
                "name": osmatch.get("name", ""),
                "accuracy": osmatch.get("accuracy", ""),
                "line": osmatch.get("line", "")
            }
            os_data["matches"].append(match_data)
        
        # Calculate average accuracy
        if os_data["matches"]:
            accuracies = [int(match["accuracy"]) for match in os_data["matches"] if match["accuracy"].isdigit()]
            if accuracies:
                os_data["accuracy"] = sum(accuracies) / len(accuracies)
        
        return os_data
    
    def _generate_summary(self, hosts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scan summary"""
        summary = {
            "total_hosts": len(hosts),
            "up_hosts": 0,
            "down_hosts": 0,
            "open_ports": 0,
            "services": {},
            "vulnerabilities": []
        }
        
        for host in hosts:
            if host["status"].get("state") == "up":
                summary["up_hosts"] += 1
            else:
                summary["down_hosts"] += 1
            
            for port in host["ports"]:
                if port["state"].get("state") == "open":
                    summary["open_ports"] += 1
                    
                    service_name = port["service"].get("name", "unknown")
                    if service_name not in summary["services"]:
                        summary["services"][service_name] = 0
                    summary["services"][service_name] += 1
        
        # Generate basic vulnerability recommendations
        summary["vulnerabilities"] = self._generate_vulnerability_recommendations(summary["services"])
        
        return summary
    
    def _generate_vulnerability_recommendations(self, services: Dict[str, int]) -> List[Dict[str, str]]:
        """Generate vulnerability recommendations based on services"""
        recommendations = []
        
        # Common service vulnerabilities
        service_vulns = {
            "ssh": "Consider SSH hardening: disable root login, use key-based auth, change default port",
            "ftp": "FTP is insecure, consider SFTP or FTPS. Check for anonymous access",
            "http": "Web server detected, run web vulnerability scans (Nikto, SQLMap)",
            "mysql": "Database detected, check for weak credentials and SQL injection",
            "smb": "SMB service detected, check for SMB vulnerabilities and null sessions",
            "telnet": "Telnet is insecure, consider SSH replacement",
            "rpcbind": "RPC service detected, check for RPC vulnerabilities"
        }
        
        for service, count in services.items():
            if service in service_vulns:
                recommendations.append({
                    "service": service,
                    "count": count,
                    "recommendation": service_vulns[service],
                    "priority": "medium"
                })
        
        return recommendations
