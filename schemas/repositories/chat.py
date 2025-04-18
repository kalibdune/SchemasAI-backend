from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.db.models.chat import Chat
from schemas.repositories.base import SQLAlchemyRepository


class ChatRepository(SQLAlchemyRepository):
    model = Chat

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all_by_user_id(self, user_id: UUID) -> list[Chat] | None:
        stmt = select(self.model).where(self.model.user_id == user_id)
        return await self._session.scalars(stmt)
