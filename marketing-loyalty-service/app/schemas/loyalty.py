"""
Loyalty program Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.loyalty import LoyaltyTier


class LoyaltyProgramResponse(BaseModel):
    """Loyalty program configuration."""
    id: UUID
    name: str
    base_earn_rate: float
    silver_threshold: int
    gold_threshold: int
    platinum_threshold: int
    
    class Config:
        from_attributes = True


class LoyaltyMemberResponse(BaseModel):
    """Member loyalty status."""
    id: UUID
    guest_id: UUID
    tier: LoyaltyTier
    points_balance: int
    lifetime_points: int
    enrolled_at: datetime
    next_tier: Optional[LoyaltyTier] = None
    points_to_next_tier: Optional[int] = None
    
    class Config:
        from_attributes = True


class PointsTransaction(BaseModel):
    """Points transaction record."""
    id: UUID
    points: int
    description: str
    source_type: str
    source_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PointsHistoryResponse(BaseModel):
    """Paginated points history."""
    items: List[PointsTransaction]
    total: int
    current_balance: int


class EarnPointsRequest(BaseModel):
    """Request to earn points from an external event."""
    guest_id: UUID
    points: int = Field(..., gt=0)
    description: str
    source_type: str  # "booking", "campaign", "manual"
    source_id: Optional[UUID] = None


class RedeemPointsRequest(BaseModel):
    """Request to redeem points."""
    guest_id: UUID
    points: int = Field(..., gt=0)
    description: str
    source_type: str = "redemption"
    source_id: Optional[UUID] = None


