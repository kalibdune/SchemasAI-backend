import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from schemas.db.models import Message
from schemas.db.schemas.message import (
    MessageBaseSchema,
    MessageCreateSchema,
    MessageSchema,
    MessageUpdateSchema,
)
from schemas.endpoints.dependencies import OAuth, get_session
from schemas.services.message import MessageService

router = APIRouter(prefix="/message")

logger = logging.getLogger(__name__)


@router.post(
    "/chat/{chat_id}", response_model=MessageSchema, status_code=status.HTTP_201_CREATED
)
async def create_message(
    chat_id: UUID, data: MessageCreateSchema, auth: OAuth, session=Depends(get_session)
):
    message_service = MessageService(session)
    return await message_service.create_message(data, chat_id)


@router.get(
    "/chat/{chat_id}",
    response_model=list[MessageSchema],
    status_code=status.HTTP_200_OK,
)
async def get_messages_by_chat_id(
    chat_id: UUID, auth: OAuth, session=Depends(get_session)
):
    message_service = MessageService(session)
    return await message_service.get_messages_by_chat_id(chat_id)


@router.get("/{id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
async def get_message_by_message_id(
    id: UUID, auth: OAuth, session=Depends(get_session)
):
    message_service = MessageService(session)
    return await message_service.get_message_by_message_id(id)


@router.patch("/{id}", response_model=MessageSchema, status_code=status.HTTP_200_OK)
async def update_message(
    data: MessageUpdateSchema, id: UUID, auth: OAuth, session=Depends(get_session)
):
    message_service = MessageService(session)
    return await message_service.update_message(id, data)


@router.delete("/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(id: UUID, auth: OAuth, session=Depends(get_session)):
    message_service = MessageService(session)
    await message_service.delete_message(id)
