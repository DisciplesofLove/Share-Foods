from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

from .notifications import NotificationType

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType))
    title = Column(String)
    message = Column(String)
    data = Column(JSON, nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"))
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recipient = relationship("User", back_populates="notifications")