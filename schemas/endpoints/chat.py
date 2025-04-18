import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from schemas.db.schemas.chat import ChatCreateSchema, ChatSchema, ChatUpdateSchema
from schemas.endpoints.dependencies import OAuth, get_session
from schemas.services.chat import ChatService

router = APIRouter(prefix="/chat")

logger = logging.getLogger(__name__)


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: ChatCreateSchema, user: OAuth, session=Depends(get_session)
):
    chat_service = ChatService(session)
    return await chat_service.create_chat(user, data)


@router.get("/chats/", response_model=list[ChatSchema], status_code=status.HTTP_200_OK)
async def get_chats_by_user_id(user: OAuth, session=Depends(get_session)):
    chat_service = ChatService(session)
    return await chat_service.get_chats_by_user_id(user)


@router.get("/{id}/", response_model=ChatSchema, status_code=status.HTTP_200_OK)
async def get_chat_by_id(id: UUID, auth: OAuth, session=Depends(get_session)):
    chat_service = ChatService(session)
    return await chat_service.get_chat_by_id(id)


@router.patch("/{id}/", response_model=ChatSchema, status_code=status.HTTP_200_OK)
async def update_chat(
    data: ChatUpdateSchema, id: UUID, auth: OAuth, session=Depends(get_session)
):
    chat_service = ChatService(session)
    return await chat_service.update_chat(id, data)


@router.delete("/{id}/", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(id: UUID, auth: OAuth, session=Depends(get_session)):
    chat_service = ChatService(session)
    await chat_service.delete_chat(id)
