from __future__ import annotations
from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .user import UserPublic

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: uuid.UUID
    created_at: datetime
    spot_id: uuid.UUID
    user_id: uuid.UUID
    user: UserPublic

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        # Ensure UTC timestamps are serialized with 'Z' suffix for proper timezone handling
        return dt.isoformat() + 'Z' if dt.tzinfo is None else dt.isoformat()

    class Config:
        from_attributes = True 