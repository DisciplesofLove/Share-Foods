from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List

from ..models.analytics import ImpactMetric, MetricType
from ..models.users import User, UserType
from ..models.listings import FoodListing, ListingStatus
from ..models.tasks import VolunteerTask, TaskStatus

class AnalyticsService:
    async def get_admin_metrics(self, db: Session, start_date: datetime, end_date: datetime) -> Dict:
        """Get comprehensive metrics for admin dashboard."""
        return {
            "period_start": start_date,
            "period_end": end_date,
            "user_metrics": await self.get_user_statistics(db),
            "system_metrics": await self.get_system_statistics(db),
            "impact_metrics": await self.calculate_impact_metrics(db, start_date, end_date),
            "financial_metrics": await self.calculate_financial_metrics(db, start_date, end_date)
        }

    async def get_user_statistics(self, db: Session) -> Dict:
        """Get detailed user statistics."""
        total_users = db.query(func.count(User.id)).scalar()
        
        # Get user counts by type
        user_types = {}
        for user_type in UserType:
            count = db.query(func.count(User.id)).filter(
                User.user_type == user_type
            ).scalar()
            user_types[user_type.value] = count
        
        # Get new users in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users = db.query(func.count(User.id)).filter(
            User.created_at >= thirty_days_ago
        ).scalar()
        
        return {
            "total_users": total_users,
            "user_types": user_types,
            "new_users_30d": new_users,
            "active_users": {
                "24h": self._get_active_users(db, hours=24),
                "7d": self._get_active_users(db, days=7),
                "30d": self._get_active_users(db, days=30)
            },
            "engagement_metrics": await self.calculate_engagement_metrics(db)
        }

    async def get_system_statistics(self, db: Session) -> Dict:
        """Get system-wide statistics."""
        return {
            "total_users": db.query(func.count(User.id)).scalar(),
            "active_users_24h": self._get_active_users(db, hours=24),
            "total_listings": db.query(func.count(FoodListing.id)).scalar(),
            "active_listings": db.query(func.count(FoodListing.id)).filter(
                FoodListing.status == ListingStatus.AVAILABLE
            ).scalar(),
            "total_donations": self._calculate_total_donations(db),
            "total_deliveries": db.query(func.count(VolunteerTask.id)).filter(
                VolunteerTask.status == TaskStatus.COMPLETED
            ).scalar(),
            "system_health": self._get_system_health(),
            "performance_metrics": self._get_performance_metrics(db)
        }

    async def calculate_impact_metrics(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """Calculate environmental and social impact metrics."""
        metrics = {}
        
        for metric_type in MetricType:
            value = db.query(func.sum(ImpactMetric.value)).filter(
                ImpactMetric.metric_type == metric_type,
                ImpactMetric.timestamp.between(start_date, end_date)
            ).scalar() or 0
            metrics[metric_type.value] = value
        
        return metrics

    async def calculate_financial_metrics(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """Calculate financial metrics and cost savings."""
        # TODO: Implement financial calculations
        return {
            "estimated_food_value": 0,
            "logistics_costs": 0,
            "cost_savings": 0
        }

    async def calculate_engagement_metrics(self, db: Session) -> Dict[str, float]:
        """Calculate user engagement metrics."""
        # TODO: Implement engagement calculations
        return {
            "average_session_duration": 0,
            "listings_per_user": 0,
            "response_rate": 0
        }

    def _get_active_users(self, db: Session, days: int = None, hours: int = None) -> int:
        """Get count of users active within the specified time period."""
        if days:
            threshold = datetime.utcnow() - timedelta(days=days)
        elif hours:
            threshold = datetime.utcnow() - timedelta(hours=hours)
        else:
            threshold = datetime.utcnow() - timedelta(days=1)

        return db.query(func.count(User.id)).filter(
            User.updated_at >= threshold
        ).scalar()

    def _calculate_total_donations(self, db: Session) -> float:
        """Calculate total weight of donated food."""
        return db.query(func.sum(FoodListing.quantity)).filter(
            FoodListing.is_donation == True,
            FoodListing.status == ListingStatus.COMPLETED
        ).scalar() or 0

    def _get_system_health(self) -> Dict[str, str]:
        """Get system health indicators."""
        # TODO: Implement system health checks
        return {
            "database": "healthy",
            "cache": "healthy",
            "queues": "healthy"
        }

    def _get_performance_metrics(self, db: Session) -> Dict[str, float]:
        """Get system performance metrics."""
        # TODO: Implement performance metric calculations
        return {
            "average_response_time": 0,
            "database_latency": 0,
            "cache_hit_rate": 0
        }