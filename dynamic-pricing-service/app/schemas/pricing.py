"""
Pydantic schemas for pricing calculation APIs.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class PriceBreakdown(BaseModel):
    """Detailed breakdown of price components."""
    base_price: Decimal = Field(..., description="Base price before adjustments")
    
    # Adjustments
    demand_adjustment: Decimal = Field(default=Decimal("0"), description="Demand-based adjustment")
    seasonal_adjustment: Decimal = Field(default=Decimal("0"), description="Seasonal adjustment")
    time_adjustment: Decimal = Field(default=Decimal("0"), description="Time-of-day/week adjustment")
    loyalty_adjustment: Decimal = Field(default=Decimal("0"), description="Loyalty tier adjustment")
    promotional_adjustment: Decimal = Field(default=Decimal("0"), description="Promotional adjustment")
    ai_adjustment: Decimal = Field(default=Decimal("0"), description="AI model adjustment")
    
    # Totals
    subtotal: Decimal = Field(..., description="Subtotal before tax")
    tax_amount: Decimal = Field(default=Decimal("0"), description="Tax amount")
    discount_amount: Decimal = Field(default=Decimal("0"), description="Total discounts")
    total: Decimal = Field(..., description="Final total price")
    
    # Applied rules
    applied_rules: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of pricing rules that were applied"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "base_price": "100.00",
                "demand_adjustment": "15.00",
                "seasonal_adjustment": "10.00",
                "time_adjustment": "0.00",
                "loyalty_adjustment": "-5.00",
                "promotional_adjustment": "0.00",
                "ai_adjustment": "8.50",
                "subtotal": "128.50",
                "tax_amount": "12.85",
                "discount_amount": "5.00",
                "total": "141.35",
                "applied_rules": [
                    {"rule_id": "high_demand", "effect": "+15%"},
                    {"rule_id": "christmas_season", "effect": "+10%"},
                    {"rule_id": "gold_member", "effect": "-5%"}
                ]
            }
        }


class PriceCalculationRequest(BaseModel):
    """
    Request schema for calculating a price.
    
    This is called by the Booking Service when creating a booking.
    Returns a versioned, auditable price decision.
    """
    venue_id: UUID = Field(..., description="Venue ID")
    venue_type: str = Field(..., description="Type of venue (hotel, restaurant, etc.)")
    venue_name: Optional[str] = Field(None, description="Venue name for display")
    
    # Booking details
    booking_time: datetime = Field(..., description="Booking date and time")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duration in minutes")
    party_size: int = Field(..., ge=1, description="Number of guests/people")
    
    # Guest context (for personalized pricing)
    guest_id: Optional[UUID] = Field(None, description="Guest ID for loyalty pricing")
    guest_tier: Optional[str] = Field(None, description="Guest loyalty tier")
    
    # Product/service (for granular pricing)
    product_id: Optional[UUID] = Field(None, description="Specific product/service ID")
    
    # Options
    include_breakdown: bool = Field(default=True, description="Include detailed breakdown")
    quote_validity_minutes: int = Field(default=30, ge=5, le=1440, description="How long the quote is valid")
    
    # Request tracking
    request_id: Optional[str] = Field(None, description="Correlation ID for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "venue_id": "223e4567-e89b-12d3-a456-426614174000",
                "venue_type": "restaurant",
                "venue_name": "Fine Dining Restaurant",
                "booking_time": "2024-12-25T19:00:00Z",
                "duration_minutes": 120,
                "party_size": 4,
                "guest_id": "123e4567-e89b-12d3-a456-426614174000",
                "guest_tier": "gold",
                "include_breakdown": True,
                "quote_validity_minutes": 30
            }
        }


class PriceCalculationResponse(BaseModel):
    """
    Response schema for price calculation.
    
    Contains the calculated price, validity period, and decision reference
    for auditing and booking confirmation.
    """
    # Decision reference (for audit trail)
    decision_reference: str = Field(..., description="Unique reference for this price decision")
    decision_version: int = Field(..., description="Version of this price decision")
    
    # Pricing
    base_price: Decimal = Field(..., description="Base price")
    tax_amount: Decimal = Field(..., description="Tax amount")
    discount_amount: Decimal = Field(default=Decimal("0"), description="Discount amount")
    total_price: Decimal = Field(..., description="Total price to charge")
    currency: str = Field(default="USD", description="Currency code")
    
    # Breakdown (if requested)
    breakdown: Optional[PriceBreakdown] = Field(None, description="Detailed price breakdown")
    
    # Validity
    valid_from: datetime = Field(..., description="Quote valid from")
    valid_until: datetime = Field(..., description="Quote valid until")
    
    # Source info (for transparency)
    pricing_source: str = Field(..., description="How price was calculated (ai_model, rule_engine, fallback)")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    
    # Context
    venue_id: UUID
    venue_type: str
    booking_time: datetime
    party_size: int
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "decision_reference": "PRC-2024-001234",
                "decision_version": 1,
                "base_price": "100.00",
                "tax_amount": "14.14",
                "discount_amount": "5.00",
                "total_price": "141.35",
                "currency": "USD",
                "valid_from": "2024-12-18T10:00:00Z",
                "valid_until": "2024-12-18T10:30:00Z",
                "pricing_source": "ai_model",
                "confidence": 0.92,
                "venue_id": "223e4567-e89b-12d3-a456-426614174000",
                "venue_type": "restaurant",
                "booking_time": "2024-12-25T19:00:00Z",
                "party_size": 4
            }
        }


class PriceEstimateRequest(BaseModel):
    """
    Request schema for price estimation.
    
    Used for availability checks - returns estimated price without
    creating a committed price decision.
    """
    venue_id: UUID = Field(..., description="Venue ID")
    venue_type: str = Field(..., description="Type of venue")
    booking_time: datetime = Field(..., description="Booking date and time")
    party_size: int = Field(..., ge=1, description="Number of guests")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duration in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "venue_id": "223e4567-e89b-12d3-a456-426614174000",
                "venue_type": "restaurant",
                "booking_time": "2024-12-25T19:00:00Z",
                "party_size": 4,
                "duration_minutes": 120
            }
        }


class PriceEstimateResponse(BaseModel):
    """Response schema for price estimation."""
    estimated_price: Decimal = Field(..., description="Estimated price")
    currency: str = Field(default="USD", description="Currency code")
    
    # Range (price may vary)
    price_range: Optional[Dict[str, Decimal]] = Field(
        None,
        description="Price range (min/max)"
    )
    
    # Factors affecting price
    demand_level: Optional[str] = Field(None, description="Current demand level")
    is_peak_time: bool = Field(default=False, description="Is this a peak time?")
    
    # Note: Estimates are not binding
    is_estimate: bool = Field(default=True)
    note: str = Field(
        default="This is an estimate. Final price will be calculated at booking time.",
        description="Disclaimer note"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "estimated_price": "135.00",
                "currency": "USD",
                "price_range": {"min": "120.00", "max": "150.00"},
                "demand_level": "high",
                "is_peak_time": True,
                "is_estimate": True,
                "note": "This is an estimate. Final price will be calculated at booking time."
            }
        }


class BulkPriceRequest(BaseModel):
    """Request for calculating prices for multiple time slots."""
    venue_id: UUID = Field(..., description="Venue ID")
    venue_type: str = Field(..., description="Type of venue")
    party_size: int = Field(..., ge=1, description="Number of guests")
    
    # Multiple time slots
    time_slots: List[datetime] = Field(..., min_length=1, max_length=50, description="List of time slots")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duration for each slot")
    
    guest_id: Optional[UUID] = Field(None, description="Guest ID for loyalty pricing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "venue_id": "223e4567-e89b-12d3-a456-426614174000",
                "venue_type": "restaurant",
                "party_size": 4,
                "time_slots": [
                    "2024-12-25T18:00:00Z",
                    "2024-12-25T19:00:00Z",
                    "2024-12-25T20:00:00Z"
                ],
                "duration_minutes": 120
            }
        }


class BulkPriceResponse(BaseModel):
    """Response for bulk price calculation."""
    prices: List[Dict[str, Any]] = Field(..., description="Price for each time slot")
    currency: str = Field(default="USD", description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prices": [
                    {"time_slot": "2024-12-25T18:00:00Z", "estimated_price": "120.00", "demand_level": "normal"},
                    {"time_slot": "2024-12-25T19:00:00Z", "estimated_price": "145.00", "demand_level": "high"},
                    {"time_slot": "2024-12-25T20:00:00Z", "estimated_price": "135.00", "demand_level": "high"}
                ],
                "currency": "USD"
            }
        }


