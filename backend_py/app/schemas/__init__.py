from .spot import Spot, SpotCreate, SpotUpdate, SpotBase
from .comment import Comment, CommentCreate
from .user import UserCreate, UserUpdate, UserBase, UserPublic

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserBase",
    "UserPublic",
    "Spot",
    "SpotCreate",
    "SpotUpdate",
    "SpotBase",
    "Comment",
    "CommentCreate",
]

UserPublic.model_rebuild()
Spot.model_rebuild()
Comment.model_rebuild() 