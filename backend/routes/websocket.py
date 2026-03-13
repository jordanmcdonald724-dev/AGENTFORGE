"""
WebSocket Routes - Real-time updates for Mission Control
Provides live agent activity, build progress, and system events
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/ws", tags=["websocket"])

# Connection managers
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.agent_states: Dict[str, dict] = {}
        
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        
    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            
    async def broadcast(self, channel: str, message: dict):
        if channel in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            # Clean up dead connections
            self.active_connections[channel] -= dead_connections
            
    async def send_to_all(self, message: dict):
        for channel in self.active_connections:
            await self.broadcast(channel, message)

manager = ConnectionManager()

# Agent simulation data
AGENTS = [
    {"id": "commander", "name": "COMMANDER", "role": "lead", "color": "#8b5cf6"},
    {"id": "atlas", "name": "ATLAS", "role": "architect", "color": "#06b6d4"},
    {"id": "forge", "name": "FORGE", "role": "developer", "color": "#f59e0b"},
    {"id": "sentinel", "name": "SENTINEL", "role": "reviewer", "color": "#ef4444"},
    {"id": "probe", "name": "PROBE", "role": "tester", "color": "#22c55e"},
    {"id": "prism", "name": "PRISM", "role": "artist", "color": "#ec4899"},
]

ACTIVITIES = [
    "Analyzing code structure",
    "Optimizing database queries",
    "Reviewing security patterns",
    "Generating test cases",
    "Refactoring components",
    "Building API endpoints",
    "Designing UI components",
    "Running integration tests",
    "Profiling performance",
    "Documenting functions",
    "Scanning for vulnerabilities",
    "Creating visual assets",
]

@router.websocket("/agents/{project_id}")
async def agent_activity_websocket(websocket: WebSocket, project_id: str):
    """WebSocket for real-time agent activity updates"""
    channel = f"agents:{project_id}"
    await manager.connect(websocket, channel)
    
    try:
        # Send initial agent states
        for agent in AGENTS:
            agent_state = {
                "type": "agent_state",
                "agent": agent,
                "status": "idle",
                "activity": None,
                "progress": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await websocket.send_json(agent_state)
        
        # Start simulation loop
        import random
        while True:
            # Randomly activate an agent
            agent = random.choice(AGENTS)
            activity = random.choice(ACTIVITIES)
            
            # Send activity start
            await manager.broadcast(channel, {
                "type": "agent_activity",
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "status": "working",
                "activity": activity,
                "progress": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Simulate progress
            for progress in [25, 50, 75, 100]:
                await asyncio.sleep(0.5 + random.random())
                await manager.broadcast(channel, {
                    "type": "agent_progress",
                    "agent_id": agent["id"],
                    "progress": progress,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            # Send completion
            await manager.broadcast(channel, {
                "type": "agent_complete",
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "activity": activity,
                "status": "idle",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Wait before next activity
            await asyncio.sleep(2 + random.random() * 3)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.websocket("/builds/{session_id}")
async def build_progress_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for real-time build progress"""
    channel = f"build:{session_id}"
    await manager.connect(websocket, channel)
    
    try:
        while True:
            # Listen for messages (keep connection alive)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.websocket("/mission-control")
async def mission_control_websocket(websocket: WebSocket):
    """WebSocket for mission control dashboard updates"""
    channel = "mission-control"
    await manager.connect(websocket, channel)
    
    try:
        # Send initial system status
        await websocket.send_json({
            "type": "system_status",
            "status": "online",
            "agents_active": len(AGENTS),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Keep connection alive and broadcast updates
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "subscribe":
                # Handle subscription to specific channels
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


# Helper function to broadcast build events (called from other routes)
async def broadcast_build_event(session_id: str, event: dict):
    """Broadcast build event to all connected clients"""
    channel = f"build:{session_id}"
    await manager.broadcast(channel, event)


async def broadcast_agent_event(project_id: str, event: dict):
    """Broadcast agent event to all connected clients"""
    channel = f"agents:{project_id}"
    await manager.broadcast(channel, event)
