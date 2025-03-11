from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Storefront(Base):
    __tablename__ = "storefronts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    logo_url = Column(String, nullable=True)
    theme_colors = Column(JSON, nullable=True)  # Store color preferences
    contact_info = Column(JSON)  # Store additional contact details
    social_links = Column(JSON, nullable=True)  # Store social media links
    impact_metrics = Column(JSON, default=dict)  # Store calculated impact metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="storefront")
    reviews = relationship("StoreReview", back_populates="storefront")

class StoreReview(Base):
    __tablename__ = "store_reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float)  # 1-5 stars
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    storefront_id = Column(Integer, ForeignKey("storefronts.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    storefront = relationship("Storefront", back_populates="reviews")
    reviewer = relationship("User")