from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# Basic Spot schema
class SpotBase(BaseModel):
    name: str
    description: Optional[str] = None

# Schema for creating a new spot
class SpotCreate(SpotBase):
    # GeoJSON format for location
    # e.g. {"type": "Point", "coordinates": [-73.97, 40.77]}
    location: dict

# Schema for reading a spot from the database
class Spot(SpotBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    # We will likely want to return GeoJSON here as well in the future
    # but for now we'll just return the WKT from the db
    location: str

    class Config:
        orm_mode = True 