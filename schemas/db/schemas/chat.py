from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ChatBaseSchema(BaseModel):
    name: str


class ChatSchema(ChatBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: UUID


class ChatCreateSchema(ChatBaseSchema): ...


class ChatUpdateSchema(BaseModel):
    name: str | None = None


class ChatInDB(ChatBaseSchema):
    user_id: UUID
