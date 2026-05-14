from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass  # Connection dead, will be cleaned up

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Authenticate user
    from .auth import decode_token
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        user = crud.get_user_by_email(db, email)
        if not user or not user.is_active:
            await websocket.close(code=4001)
            return
    except:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client ping
            data = await websocket.receive_text()
            # Echo back or handle client messages
            await manager.send_personal_message({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Broadcast position updates to relevant users
async def broadcast_position_update(user_id: int, position: dict):
    """Send position update to user's WebSocket connections"""
    for connection in manager.active_connections:
        # In production, track user_id per connection
        await manager.send_personal_message({
            "type": "position_update",
            "data": position
        }, connection)
