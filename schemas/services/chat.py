from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.db.schemas.chat import (
    ChatCreateSchema,
    ChatInDB,
    ChatSchema,
    ChatUpdateSchema,
)
from schemas.db.schemas.user import UserSchema
from schemas.repositories.chat import ChatRepository
from schemas.utils.exceptions import NotFoundError


class ChatService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = ChatRepository(session)

    async def get_chat_by_id(self, chat_id: UUID) -> ChatSchema:
        chat = await self._repository.get_by_id(chat_id)
        if chat is None:
            raise NotFoundError(f"chat_id: {chat_id}")
        return ChatSchema.model_validate(chat, from_attributes=True)

    async def get_chats_by_user_id(self, user: UserSchema) -> list[ChatSchema]:
        chats = await self._repository.get_all_by_user_id(user.id)
        return [ChatSchema.model_validate(chat, from_attributes=True) for chat in chats]

    async def create_chat(self, user: UserSchema, chat: ChatCreateSchema) -> ChatSchema:
        chat = ChatInDB(name=chat.name, user_id=user.id)
        chat = await self._repository.create(chat.model_dump())
        return ChatSchema.model_validate(chat, from_attributes=True)

    async def update_chat(
        self, chat_id: UUID, new_chat: ChatUpdateSchema
    ) -> ChatSchema:
        chat = await self.get_chat_by_id(chat_id)

        for key, value in new_chat.model_dump(exclude_unset=True).items():
            setattr(chat, key, value)

        chat = await self._repository.update_by_id(chat_id, chat.model_dump())
        return ChatSchema.model_validate(chat, from_attributes=True)

    async def delete_chat(self, chat_id: UUID) -> None:
        chat = self.get_chat_by_id(chat_id)
        await self._repository.delete_by_id(chat_id)
