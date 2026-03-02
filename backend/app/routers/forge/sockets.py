from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging

logger = logging.getLogger("nexusfest")

router = APIRouter()

# Store connections per project
# Key: project_id, Value: List of WebSocket connections
project_connections: Dict[int, List[WebSocket]] = {}

@router.websocket("/ws/forge/projects/{project_id}")
async def forge_websocket_endpoint(websocket: WebSocket, project_id: int):
    await websocket.accept()
    
    if project_id not in project_connections:
        project_connections[project_id] = []
    
    project_connections[project_id].append(websocket)
    logger.info(f"Client connected to Forge Project {project_id}. Total connections: {len(project_connections[project_id])}")

    try:
        while True:
            # Keep the connection alive and listen for optional client messages (pings)
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from Forge Project {project_id}")
        if project_id in project_connections:
            project_connections[project_id].remove(websocket)
            if not project_connections[project_id]:
                del project_connections[project_id]

async def broadcast_forge_event(project_id: int, event_type: str, data: dict):
    """
    Broadcasts a JSON message to all clients connected to the specific project.
    Message format: { "type": event_type, "payload": data }
    """
    if project_id in project_connections:
        message = {
            "type": event_type,
            "payload": data
        }
        json_message = json.dumps(message, default=str) # default=str handles datetime serialization
        
        dead_connections = []
        for connection in project_connections[project_id]:
            try:
                await connection.send_text(json_message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                dead_connections.append(connection)
        
        # Cleanup dead connections
        for dead in dead_connections:
            if dead in project_connections[project_id]:
                project_connections[project_id].remove(dead)
