from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from geoalchemy2.functions import ST_MakeEnvelope, ST_Contains
from typing import List, Optional
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
async def get_spots(
    db: AsyncSession = Depends(get_db),
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
    from sqlalchemy.future import select

    query = select(Spot)

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
    spots = result.scalars().all()
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