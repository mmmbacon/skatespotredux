from __future__ import annotations
import uuid
import secrets
import string
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..database import Base


def generate_short_id(length: int = 4) -> str:
    """Generate a random alphanumeric ID of specified length."""
    alphabet = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class Spot(Base):
    __tablename__ = "spots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    short_id = Column(String(6), unique=True, nullable=False, index=True, default=generate_short_id)
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