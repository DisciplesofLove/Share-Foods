from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
from ..services.auth import get_current_user_ws
from ..models.users import User

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
    
    async def broadcast(self, message: str, exclude_user: int = None):
        for user_id, connection in self.active_connections.items():
            if user_id != exclude_user:
                await connection.send_text(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "chat":
                await manager.broadcast(
                    json.dumps({
                        "type": "chat",
                        "user_id": user_id,
                        "content": message["content"]
                    }),
                    exclude_user=user_id
                )
            elif message["type"] == "notification":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "notification",
                        "content": message["content"]
                    }),
                    user_id=message["recipient_id"]
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(
            json.dumps({
                "type": "system",
                "content": f"User {user_id} left the chat"
            })
        )

# Connection manager is already defined above
    # Using the implementation defined above
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)
    
    async def broadcast(self, message: str):
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    user: User = Depends(get_current_user_ws)
):
    await manager.connect(websocket, user.id)
    try:
        while True:
            # Wait for messages (heartbeat or client messages)
            data = await websocket.receive_text()
            # Echo back to maintain connection
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)