from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class MetricType(str, enum.Enum):
    FOOD_RESCUED = "food_rescued"
    MEALS_PROVIDED = "meals_provided"
    CARBON_REDUCED = "carbon_reduced"
    DELIVERIES_COMPLETED = "deliveries_completed"
    VOLUNTEER_HOURS = "volunteer_hours"

class ImpactMetric(Base):
    __tablename__ = "impact_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(Enum(MetricType))
    value = Column(Float)
    metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("food_listings.id"), nullable=True)
    
    # Relationships
    user = relationship("User")
    listing = relationship("FoodListing")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    details = Column(JSON)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User")