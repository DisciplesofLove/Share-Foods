from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.database import SessionLocal
from ..models.trades import Trade, TradeMessage, TradeStatus
from ..models.users import User, UserType
from ..models.listings import FoodListing, ListingStatus
from ..schemas.trades import (
    TradeCreate, TradeUpdate, TradeResponse,
    TradeMessageCreate, TradeMessageResponse
)
from .auth import get_current_active_user, get_db
from ..services.notifications import send_notification
from ..services.blockchain import BlockchainLogger

router = APIRouter(
    prefix="/trades",
    tags=["Trades"]
)

blockchain = BlockchainLogger()

@router.post("/", response_model=TradeResponse)
async def create_trade(
    trade: TradeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify listings exist and are available
    initiator_listing = db.query(FoodListing).filter(
        FoodListing.id == trade.initiator_listing_id
    ).first()
    responder_listing = db.query(FoodListing).filter(
        FoodListing.id == trade.responder_listing_id
    ).first()
    
    if not initiator_listing or not responder_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if (initiator_listing.status != ListingStatus.AVAILABLE or 
        responder_listing.status != ListingStatus.AVAILABLE):
        raise HTTPException(status_code=400, detail="One or both listings are not available")
    
    if initiator_listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to trade this listing")
    
    # Create trade
    db_trade = Trade(
        initiator_id=current_user.id,
        responder_id=trade.responder_id,
        initiator_listing_id=trade.initiator_listing_id,
        responder_listing_id=trade.responder_listing_id,
        initiator_notes=trade.initiator_notes,
        terms=trade.terms
    )
    db.add(db_trade)
    
    # Update listing statuses
    initiator_listing.status = ListingStatus.IN_TRANSIT
    responder_listing.status = ListingStatus.IN_TRANSIT
    
    db.commit()
    db.refresh(db_trade)
    
    # Notify responder
    await send_notification(
        trade.responder_id,
        f"New trade proposal received for your listing: {responder_listing.title}"
    )
    
    return db_trade

@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    status: Optional[TradeStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Trade).filter(
        (Trade.initiator_id == current_user.id) |
        (Trade.responder_id == current_user.id)
    )
    
    if status:
        query = query.filter(Trade.status == status)
        
    return query.all()

@router.put("/{trade_id}", response_model=TradeResponse)
async def update_trade(
    trade_id: int,
    trade_update: TradeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
        
    if not (current_user.id == db_trade.initiator_id or 
            current_user.id == db_trade.responder_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this trade")
    
    # Handle status updates
    if trade_update.status:
        if trade_update.status == TradeStatus.COMPLETED:
            db_trade.completion_time = datetime.utcnow()
            
            # Log completion to blockchain
            await blockchain.log_transaction(
                "trade_completed",
                {
                    "trade_id": trade_id,
                    "initiator_id": db_trade.initiator_id,
                    "responder_id": db_trade.responder_id,
                    "completion_time": db_trade.completion_time.isoformat()
                }
            )
        
        # Update listing statuses
        if trade_update.status in [TradeStatus.REJECTED, TradeStatus.CANCELLED]:
            initiator_listing = db.query(FoodListing).filter(
                FoodListing.id == db_trade.initiator_listing_id
            ).first()
            responder_listing = db.query(FoodListing).filter(
                FoodListing.id == db_trade.responder_listing_id
            ).first()
            
            if initiator_listing:
                initiator_listing.status = ListingStatus.AVAILABLE
            if responder_listing:
                responder_listing.status = ListingStatus.AVAILABLE
    
    for field, value in trade_update.dict(exclude_unset=True).items():
        setattr(db_trade, field, value)
    
    db.commit()
    db.refresh(db_trade)
    
    # Send notifications
    if trade_update.status:
        notify_user_id = (db_trade.responder_id if current_user.id == db_trade.initiator_id 
                         else db_trade.initiator_id)
        await send_notification(
            notify_user_id,
            f"Trade #{trade_id} status updated to: {trade_update.status}"
        )
    
    return db_trade

@router.post("/{trade_id}/messages", response_model=TradeMessageResponse)
async def create_trade_message(
    trade_id: int,
    message: TradeMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify trade exists and user is participant
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
        
    if not (current_user.id == trade.initiator_id or 
            current_user.id == trade.responder_id):
        raise HTTPException(status_code=403, detail="Not authorized to message this trade")
    
    db_message = TradeMessage(
        trade_id=trade_id,
        sender_id=current_user.id,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Notify other participant
    notify_user_id = (trade.responder_id if current_user.id == trade.initiator_id 
                     else trade.initiator_id)
    await send_notification(
        notify_user_id,
        f"New message in Trade #{trade_id}: {message.message[:50]}..."
    )
    
    return db_message

@router.get("/{trade_id}/messages", response_model=List[TradeMessageResponse])
async def get_trade_messages(
    trade_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify trade exists and user is participant
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
        
    if not (current_user.id == trade.initiator_id or 
            current_user.id == trade.responder_id):
        raise HTTPException(status_code=403, detail="Not authorized to view these messages")
    
    return db.query(TradeMessage).filter(TradeMessage.trade_id == trade_id).all()