"""
Loyalty program API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.services.loyalty_service import LoyaltyService
from app.schemas.loyalty import (
    LoyaltyMemberResponse, PointsHistoryResponse, PointsTransaction,
    EarnPointsRequest, RedeemPointsRequest
)
from app.models.loyalty import LoyaltyTier

router = APIRouter(prefix="/loyalty", tags=["loyalty"])


def _enrich_member_response(member, service: LoyaltyService) -> dict:
    """Add computed fields to member response."""
    from app.models.loyalty import LoyaltyProgram
    
    program = service.db.query(LoyaltyProgram).filter(LoyaltyProgram.id == member.program_id).first()
    
    next_tier = None
    points_to_next = None
    
    if member.tier == LoyaltyTier.BRONZE and program:
        next_tier = LoyaltyTier.SILVER
        points_to_next = max(0, program.silver_threshold - member.lifetime_points)
    elif member.tier == LoyaltyTier.SILVER and program:
        next_tier = LoyaltyTier.GOLD
        points_to_next = max(0, program.gold_threshold - member.lifetime_points)
    elif member.tier == LoyaltyTier.GOLD and program:
        next_tier = LoyaltyTier.PLATINUM
        points_to_next = max(0, program.platinum_threshold - member.lifetime_points)
    
    return {
        **member.__dict__,
        "next_tier": next_tier,
        "points_to_next_tier": points_to_next,
    }


@router.get("/member/{guest_id}", response_model=LoyaltyMemberResponse)
def get_member_status(guest_id: UUID, db: Session = Depends(get_db)):
    """Get loyalty member status for a guest."""
    service = LoyaltyService(db)
    member = service.get_or_create_member(guest_id)
    return _enrich_member_response(member, service)


@router.get("/member/{guest_id}/history", response_model=PointsHistoryResponse)
def get_points_history(guest_id: UUID, limit: int = 20, db: Session = Depends(get_db)):
    """Get points transaction history."""
    service = LoyaltyService(db)
    member = service.get_member(guest_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    transactions = service.get_points_history(guest_id, limit)
    return PointsHistoryResponse(
        items=[PointsTransaction.model_validate(t) for t in transactions],
        total=len(transactions),
        current_balance=member.points_balance,
    )


@router.post("/points/earn", response_model=LoyaltyMemberResponse)
def earn_points(request: EarnPointsRequest, db: Session = Depends(get_db)):
    """
    Award points to a member.
    
    Called by other services (booking, campaigns) when points should be awarded.
    """
    service = LoyaltyService(db)
    member = service.earn_points(
        guest_id=request.guest_id,
        points=request.points,
        description=request.description,
        source_type=request.source_type,
        source_id=request.source_id,
    )
    return _enrich_member_response(member, service)


@router.post("/points/redeem", response_model=LoyaltyMemberResponse)
def redeem_points(request: RedeemPointsRequest, db: Session = Depends(get_db)):
    """Redeem points from a member's balance."""
    service = LoyaltyService(db)
    member = service.redeem_points(
        guest_id=request.guest_id,
        points=request.points,
        description=request.description,
        source_type=request.source_type,
        source_id=request.source_id,
    )
    if not member:
        raise HTTPException(status_code=400, detail="Insufficient points or member not found")
    return _enrich_member_response(member, service)


