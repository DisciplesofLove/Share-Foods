from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class TradeStatus(str, enum.Enum):
    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(TradeStatus), default=TradeStatus.PROPOSED)
    initiator_notes = Column(String, nullable=True)
    responder_notes = Column(String, nullable=True)
    terms = Column(JSON)  # Store trade terms and conditions
    completion_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    initiator_id = Column(Integer, ForeignKey("users.id"))
    responder_id = Column(Integer, ForeignKey("users.id"))
    initiator_listing_id = Column(Integer, ForeignKey("food_listings.id"))
    responder_listing_id = Column(Integer, ForeignKey("food_listings.id"))
    
    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id])
    responder = relationship("User", foreign_keys=[responder_id])
    initiator_listing = relationship("FoodListing", foreign_keys=[initiator_listing_id])
    responder_listing = relationship("FoodListing", foreign_keys=[responder_listing_id])

class TradeMessage(Base):
    __tablename__ = "trade_messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    trade_id = Column(Integer, ForeignKey("trades.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    trade = relationship("Trade")
    sender = relationship("User")