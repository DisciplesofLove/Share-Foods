from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class SystemStats(BaseModel):
    total_users: int
    active_users_24h: int
    total_listings: int
    active_listings: int
    total_donations: float  # in kg
    total_deliveries: int
    system_health: Dict[str, str]
    performance_metrics: Dict[str, float]

class UserStats(BaseModel):
    total_users: int
    user_types: Dict[str, int]
    new_users_30d: int
    active_users: Dict[str, int]  # different time periods
    engagement_metrics: Dict[str, float]

class ContentModerationAction(BaseModel):
    content_type: str  # "listing", "review", "comment"
    content_id: int
    action: str  # "remove", "flag", "approve"
    reason: str

class FeatureFlag(BaseModel):
    enabled: bool
    description: Optional[str]
    conditions: Optional[Dict]

class AdminMetrics(BaseModel):
    period_start: datetime
    period_end: datetime
    user_metrics: UserStats
    system_metrics: SystemStats
    impact_metrics: Dict[str, float]
    financial_metrics: Optional[Dict[str, float]]