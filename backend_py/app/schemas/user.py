from __future__ import annotations
from pydantic import BaseModel, EmailStr
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

    class Config:
        from_attributes = True

class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    last_login: datetime
    spots: List[Spot] = []
    comments: List[Comment] = []

    class Config:
        from_attributes = True 