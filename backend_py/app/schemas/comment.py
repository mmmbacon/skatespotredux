from __future__ import annotations
from pydantic import BaseModel
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

    class Config:
        from_attributes = True 