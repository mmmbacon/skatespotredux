from __future__ import annotations
from pydantic import BaseModel, Field, validator, field_validator, field_serializer
from typing import Any, Optional, List, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from geoalchemy2.elements import WKBElement
from shapely.wkb import loads as wkb_loads
import json

from .comment import Comment

if TYPE_CHECKING:
    from .user import UserPublic

# Basic Spot schema
class SpotBase(BaseModel):
    name: str
    description: Optional[str] = None

# Schema for creating a new spot
class SpotCreate(SpotBase):
    # GeoJSON format for location
    # e.g. {"type": "Point", "coordinates": [-73.97, 40.77]}
    location: dict

# Schema for updating a spot
class SpotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[dict] = None

# Schema for reading a spot from the database
class Spot(SpotBase):
    id: UUID
    short_id: str
    user: UserPublic
    location: dict # The location will always be a GeoJSON dict in the response
    created_at: datetime
    updated_at: Optional[datetime] = None
    comments: List[Comment] = []
    score: int = 0
    my_vote: int | None = None

    @field_validator("location", mode="before")
    def validate_location(cls, v: Any) -> Any:
        if isinstance(v, WKBElement):
            # Parse the WKBElement to a Shapely geometry object
            geom = wkb_loads(v.data)
            # Convert the geometry object to a GeoJSON dict
            return json.loads(json.dumps(geom.__geo_interface__))
        elif isinstance(v, str) and v.startswith('POINT('):
            # Handle WKT string format: 'POINT(-114.03070 51.04107)'
            # Extract coordinates from the WKT string
            coords_str = v.replace('POINT(', '').replace(')', '')
            lon, lat = map(float, coords_str.split())
            return {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        return v

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        # Ensure UTC timestamps are serialized with 'Z' suffix for proper timezone handling
        return dt.isoformat() + 'Z' if dt.tzinfo is None else dt.isoformat()

    @field_serializer('updated_at')
    def serialize_updated_at(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        # Ensure UTC timestamps are serialized with 'Z' suffix for proper timezone handling
        return dt.isoformat() + 'Z' if dt.tzinfo is None else dt.isoformat()

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True 