from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..models.claims import ClaimStatus

class ClaimBase(BaseModel):
    listing_id: int
    notes: Optional[str] = None
    pickup_time: datetime

    @validator('pickup_time')
    def ensure_future_time(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Pickup time must be in the future')
        return v

class ClaimCreate(ClaimBase):
    pass

class ClaimUpdate(BaseModel):
    notes: Optional[str] = None
    pickup_time: Optional[datetime] = None
    status: Optional[ClaimStatus] = None

    @validator('pickup_time')
    def ensure_future_time(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Pickup time must be in the future')
        return v

class ClaimResponse(ClaimBase):
    id: int
    status: ClaimStatus
    claimer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True