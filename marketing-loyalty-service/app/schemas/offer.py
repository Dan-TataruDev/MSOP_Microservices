"""
Offer Pydantic schemas.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.offer import OfferStatus, OfferType


class OfferResponse(BaseModel):
    """Schema for offer response."""
    id: UUID
    offer_code: str
    guest_id: UUID
    campaign_id: Optional[UUID]
    offer_type: OfferType
    title: str
    description: Optional[str]
    offer_value: str
    valid_from: datetime
    valid_until: datetime
    status: OfferStatus
    
    class Config:
        from_attributes = True


class OfferListResponse(BaseModel):
    """Paginated offer list."""
    items: List[OfferResponse]
    total: int


class EligibleOffersResponse(BaseModel):
    """
    Offers eligible for a guest.
    
    This is the primary endpoint for frontend to fetch
    personalized offers to display.
    """
    guest_id: UUID
    offers: List[OfferResponse]
    loyalty_tier: Optional[str] = None
    points_balance: Optional[int] = None


class ClaimOfferRequest(BaseModel):
    """Request to claim an offer."""
    offer_code: str


class RedeemOfferRequest(BaseModel):
    """Request to redeem an offer on a booking."""
    offer_code: str
    booking_id: UUID


