from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..models.database import SessionLocal
from ..models.tasks import VolunteerTask, TaskStatus, TaskType
from ..models.users import User, UserType
from ..models.listings import FoodListing
from ..schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from .auth import get_current_active_user, get_db
from ..services.ai_logistics import LogisticsOptimizer
from ..services.notifications import send_notification

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

logistics = LogisticsOptimizer()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type not in [UserType.ADMIN, UserType.DONOR]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and donors can create tasks"
        )
    
    # Verify listing exists
    listing = db.query(FoodListing).filter(FoodListing.id == task.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    db_task = VolunteerTask(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Try to find and notify suitable volunteers
    await notify_available_volunteers(db_task, db)
    
    return db_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    upcoming: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(VolunteerTask)
    
    # Filter based on user type
    if current_user.user_type == UserType.VOLUNTEER:
        query = query.filter(
            (VolunteerTask.volunteer_id == current_user.id) |
            (VolunteerTask.status == TaskStatus.PENDING)
        )
    
    if status:
        query = query.filter(VolunteerTask.status == status)
    if task_type:
        query = query.filter(VolunteerTask.task_type == task_type)
    if upcoming:
        query = query.filter(
            VolunteerTask.scheduled_time > datetime.utcnow()
        ).order_by(VolunteerTask.scheduled_time)
    
    return query.offset(skip).limit(limit).all()

@router.get("/available", response_model=List[TaskResponse])
async def get_available_tasks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.VOLUNTEER:
        raise HTTPException(
            status_code=403,
            detail="Only volunteers can view available tasks"
        )
    
    # Get pending tasks near the volunteer's location
    tasks = db.query(VolunteerTask).filter(
        VolunteerTask.status == TaskStatus.PENDING,
        VolunteerTask.scheduled_time > datetime.utcnow()
    ).all()
    
    # Use AI service to optimize task suggestions
    return logistics.optimize_volunteer_tasks(
        current_user.location,
        [task.__dict__ for task in tasks]
    )

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(VolunteerTask).filter(VolunteerTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if not (current_user.user_type == UserType.ADMIN or 
            (current_user.user_type == UserType.VOLUNTEER and 
             current_user.id == db_task.volunteer_id)):
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    # Handle volunteer assignment
    if (task_update.volunteer_id is not None and 
        task_update.volunteer_id != db_task.volunteer_id):
        if current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only admins can reassign tasks"
            )
        # Verify new volunteer exists
        new_volunteer = db.query(User).filter(
            User.id == task_update.volunteer_id,
            User.user_type == UserType.VOLUNTEER
        ).first()
        if not new_volunteer:
            raise HTTPException(
                status_code=404,
                detail="Volunteer not found"
            )
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.post("/{task_id}/volunteer", response_model=TaskResponse)
async def volunteer_for_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.VOLUNTEER:
        raise HTTPException(
            status_code=403,
            detail="Only volunteers can accept tasks"
        )
    
    db_task = db.query(VolunteerTask).filter(VolunteerTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Task is not available for volunteers"
        )
    
    db_task.volunteer_id = current_user.id
    db_task.status = TaskStatus.ASSIGNED
    
    db.commit()
    db.refresh(db_task)
    
    # Notify task creator
    listing = db.query(FoodListing).filter(FoodListing.id == db_task.listing_id).first()
    if listing:
        await send_notification(
            listing.owner_id,
            f"Volunteer {current_user.full_name} has accepted your task: {db_task.title}"
        )
    
    return db_task

async def notify_available_volunteers(task: VolunteerTask, db: Session):
    """Helper function to notify nearby volunteers about new tasks."""
    # Find volunteers near the task location
    volunteers = db.query(User).filter(
        User.user_type == UserType.VOLUNTEER,
        User.is_active == True
    ).all()
    
    # Use AI service to find suitable volunteers based on location and availability
    suitable_volunteers = logistics.match_volunteers(
        task.__dict__,
        [volunteer.__dict__ for volunteer in volunteers]
    )
    
    # Send notifications to suitable volunteers
    for volunteer in suitable_volunteers:
        await send_notification(
            volunteer['id'],
            f"New task available in your area: {task.title}"
        )