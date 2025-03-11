from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..models.database import SessionLocal
from ..models.claims import Claim, ClaimStatus
from ..models.listings import FoodListing, ListingStatus
from ..models.users import User, UserType
from ..schemas.claims import ClaimCreate, ClaimUpdate, ClaimResponse
from .auth import get_current_active_user, get_db
from ..services.ai_logistics import LogisticsOptimizer

router = APIRouter(
    prefix="/claims",
    tags=["Claims"]
)

logistics = LogisticsOptimizer()

@router.post("/", response_model=ClaimResponse)
async def create_claim(
    claim: ClaimCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if listing exists and is available
    listing = db.query(FoodListing).filter(FoodListing.id == claim.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != ListingStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Listing is not available")
    
    # Create claim
    db_claim = Claim(
        **claim.dict(),
        claimer_id=current_user.id,
        status=ClaimStatus.PENDING
    )
    db.add(db_claim)
    
    # Update listing status
    listing.status = ListingStatus.CLAIMED
    
    db.commit()
    db.refresh(db_claim)
    return db_claim

@router.get("/", response_model=List[ClaimResponse])
async def get_claims(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Return claims based on user type
    if current_user.user_type == UserType.ADMIN:
        return db.query(Claim).all()
    elif current_user.user_type in [UserType.DONOR, UserType.TRADER]:
        return db.query(Claim).join(FoodListing).filter(
            FoodListing.owner_id == current_user.id
        ).all()
    else:
        return db.query(Claim).filter(Claim.claimer_id == current_user.id).all()

@router.put("/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_id: int,
    claim_update: ClaimUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Check permissions
    listing = db.query(FoodListing).filter(FoodListing.id == db_claim.listing_id).first()
    if not (current_user.id == listing.owner_id or 
            current_user.id == db_claim.claimer_id or 
            current_user.user_type == UserType.ADMIN):
        raise HTTPException(status_code=403, detail="Not authorized to update this claim")
    
    # Update claim
    for field, value in claim_update.dict(exclude_unset=True).items():
        setattr(db_claim, field, value)
    
    # Update listing status based on claim status
    if claim_update.status == ClaimStatus.APPROVED:
        listing.status = ListingStatus.IN_TRANSIT
    elif claim_update.status == ClaimStatus.REJECTED:
        listing.status = ListingStatus.AVAILABLE
    elif claim_update.status == ClaimStatus.CANCELLED:
        listing.status = ListingStatus.AVAILABLE
    
    db.commit()
    db.refresh(db_claim)
    return db_claim