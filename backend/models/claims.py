from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class ClaimStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.PENDING)
    notes = Column(String, nullable=True)
    pickup_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    listing_id = Column(Integer, ForeignKey("food_listings.id"))
    claimer_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    listing = relationship("FoodListing", back_populates="claims")
    claimer = relationship("User")