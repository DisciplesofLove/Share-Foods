from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskType(str, enum.Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"
    SORTING = "sorting"
    INSPECTION = "inspection"

class VolunteerTask(Base):
    __tablename__ = "volunteer_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(Enum(TaskType))
    title = Column(String)
    description = Column(String)
    location = Column(String)
    scheduled_time = Column(DateTime)
    estimated_duration = Column(Integer)  # in minutes
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    volunteer_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("food_listings.id"))
    
    # Relationships
    volunteer = relationship("User", back_populates="volunteer_tasks")
    listing = relationship("FoodListing")