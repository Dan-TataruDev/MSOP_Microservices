"""
Billing Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class BillingRecordCreate(BaseModel):
    """Schema for creating a billing record."""
    payment_id: UUID
    booking_id: UUID
    booking_reference: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    billing_type: str
    base_amount: float
    tax_amount: float = Field(default=0, ge=0)
    fee_amount: float = Field(default=0, ge=0)
    discount_amount: float = Field(default=0, ge=0)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BillingRecordResponse(BaseModel):
    """Schema for billing record response."""
    id: UUID
    payment_id: UUID
    booking_id: UUID
    booking_reference: Optional[str]
    amount: float
    currency: str
    billing_type: str
    base_amount: float
    tax_amount: float
    fee_amount: float
    discount_amount: float
    description: Optional[str]
    created_at: datetime
    billed_at: datetime
    
    class Config:
        from_attributes = True


