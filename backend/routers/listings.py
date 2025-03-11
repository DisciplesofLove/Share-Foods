from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.database import SessionLocal
from ..models.listings import FoodListing, FoodCategory, ListingStatus
from ..models.users import User, UserType
from ..schemas.listings import ListingCreate, ListingUpdate, ListingResponse
from .auth import get_current_active_user, get_db
from ..services.ai_logistics import LogisticsOptimizer

router = APIRouter(
    prefix="/listings",
    tags=["Listings"]
)

logistics = LogisticsOptimizer()

@router.post("/", response_model=ListingResponse)
async def create_listing(
    listing: ListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type not in [UserType.DONOR, UserType.TRADER]:
        raise HTTPException(
            status_code=403,
            detail="Only donors and traders can create listings"
        )
    
    db_listing = FoodListing(**listing.dict(), owner_id=current_user.id)
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

@router.get("/", response_model=List[ListingResponse])
async def get_listings(
    skip: int = 0,
    limit: int = 100,
    category: Optional[FoodCategory] = None,
    status: Optional[ListingStatus] = None,
    is_donation: Optional[bool] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FoodListing)
    
    if category:
        query = query.filter(FoodListing.category == category)
    if status:
        query = query.filter(FoodListing.status == status)
    if is_donation is not None:
        query = query.filter(FoodListing.is_donation == is_donation)
    if location:
        query = query.filter(FoodListing.pickup_location.ilike(f"%{location}%"))
        
    return query.offset(skip).limit(limit).all()

@router.get("/recommendations", response_model=List[ListingResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered listing recommendations based on user profile and history."""
    available_listings = db.query(FoodListing).filter(
        FoodListing.status == ListingStatus.AVAILABLE
    ).all()
    
    if not available_listings:
        return []
    
    # Use AI service to match listings with recipients
    recommended_listings = logistics.match_recipients(
        {"location": current_user.location, "user_type": current_user.user_type},
        [listing.__dict__ for listing in available_listings]
    )
    
    return recommended_listings

@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    listing_update: ListingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
        
    if db_listing.owner_id != current_user.id and current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")
    
    for field, value in listing_update.dict(exclude_unset=True).items():
        setattr(db_listing, field, value)
    
    db.commit()
    db.refresh(db_listing)
    return db_listing

@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if listing exists
    listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Verify authorization
    if listing.owner_id != current_user.id and current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    
    # Delete the listing
    db.delete(listing)
    db.commit()
    db_listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
        
    if db_listing.owner_id != current_user.id and current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    
    db.delete(db_listing)
    db.commit()