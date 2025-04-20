from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.db.schemas.chat import ChatSchema
from schemas.db.schemas.message import (
    MessageBaseSchema,
    MessageCreateSchema,
    MessageSchema,
    MessageUpdateSchema,
)
from schemas.db.schemas.user import UserSchema
from schemas.repositories.chat import ChatRepository
from schemas.repositories.message import MessageRepository
from schemas.utils.exceptions import NotFoundError


class MessageService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = MessageRepository(session)

    async def get_messages_by_chat_id(self, chat_id: UUID) -> list[MessageSchema]:
        messages = await self._repository.get_all_by_chat_id(chat_id)
        if messages is None:
            raise NotFoundError(f"messages from {chat_id} not found")
        return [
            MessageSchema.model_validate(message, from_attributes=True)
            for message in messages
        ]

    async def get_paginated_messages_by_chat_id(
        self, chat_id: UUID, start: str, count: int
    ) -> list[MessageSchema]:
        offset = 0
        if start != "last":
            try:
                offset = int(start)
                if offset < 0:
                    offset = 0
            except ValueError:
                raise ValueError("start must be a number or 'last'")

        messages = await self._repository.get_paginated_by_chat_id(
            chat_id, offset, count
        )
        if not messages:
            return []

        return [
            MessageSchema.model_validate(message, from_attributes=True)
            for message in messages
        ]

    async def get_message_by_message_id(self, message_id: UUID) -> MessageSchema:
        message = await self._repository.get_by_id(message_id)
        if message is None:
            raise NotFoundError(f"message with id {message_id} not found")
        return MessageSchema.model_validate(message, from_attributes=True)

    async def create_message(
        self, message: MessageCreateSchema, chat_id: UUID
    ) -> MessageSchema:
        chat_repos = ChatRepository(self._session)
        chat = await chat_repos.get_by_id(chat_id)
        if chat is None:
            raise NotFoundError(f"chat with id {chat_id} not found")
        message_data = message.model_dump()
        message_data["chat_id"] = chat_id
        created_message = await self._repository.create(message_data)
        return MessageSchema.model_validate(created_message, from_attributes=True)

    async def update_message(
        self, message_id: UUID, new_message: MessageUpdateSchema
    ) -> MessageSchema:
        message = await self.get_message_by_message_id(message_id)
        for key, value in new_message.model_dump(exclude_unset=True).items():
            setattr(message, key, value)

        message = await self._repository.update_by_id(message_id, message.model_dump())
        return MessageSchema.model_validate(message, from_attributes=True)

    async def delete_message(self, message_id: UUID) -> None:
        message = self.get_message_by_message_id(message_id)
        await self._repository.delete_by_id(message_id)
