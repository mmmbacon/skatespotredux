from pydantic import BaseModel, Field
from uuid import UUID

class VoteCreate(BaseModel):
    value: int = Field(..., description="1 for upvote, -1 for downvote", ge=-1, le=1)

class Vote(BaseModel):
    id: UUID
    user_id: UUID
    spot_id: UUID
    value: int

    class Config:
        from_attributes = True 