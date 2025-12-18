"""
Offers API endpoints.

Primary endpoint for frontend to fetch personalized offers.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.services.offer_service import OfferService
from app.services.loyalty_service import LoyaltyService
from app.clients.insights_client import insights_client
from app.schemas.offer import (
    OfferResponse, EligibleOffersResponse, ClaimOfferRequest, RedeemOfferRequest
)

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/eligible/{guest_id}", response_model=EligibleOffersResponse)
async def get_eligible_offers(guest_id: UUID, db: Session = Depends(get_db)):
    """
    Get all offers a guest is eligible for.
    
    This is the main endpoint for frontend to fetch personalized offers.
    Consumes insights from external services to determine eligibility.
    """
    # Get guest insights from external services
    guest_insights = await insights_client.get_guest_insights(guest_id)
    
    # Get loyalty status
    loyalty_service = LoyaltyService(db)
    loyalty_member = loyalty_service.get_member(guest_id)
    
    # Get eligible offers
    offer_service = OfferService(db)
    offers = offer_service.get_eligible_offers(guest_id, guest_insights, loyalty_member)
    
    # Mark as presented
    for offer in offers:
        offer_service.mark_presented(offer.id)
    
    return EligibleOffersResponse(
        guest_id=guest_id,
        offers=[OfferResponse.model_validate(o) for o in offers],
        loyalty_tier=loyalty_member.tier.value if loyalty_member else None,
        points_balance=loyalty_member.points_balance if loyalty_member else None,
    )


@router.post("/claim", response_model=OfferResponse)
def claim_offer(request: ClaimOfferRequest, guest_id: UUID, db: Session = Depends(get_db)):
    """Claim an offer."""
    service = OfferService(db)
    offer = service.claim_offer(request.offer_code, guest_id)
    if not offer:
        raise HTTPException(status_code=400, detail="Unable to claim offer")
    return offer


@router.post("/redeem", response_model=OfferResponse)
def redeem_offer(request: RedeemOfferRequest, guest_id: UUID, db: Session = Depends(get_db)):
    """
    Redeem an offer on a booking.
    
    Note: This records the redemption. The actual discount calculation
    is handled by the pricing/booking service.
    """
    service = OfferService(db)
    offer = service.redeem_offer(request.offer_code, guest_id, request.booking_id)
    if not offer:
        raise HTTPException(status_code=400, detail="Unable to redeem offer")
    return offer


@router.get("/validate/{offer_code}")
def validate_offer(offer_code: str, guest_id: UUID, db: Session = Depends(get_db)):
    """
    Validate an offer for use.
    
    Called by pricing/booking services to validate before applying.
    Returns offer details without embedding pricing logic.
    """
    service = OfferService(db)
    return service.validate_offer(offer_code, guest_id)


@router.get("/{offer_code}", response_model=OfferResponse)
def get_offer(offer_code: str, db: Session = Depends(get_db)):
    """Get offer by code."""
    service = OfferService(db)
    offer = service.get_offer_by_code(offer_code)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


