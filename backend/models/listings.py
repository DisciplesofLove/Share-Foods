from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class FoodCategory(str, enum.Enum):
    PRODUCE = "produce"
    DAIRY = "dairy"
    MEAT = "meat"
    BAKERY = "bakery"
    PANTRY = "pantry"
    PREPARED = "prepared"

class ListingStatus(str, enum.Enum):
    AVAILABLE = "available"
    CLAIMED = "claimed"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class FoodListing(Base):
    __tablename__ = "food_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    category = Column(Enum(FoodCategory))
    quantity = Column(Float)
    quantity_unit = Column(String)
    expiration_date = Column(DateTime)
    pickup_location = Column(String)
    pickup_instructions = Column(String)
    is_donation = Column(Boolean, default=True)
    status = Column(Enum(ListingStatus), default=ListingStatus.AVAILABLE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="listings")
    claims = relationship("Claim", back_populates="listing")