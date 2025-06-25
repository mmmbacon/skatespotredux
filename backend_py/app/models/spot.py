from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..database import Base


class Spot(Base):
    __tablename__ = "spots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Using SRID 4326 for standard WGS 84 geographic coordinates (lat/lng)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False, index=True)

    photos = Column(JSONB, nullable=True, default=[])

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="spots")

    comments = relationship("Comment", back_populates="spot", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="spot", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 