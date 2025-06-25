from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base

class Vote(Base):
    __tablename__ = "votes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id", ondelete="CASCADE"), nullable=False)
    value = Column(Integer, nullable=False)  # +1 or -1
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="votes")
    spot = relationship("Spot", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "spot_id", name="uq_user_spot_vote"),
    ) 