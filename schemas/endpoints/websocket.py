import logging
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from schemas.db.schemas.message import MessageCreateSchema, MessageSchema
from schemas.endpoints.dependencies import WebSocketOAuth, get_session
from schemas.services.message import MessageService
from schemas.services.rabbit import client_service
from schemas.utils.enums import SenderType

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID,
    session=Depends(get_session),
):
    message_service = MessageService(session)
    await websocket.accept()
    try:
        while True:
            user_message = MessageCreateSchema.model_validate(
                (await websocket.receive_json())
            )
            saved_user_message = await message_service.create_message(
                user_message, chat_id
            )

            ai_message = await client_service.call("message_queue", saved_user_message)
            saved_ai_message = await message_service.create_message(ai_message, chat_id)

            await websocket.send_json(ai_message.model_dump_json())
    except WebSocketDisconnect:
        logging.info(f"Client disconnected: {chat_id}")
