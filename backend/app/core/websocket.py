"""
WebSocket connection manager untuk real-time updates
"""

from fastapi import WebSocket
from typing import List
import json
import asyncio
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_scan_update(self, scan_id: str, status: str, data: dict = None):
        """Send scan status update"""
        message = {
            "type": "scan_update",
            "scan_id": scan_id,
            "status": status,
            "data": data or {}
        }
        await self.broadcast(message)
    
    async def send_tool_output(self, scan_id: str, tool: str, output: str):
        """Send tool output in real-time"""
        message = {
            "type": "tool_output",
            "scan_id": scan_id,
            "tool": tool,
            "output": output
        }
        await self.broadcast(message)
    
    async def send_recommendation(self, scan_id: str, recommendations: list):
        """Send automated recommendations"""
        message = {
            "type": "recommendations",
            "scan_id": scan_id,
            "recommendations": recommendations
        }
        await self.broadcast(message)
