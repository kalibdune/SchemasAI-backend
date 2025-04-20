from sqlalchemy import desc, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.db.models import Message
from schemas.repositories.base import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository):
    model = Message

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all_by_chat_id(self, chat_id: UUID) -> list[Message]:
        stmt = select(self.model).where(self.model.chat_id == chat_id)
        return await self._session.scalars(stmt)

    async def get_paginated_by_chat_id(
        self, chat_id: UUID, start: int, count: int
    ) -> list[Message]:
        stmt = select(self.model).where(self.model.chat_id == chat_id)
        stmt = stmt.order_by(desc(self.model.created_at))
        stmt = stmt.offset(start)
        stmt = stmt.limit(count)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
