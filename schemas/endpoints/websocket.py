import logging
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from schemas.db.schemas.message import MessageCreateSchema, MessageSchema
from schemas.endpoints.dependencies import get_session, WebSocketOAuth, OAuth
from schemas.services.message import MessageService
from schemas.services.websocket_service import ConnectionManager
from schemas.utils.enums import SenderType

router = APIRouter()
manager = ConnectionManager()
logger = logging.getLogger(__name__)

class RabbitClientServiceStub:
    async def connect(self):
        logging.info("RabbitMQ подключен (заглушка)")

    async def call(self, message: dict) -> dict:
        logging.info(f"Получено сообщение: {message}")
        # Заглушка для ответа ИИ
        return {"response": "Это ответ от ии (заглушка)"}

    async def close(self):
        logging.info("RabbitMQ соединение закрыто (заглушка)")


rabbit_service = RabbitClientServiceStub()


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
        chat_id: UUID,
        auth: WebSocketOAuth,
        session=Depends(get_session),
):
    message_service = MessageService(session)
    await manager.connect(websocket, chat_id)
    try:
        await rabbit_service.connect()
        while True:
            data = await websocket.receive_json()
            user_message = MessageCreateSchema(
                content=data.get("content"),
                sender_type=SenderType.user,
                chat_id=chat_id,
            )
            saved_user_message = await message_service.create_message(
                user_message, chat_id
            )

            response_data = await rabbit_service.call(user_message.model_dump())
            ai_message = MessageCreateSchema(
                content=response_data.get("content"),
                sender_type=SenderType.ai,
                chat_id=chat_id,
            )
            saved_ai_message = await message_service.create_message(ai_message, chat_id)
            response_message = MessageSchema(
                id=saved_ai_message.id,
                content=saved_ai_message.content,
                sender_type=saved_ai_message.sender_type,
                chat_id=chat_id,
                created_at=saved_ai_message.created_at,
                updated_at=saved_ai_message.updated_at
            )
            await manager.send_message(response_message, chat_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)
        logging.info(f"Client disconnected: {chat_id}")
        await websocket.close()
    finally:
        await rabbit_service.close()
        logging.info("RabbitMQ connection closed")
