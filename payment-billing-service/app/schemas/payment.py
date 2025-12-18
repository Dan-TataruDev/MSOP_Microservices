"""
Payment Pydantic schemas for API requests and responses.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.payment import PaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    """Schema for creating a payment."""
    booking_id: UUID
    booking_reference: Optional[str] = None
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="USD", max_length=3)
    payment_method: PaymentMethod
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    idempotency_key: Optional[str] = None


class PaymentResponse(BaseModel):
    """Schema for payment response (sanitized, no sensitive data)."""
    id: UUID
    payment_reference: str
    booking_id: UUID
    booking_reference: Optional[str]
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    card_last4: Optional[str] = None  # Only last 4 digits, safe to expose
    card_brand: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentStatusResponse(BaseModel):
    """Schema for payment status check (minimal, secure)."""
    payment_reference: str
    status: PaymentStatus
    amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    """Schema for updating payment (internal use)."""
    status: Optional[PaymentStatus] = None
    provider_payment_id: Optional[str] = None
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None


