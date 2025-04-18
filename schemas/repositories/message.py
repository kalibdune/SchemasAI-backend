from sqlalchemy import select
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
