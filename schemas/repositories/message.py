from sqlalchemy import desc, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.db.models import Message
from schemas.repositories.base import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository):
    model = Message

    def __init(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all_by_chat_id(self, chat_id: UUID) -> list[Message]:
        stmt = select(self.model).where(self.model.chat_id == chat_id)
        return await self._session.scalars(stmt)

    async def get_paginated_by_chat_id(
        self, chat_id: UUID, start: str, count: int
    ) -> list[Message]:
        stmt = select(self.model).where(self.model.chat_id == chat_id)
        if start == "last":
            stmt = stmt.order_by(desc(self.model.created_at))
        else:
            try:
                start_id = UUID(start)
                start_message = await self._session.get(self.model, start_id)
                if start_message:
                    stmt = stmt.where(self.model.created_at < start_message.created_at)
                    stmt = stmt.order_by(desc(self.model.created_at))
                else:
                    stmt = stmt.order_by(desc(self.model.created_at))
            except ValueError:
                stmt = stmt.order_by(desc(self.model.created_at))

        stmt = stmt.limit(count)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
