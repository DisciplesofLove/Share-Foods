from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..models.tasks import TaskStatus, TaskType

class TaskBase(BaseModel):
    task_type: TaskType
    title: str
    description: str
    location: str
    scheduled_time: datetime
    estimated_duration: int  # in minutes
    priority: int = 1

    @validator('scheduled_time')
    def ensure_future_time(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v

    @validator('estimated_duration')
    def ensure_positive_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v

    @validator('priority')
    def ensure_valid_priority(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Priority must be between 1 and 5')
        return v

class TaskCreate(TaskBase):
    listing_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    priority: Optional[int] = None
    status: Optional[TaskStatus] = None
    volunteer_id: Optional[int] = None

    @validator('scheduled_time')
    def ensure_future_time(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v

    @validator('estimated_duration')
    def ensure_positive_duration(cls, v):
        if v and v <= 0:
            raise ValueError('Duration must be positive')
        return v

    @validator('priority')
    def ensure_valid_priority(cls, v):
        if v and not 1 <= v <= 5:
            raise ValueError('Priority must be between 1 and 5')
        return v

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    volunteer_id: Optional[int]
    listing_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True