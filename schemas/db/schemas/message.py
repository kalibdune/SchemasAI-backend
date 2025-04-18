from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from schemas.db.schemas.chat import ChatBaseSchema
from schemas.utils.enums import SenderType


class MessageBaseSchema(BaseModel):
    content: str
    sender_type: SenderType
    chat_id: UUID


class MessageSchema(MessageBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class MessageCreateSchema(BaseModel):
    content: str
    sender_type: SenderType


class MessageUpdateSchema(BaseModel):
    content: str | None
