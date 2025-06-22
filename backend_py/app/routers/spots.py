from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from .. import schemas
from ..database import get_db
from ..models import Spot, User
from ..routers.auth import get_current_user

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
    return db_spot


@router.get("/", response_model=List[schemas.Spot])
async def get_spots(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve a list of skate spots.
    """
    from sqlalchemy.future import select

    result = await db.execute(select(Spot).offset(skip).limit(limit))
    spots = result.scalars().all()
    return spots 