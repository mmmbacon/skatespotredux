from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from geoalchemy2.functions import ST_MakeEnvelope, ST_Contains
from typing import List, Optional
from uuid import UUID
from app.config import get_r2_client, R2_BUCKET, R2_ENDPOINT
from fastapi.responses import JSONResponse

from .. import schemas
from ..database import get_db
from ..models import Spot, User, Comment, Vote
from ..routers.auth import get_current_user, get_current_user_optional

router = APIRouter(
    prefix="/spots",
    tags=["spots"],
)


@router.post("/", response_model=schemas.Spot, status_code=201)
async def create_spot(
    spot: schemas.SpotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new skate spot.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Convert GeoJSON to WKT format for PostGIS
    point = spot.location["coordinates"]
    wkt_location = f"POINT({point[0]} {point[1]})"

    db_spot = Spot(
        name=spot.name,
        description=spot.description,
        location=wkt_location,
        user_id=current_user.id,
    )
    db.add(db_spot)
    await db.commit()
    await db.refresh(db_spot)
    # Eagerly load comments and user for serialization
    result = await db.execute(
        select(Spot)
        .options(
            joinedload(Spot.user),
            joinedload(Spot.comments).joinedload(Comment.user)
        )
        .where(Spot.id == db_spot.id)
    )
    spot_with_comments = result.unique().scalar_one()
    return spot_with_comments


@router.get("/", response_model=List[schemas.Spot])
async def get_spots(
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
    skip: int = 0,
    limit: int = 100,
    north: Optional[float] = None,
    south: Optional[float] = None,
    east: Optional[float] = None,
    west: Optional[float] = None,
):
    """
    Retrieve a list of skate spots.
    Can be filtered by a bounding box.
    """
    query = select(Spot).options(
        joinedload(Spot.user),
        joinedload(Spot.comments).joinedload(Comment.user)
    )

    if all(coord is not None for coord in [north, south, east, west]):
        # Ensure coordinates are valid
        if west > east or south > north:
            raise HTTPException(status_code=400, detail="Invalid bounding box coordinates")

        # Create a bounding box polygon from the coordinates
        # Note: PostGIS uses (longitude, latitude) order
        bounding_box = ST_MakeEnvelope(west, south, east, north, 4326)

        # Filter spots that are contained within the bounding box
        query = query.where(ST_Contains(bounding_box, Spot.location))

    result = await db.execute(query.offset(skip).limit(limit))
    spots = result.scalars().unique().all()

    # Attach vote info
    user_id = current_user.id if current_user else None

    for spot in spots:
        vote_result = await db.execute(
            select(func.coalesce(func.sum(Vote.value), 0)).where(Vote.spot_id == spot.id)
        )
        spot.score = vote_result.scalar() or 0

        if user_id:
            my_vote_result = await db.execute(
                select(Vote.value).where(Vote.spot_id == spot.id, Vote.user_id == user_id)
            )
            spot.my_vote = my_vote_result.scalar()
        else:
            spot.my_vote = None
    return spots


@router.put("/{spot_id}", response_model=schemas.Spot)
async def update_spot(
    spot_id: UUID,
    spot_update: schemas.SpotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a skate spot.
    """
    db_spot = await db.get(Spot, spot_id)

    if not db_spot:
        raise HTTPException(status_code=404, detail="Spot not found")

    if db_spot.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this spot"
        )

    update_data = spot_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "location" and value:
            point = value["coordinates"]
            wkt_location = f"POINT({point[0]} {point[1]})"
            setattr(db_spot, key, wkt_location)
        else:
            setattr(db_spot, key, value)

    await db.commit()
    await db.refresh(db_spot)
    return db_spot


@router.put("/by-short-id/{short_id}", response_model=schemas.Spot)
async def update_spot_by_short_id(
    short_id: str,
    spot_update: schemas.SpotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a skate spot by short_id.
    """
    # Find spot by short_id
    result = await db.execute(select(Spot).where(Spot.short_id == short_id))
    db_spot = result.scalars().first()

    if not db_spot:
        raise HTTPException(status_code=404, detail="Spot not found")

    if db_spot.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this spot"
        )

    update_data = spot_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "location" and value:
            point = value["coordinates"]
            wkt_location = f"POINT({point[0]} {point[1]})"
            setattr(db_spot, key, wkt_location)
        else:
            setattr(db_spot, key, value)

    await db.commit()
    
    # Reload the spot with all relationships to avoid serialization issues
    result = await db.execute(
        select(Spot)
        .options(
            joinedload(Spot.user),
            joinedload(Spot.comments).joinedload(Comment.user)
        )
        .where(Spot.short_id == short_id)
    )
    updated_spot = result.unique().scalar_one()
    
    # Add vote info
    vote_result = await db.execute(
        select(func.coalesce(func.sum(Vote.value), 0)).where(Vote.spot_id == updated_spot.id)
    )
    updated_spot.score = vote_result.scalar() or 0

    my_vote_result = await db.execute(
        select(Vote.value).where(Vote.spot_id == updated_spot.id, Vote.user_id == current_user.id)
    )
    updated_spot.my_vote = my_vote_result.scalar()
    
    return updated_spot


@router.delete("/{spot_id}", status_code=204)
async def delete_spot(
    spot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a skate spot.
    """
    db_spot = await db.get(Spot, spot_id)

    if not db_spot:
        raise HTTPException(status_code=404, detail="Spot not found")

    if db_spot.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this spot"
        )

    await db.delete(db_spot)
    await db.commit()
    return Response(status_code=204)


@router.post("/image-upload-url")
def create_presigned_url(
    filename: str = Query(..., description="The name of the file to upload"),
    content_type: str = Query(..., description="The MIME type of the file")
):
    s3 = get_r2_client()
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": R2_BUCKET,
            "Key": filename,
            "ContentType": content_type,
        },
        ExpiresIn=600,  # 10 minutes
    )
    public_url = f"https://{R2_BUCKET}.{R2_ENDPOINT.replace('https://', '')}/{filename}"
    return JSONResponse({"url": url, "public_url": public_url})


# ----------------- Voting --------------------


@router.post("/{spot_id}/vote", response_model=schemas.Spot)
async def vote_spot(
    spot_id: UUID,
    vote: schemas.VoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update a vote for a spot."""
    if vote.value not in (1, -1):
        raise HTTPException(status_code=400, detail="value must be 1 or -1")

    db_vote = await db.execute(
        select(Vote).where(Vote.spot_id == spot_id, Vote.user_id == current_user.id)
    )
    db_vote = db_vote.scalars().first()

    if db_vote:
        db_vote.value = vote.value
    else:
        db_vote = Vote(spot_id=spot_id, user_id=current_user.id, value=vote.value)
        db.add(db_vote)

    await db.commit()

    # return updated spot with score - eagerly load relationships to avoid serialization issues
    result = await db.execute(
        select(Spot)
        .options(
            joinedload(Spot.user),
            joinedload(Spot.comments).joinedload(Comment.user)
        )
        .where(Spot.id == spot_id)
    )
    updated_spot = result.unique().scalar_one()
    
    score_result = await db.execute(select(func.coalesce(func.sum(Vote.value), 0)).where(Vote.spot_id == spot_id))
    updated_spot.score = score_result.scalar() or 0
    updated_spot.my_vote = vote.value
    return updated_spot


@router.delete("/{spot_id}/vote", response_model=schemas.Spot)
async def remove_vote(
    spot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Vote).where(Vote.spot_id == spot_id, Vote.user_id == current_user.id))
    vote = res.scalars().first()
    if vote:
        await db.delete(vote)
        await db.commit()

    # return updated spot with score - eagerly load relationships to avoid serialization issues
    result = await db.execute(
        select(Spot)
        .options(
            joinedload(Spot.user),
            joinedload(Spot.comments).joinedload(Comment.user)
        )
        .where(Spot.id == spot_id)
    )
    updated_spot = result.unique().scalar_one()
    
    score_result = await db.execute(select(func.coalesce(func.sum(Vote.value), 0)).where(Vote.spot_id == spot_id))
    updated_spot.score = score_result.scalar() or 0
    updated_spot.my_vote = None
    return updated_spot 