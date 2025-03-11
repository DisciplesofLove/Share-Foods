from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.trades import TradeStatus

class TradeBase(BaseModel):
    initiator_listing_id: int
    responder_listing_id: int
    initiator_notes: Optional[str] = None
    terms: Dict[str, Any]

class TradeCreate(TradeBase):
    responder_id: int

class TradeUpdate(BaseModel):
    status: Optional[TradeStatus] = None
    responder_notes: Optional[str] = None
    terms: Optional[Dict[str, Any]] = None

class TradeResponse(TradeBase):
    id: int
    status: TradeStatus
    responder_notes: Optional[str]
    initiator_id: int
    responder_id: int
    completion_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TradeMessageBase(BaseModel):
    message: str

class TradeMessageCreate(TradeMessageBase):
    pass

class TradeMessageResponse(TradeMessageBase):
    id: int
    trade_id: int
    sender_id: int
    created_at: datetime

    class Config:
        orm_mode = True