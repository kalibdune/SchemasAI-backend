from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schemas.db.models.base import Base, TimeStampMixin
from schemas.utils.enums import SenderType

if TYPE_CHECKING:
    from schemas.db.models.chat import Chat


class Message(Base, TimeStampMixin):
    __tablename__ = "message"

    chat_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat.id"))
    content: Mapped[str] = mapped_column(nullable=False)
    sender_type: Mapped[SenderType] = mapped_column(ENUM(SenderType), nullable=False)

    chat: Mapped["Chat"] = relationship(
        "Chat",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        return f"Message({attrs})"

    class Config:
        orm_mode = True
