from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class NotificationType(str, Enum):
    LISTING_CLAIMED = "listing_claimed"
    TRADE_PROPOSED = "trade_proposed"
    TRADE_ACCEPTED = "trade_accepted"
    TRADE_COMPLETED = "trade_completed"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    SYSTEM = "system"

class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None

class NotificationCreate(NotificationBase):
    recipient_id: int

class NotificationResponse(NotificationBase):
    id: int
    recipient_id: int
    read: bool
    created_at: datetime

    class Config:
        orm_mode = True