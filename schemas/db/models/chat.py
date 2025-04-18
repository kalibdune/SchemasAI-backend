from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schemas.db.models.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from schemas.db.models.message import Message
    from schemas.db.models.user import User


class Chat(Base, TimeStampMixin):
    __tablename__ = "chat"

    name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))

    user: Mapped["User"] = relationship("User", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        return f"Chat({attrs})"

    class Config:
        orm_mode = True
