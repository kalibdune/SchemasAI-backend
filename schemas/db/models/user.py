from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from schemas.db.models.base import Base, TimeStampMixin

if TYPE_CHECKING:
    from schemas.db.models.auth import Auth
    from schemas.db.models.chat import Chat


class User(Base, TimeStampMixin):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    auths: Mapped[list["Auth"]] = relationship(back_populates="user")
    chats: Mapped[list["Chat"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        return f"User({attrs})"

    class Config:
        orm_mode = True
