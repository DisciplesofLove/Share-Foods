from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..models.database import SessionLocal
from ..models.users import User, UserType
from ..models.listings import FoodListing
from ..models.analytics import ImpactMetric, ActivityLog
from ..schemas.admin import (
    SystemStats, UserStats, ContentModerationAction,
    FeatureFlag, AdminMetrics
)
from .auth import get_current_active_user, get_db
from ..services.analytics import AnalyticsService
from ..services.notifications import send_notification

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

analytics = AnalyticsService()

def check_admin_access(current_user: User = Depends(get_current_active_user)):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can access this endpoint"
        )
    return current_user

@router.get("/metrics", response_model=AdminMetrics)
async def get_admin_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get comprehensive system metrics and statistics."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    return await analytics.get_admin_metrics(db, start_date, end_date)

@router.get("/users/stats", response_model=UserStats)
async def get_user_statistics(
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get detailed user statistics and engagement metrics."""
    return await analytics.get_user_statistics(db)

@router.post("/users/{user_id}/moderate")
async def moderate_user(
    user_id: int,
    action: str,
    reason: str,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Moderate user accounts (suspend, warn, reinstate)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if action == "suspend":
        user.is_active = False
        await send_notification(user.id, f"Your account has been suspended. Reason: {reason}")
    elif action == "reinstate":
        user.is_active = True
        await send_notification(user.id, "Your account has been reinstated")
    elif action == "warn":
        await send_notification(user.id, f"Warning: {reason}")

    # Log moderation action
    log = ActivityLog(
        user_id=current_user.id,
        action=f"user_moderation_{action}",
        details={"target_user": user_id, "reason": reason}
    )
    db.add(log)
    db.commit()

    return {"status": "success", "message": f"User {action} completed"}

@router.post("/content/moderate")
async def moderate_content(
    action: ContentModerationAction,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Moderate content (listings, reviews, comments)."""
    if action.content_type == "listing":
        listing = db.query(FoodListing).filter(FoodListing.id == action.content_id).first()
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        if action.action == "remove":
            db.delete(listing)
            await send_notification(
                listing.owner_id,
                f"Your listing has been removed. Reason: {action.reason}"
            )
    
    # Log moderation action
    log = ActivityLog(
        user_id=current_user.id,
        action=f"content_moderation_{action.action}",
        details={
            "content_type": action.content_type,
            "content_id": action.content_id,
            "reason": action.reason
        }
    )
    db.add(log)
    db.commit()
    
    return {"status": "success", "message": "Content moderation completed"}

@router.get("/system/stats", response_model=SystemStats)
async def get_system_statistics(
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics and performance metrics."""
    return await analytics.get_system_statistics(db)

@router.put("/features/{feature_name}")
async def update_feature_flag(
    feature_name: str,
    feature: FeatureFlag,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Update feature flag settings."""
    # TODO: Implement feature flag management system
    return {"status": "success", "message": f"Feature {feature_name} updated"}