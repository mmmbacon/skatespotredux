from .spot import Spot, SpotCreate, SpotUpdate, SpotBase
from .comment import Comment, CommentCreate
from .user import User, UserCreate, UserUpdate, UserBase, UserPublic

__all__ = [
    "User",
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

User.model_rebuild()
Spot.model_rebuild()
Comment.model_rebuild() 