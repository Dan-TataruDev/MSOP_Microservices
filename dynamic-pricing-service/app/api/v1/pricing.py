"""
Pricing API endpoints.

These are the primary endpoints called by the Booking Service
to get prices for bookings.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.pricing_service import PricingService
from app.schemas.pricing import (
    PriceCalculationRequest,
    PriceCalculationResponse,
    PriceEstimateRequest,
    PriceEstimateResponse,
    BulkPriceRequest,
    BulkPriceResponse,
)

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post(
    "/calculate",
    response_model=PriceCalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate price for a booking",
    description="""
    Calculate the dynamic price for a booking request.
    
    This endpoint is called by the Booking Service when creating a booking.
    It returns a versioned, auditable price decision with:
    - Calculated total price
    - Tax breakdown
    - Applied discounts
    - Price validity period
    - Decision reference for audit
    
    The price is calculated using:
    1. AI/ML model (primary, if available)
    2. Rule-based engine (fallback)
    3. Base price with demand adjustment (last resort)
    """
)
async def calculate_price(
    request: PriceCalculationRequest,
    http_request: Request,
    db: Session = Depends(get_db),
) -> PriceCalculationResponse:
    """Calculate dynamic price for a booking."""
    service = PricingService(db)
    
    # Extract client info for audit
    client_ip = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("user-agent")
    
    return await service.calculate_price(
        request=request,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/estimate",
    response_model=PriceEstimateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get price estimate",
    description="""
    Get a non-binding price estimate for availability checks.
    
    This endpoint provides a quick price estimate without creating
    a committed price decision. Use this for:
    - Availability search results
    - Price preview in UI
    - Comparison shopping
    
    Note: The actual price may differ at booking time based on
    real-time demand and other factors.
    """
)
async def estimate_price(
    request: PriceEstimateRequest,
    db: Session = Depends(get_db),
) -> PriceEstimateResponse:
    """Get a non-binding price estimate."""
    service = PricingService(db)
    return await service.estimate_price(request)


@router.post(
    "/bulk",
    response_model=BulkPriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get prices for multiple time slots",
    description="""
    Calculate prices for multiple time slots in a single request.
    
    Useful for:
    - Showing price variations throughout the day
    - Availability calendars with pricing
    - Optimal time slot recommendations
    """
)
async def bulk_price_calculation(
    request: BulkPriceRequest,
    db: Session = Depends(get_db),
) -> BulkPriceResponse:
    """Calculate prices for multiple time slots."""
    service = PricingService(db)
    
    prices = []
    for time_slot in request.time_slots:
        estimate_request = PriceEstimateRequest(
            venue_id=request.venue_id,
            venue_type=request.venue_type,
            booking_time=time_slot,
            party_size=request.party_size,
            duration_minutes=request.duration_minutes,
        )
        
        estimate = await service.estimate_price(estimate_request)
        
        prices.append({
            "time_slot": time_slot.isoformat(),
            "estimated_price": str(estimate.estimated_price),
            "demand_level": estimate.demand_level,
            "is_peak_time": estimate.is_peak_time,
        })
    
    return BulkPriceResponse(prices=prices)


@router.post(
    "/accept/{decision_reference}",
    status_code=status.HTTP_200_OK,
    summary="Mark price decision as accepted",
    description="""
    Mark a price decision as accepted when a booking is created.
    
    Called by the Booking Service after successfully creating a booking
    with the quoted price.
    """
)
async def accept_price_decision(
    decision_reference: str,
    booking_id: str,
    booking_reference: str,
    db: Session = Depends(get_db),
):
    """Mark a price decision as accepted."""
    from uuid import UUID
    
    service = PricingService(db)
    success = service.mark_decision_accepted(
        decision_reference=decision_reference,
        booking_id=UUID(booking_id),
        booking_reference=booking_reference,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Price decision {decision_reference} not found or expired"
        )
    
    return {"status": "accepted", "decision_reference": decision_reference}


