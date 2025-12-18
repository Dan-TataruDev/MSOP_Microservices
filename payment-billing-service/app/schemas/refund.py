"""
Refund Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.refund import RefundStatus


class RefundCreate(BaseModel):
    """Schema for creating a refund."""
    payment_id: UUID
    booking_id: UUID
    booking_reference: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0, description="Refund amount (None for full refund)")
    reason: Optional[str] = None
    refund_type: str = Field(default="full", pattern="^(full|partial|cancellation|dispute)$")
    metadata: Optional[Dict[str, Any]] = None
    idempotency_key: Optional[str] = None


class RefundResponse(BaseModel):
    """Schema for refund response (sanitized)."""
    id: UUID
    refund_reference: str
    payment_id: UUID
    booking_id: UUID
    booking_reference: Optional[str]
    amount: float
    currency: str
    status: RefundStatus
    reason: Optional[str]
    refund_type: str
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RefundUpdate(BaseModel):
    """Schema for updating refund (internal use)."""
    status: Optional[RefundStatus] = None
    provider_refund_id: Optional[str] = None
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None


