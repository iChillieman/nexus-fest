# filename: app/routers/chilliesockets.py

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()

# Store connections per thread
thread_connections: Dict[int, List[WebSocket]] = {}

@router.websocket("/ws/threads/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: int):
    await websocket.accept()

    if thread_id not in thread_connections:
        thread_connections[thread_id] = []
    thread_connections[thread_id].append(websocket)

    try:
        while True:
            await websocket.receive_text()  # optional ping/heartbeat
    except WebSocketDisconnect:
        thread_connections[thread_id].remove(websocket)

async def broadcast_entry(entry: dict, thread_id: int):
    if thread_id in thread_connections:
        for ws in thread_connections[thread_id]:
            await ws.send_text(json.dumps(entry))