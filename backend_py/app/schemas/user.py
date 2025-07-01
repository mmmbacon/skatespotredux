from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_serializer
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .spot import Spot
    from .comment import Comment

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime
    last_login: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        # Ensure UTC timestamps are serialized with 'Z' suffix for proper timezone handling
        return dt.isoformat() + 'Z' if dt.tzinfo is None else dt.isoformat()

    @field_serializer('last_login')
    def serialize_last_login(self, dt: datetime) -> str:
        # Ensure UTC timestamps are serialized with 'Z' suffix for proper timezone handling
        return dt.isoformat() + 'Z' if dt.tzinfo is None else dt.isoformat()

    class Config:
        from_attributes = True

class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    last_login: datetime
    spots: List[Spot] = []
    comments: List[Comment] = []

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        # Ensure UTC timestamps are serialized with 'Z' suffix for proper timezone handling
        return dt.isoformat() + 'Z' if dt.tzinfo is None else dt.isoformat()

    @field_serializer('last_login')
    def serialize_last_login(self, dt: datetime) -> str:
        # Ensure UTC timestamps are serialized with 'Z' suffix for proper timezone handling
        return dt.isoformat() + 'Z' if dt.tzinfo is None else dt.isoformat()

    class Config:
        from_attributes = True 