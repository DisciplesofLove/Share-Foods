from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..models.listings import FoodCategory, ListingStatus

class ListingBase(BaseModel):
    title: str
    description: str
    category: FoodCategory
    quantity: float
    quantity_unit: str
    expiration_date: datetime
    pickup_location: str
    pickup_instructions: str
    is_donation: bool = True

class ListingCreate(ListingBase):
    @validator('expiration_date')
    def ensure_future_date(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Expiration date must be in the future')
        return v

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[FoodCategory] = None
    quantity: Optional[float] = None
    quantity_unit: Optional[str] = None
    expiration_date: Optional[datetime] = None
    pickup_location: Optional[str] = None
    pickup_instructions: Optional[str] = None
    status: Optional[ListingStatus] = None

    @validator('expiration_date')
    def ensure_future_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Expiration date must be in the future')
        return v

class ListingResponse(ListingBase):
    id: int
    status: ListingStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True