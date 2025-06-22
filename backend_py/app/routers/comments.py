from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from .. import schemas
from ..database import get_db
from ..models import Comment, Spot, User
from .auth import get_current_user

router = APIRouter(
    tags=["comments"],
)

@router.post("/spots/{spot_id}/comments", response_model=schemas.Comment, status_code=201)
async def create_comment_for_spot(
    spot_id: UUID,
    comment: schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new comment for a specific spot.
    """
    # First, check if the spot exists
    db_spot = await db.get(Spot, spot_id)
    if not db_spot:
        raise HTTPException(status_code=404, detail="Spot not found")

    db_comment = Comment(
        **comment.model_dump(),
        user_id=current_user.id,
        spot_id=spot_id
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


@router.get("/spots/{spot_id}/comments", response_model=List[schemas.Comment])
async def get_comments_for_spot(
    spot_id: UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all comments for a specific spot.
    """
    result = await db.execute(
        select(Comment)
        .where(Comment.spot_id == spot_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    comments = result.scalars().all()
    return comments 