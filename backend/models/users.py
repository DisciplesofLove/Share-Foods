from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class UserType(str, enum.Enum):
    DONOR = "donor"
    RECIPIENT = "recipient"
    TRADER = "trader"
    VOLUNTEER = "volunteer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    bio = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    location = Column(String)
    contact_number = Column(String)
    user_type = Column(Enum(UserType))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    listings = relationship("FoodListing", back_populates="owner")
    volunteer_tasks = relationship("VolunteerTask", back_populates="volunteer")
    storefront = relationship("Storefront", back_populates="owner", uselist=False)
    impact_metrics = relationship("ImpactMetric", back_populates="user")