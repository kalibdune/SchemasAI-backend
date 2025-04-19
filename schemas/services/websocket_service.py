from typing import Dict, List
from uuid import UUID

from fastapi import WebSocket

from schemas.db.schemas.chat import ChatSchema
from schemas.db.schemas.message import MessageSchema


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: UUID):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: UUID):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def send_message(self, message: MessageSchema, chat_id: UUID):
        if chat_id in self.active_connections:
            message_dict = message.model_dump()
            for connection in self.active_connections[chat_id]:
                await connection.send_json(message_dict)
