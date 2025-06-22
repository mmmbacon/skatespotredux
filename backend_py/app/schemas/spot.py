from pydantic import BaseModel, Field, validator
from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from geoalchemy2.elements import WKBElement
from shapely.wkb import loads as wkb_loads
import json

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
    location: dict # The location will always be a GeoJSON dict in the response
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("location", pre=True, always=True)
    def validate_location(cls, v):
        if isinstance(v, WKBElement):
            # Parse the WKBElement to a Shapely geometry object
            geom = wkb_loads(v.data)
            # Convert the geometry object to a GeoJSON dict
            return json.loads(json.dumps(geom.__geo_interface__))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True 