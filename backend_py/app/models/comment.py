from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(Text, nullable=False)

    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id"), nullable=False)
    spot = relationship("Spot", back_populates="comments")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="comments")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 