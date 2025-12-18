"""
Pydantic schemas for price decision queries and audit.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.models.price_decision import DecisionSource, DecisionStatus


class PriceDecisionResponse(BaseModel):
    """Response schema for a price decision (audit record)."""
    id: UUID
    decision_reference: str
    version: int
    
    # Context
    venue_id: UUID
    venue_type: str
    venue_name: Optional[str]
    
    booking_date: datetime
    booking_time: datetime
    duration_minutes: Optional[int]
    party_size: int
    
    guest_id: Optional[UUID]
    guest_tier: Optional[str]
    
    # Pricing
    base_price: Decimal
    demand_adjustment: Decimal
    seasonal_adjustment: Decimal
    time_adjustment: Decimal
    loyalty_adjustment: Decimal
    promotional_adjustment: Decimal
    ai_adjustment: Decimal
    
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_price: Decimal
    currency: str
    
    # Decision metadata
    source: DecisionSource
    status: DecisionStatus
    ai_confidence: Optional[Decimal]
    model_version: Optional[str]
    
    applied_rules: Optional[List[Dict[str, Any]]]
    price_breakdown: Optional[Dict[str, Any]]
    
    # Validity
    valid_from: datetime
    valid_until: datetime
    
    # Timing
    calculation_time_ms: Optional[int]
    created_at: datetime
    served_at: Optional[datetime]
    accepted_at: Optional[datetime]
    
    # Linked booking
    booking_id: Optional[UUID]
    booking_reference: Optional[str]
    
    class Config:
        from_attributes = True
        # Disable protected namespace warning for model_version field
        protected_namespaces = ()


class PriceDecisionListResponse(BaseModel):
    """Response schema for paginated decision list."""
    decisions: List[PriceDecisionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DecisionAuditResponse(BaseModel):
    """Response schema for decision audit trail."""
    decision: PriceDecisionResponse
    
    # Version history
    version_history: List[Dict[str, Any]] = Field(
        default=[],
        description="Previous versions of this decision"
    )
    
    # Audit events
    audit_events: List[Dict[str, Any]] = Field(
        default=[],
        description="Audit log entries for this decision"
    )
    
    # Related decisions (same booking context)
    related_decisions: List[Dict[str, Any]] = Field(
        default=[],
        description="Other decisions for the same booking context"
    )


class DecisionStatusUpdate(BaseModel):
    """Schema for updating decision status."""
    status: DecisionStatus = Field(..., description="New status")
    booking_id: Optional[UUID] = Field(None, description="Linked booking ID")
    booking_reference: Optional[str] = Field(None, description="Linked booking reference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "accepted",
                "booking_id": "123e4567-e89b-12d3-a456-426614174000",
                "booking_reference": "BK-2024-001234"
            }
        }


class DecisionQueryParams(BaseModel):
    """Query parameters for searching decisions."""
    venue_id: Optional[UUID] = None
    venue_type: Optional[str] = None
    guest_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    
    source: Optional[DecisionSource] = None
    status: Optional[DecisionStatus] = None
    
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


