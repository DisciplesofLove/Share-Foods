from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..models.users import UserType

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    bio: Optional[str] = None
    organization: Optional[str] = None
    location: str
    contact_number: str
    user_type: UserType

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    contact_number: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True