"""
Invoice Pydantic schemas.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from app.models.invoice import InvoiceStatus


class InvoiceLineItem(BaseModel):
    """Schema for invoice line item."""
    description: str
    quantity: float = Field(default=1, gt=0)
    unit_price: float = Field(..., gt=0)
    amount: float = Field(..., gt=0)


class InvoiceCreate(BaseModel):
    """Schema for creating an invoice."""
    booking_id: UUID
    booking_reference: Optional[str] = None
    payment_id: Optional[UUID] = None
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    base_amount: float
    tax_amount: float = Field(default=0, ge=0)
    fee_amount: float = Field(default=0, ge=0)
    discount_amount: float = Field(default=0, ge=0)
    billing_name: str
    billing_email: EmailStr
    billing_address: Optional[str] = None
    description: Optional[str] = None
    line_items: Optional[List[InvoiceLineItem]] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    due_days: int = Field(default=30, ge=1, le=365)


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""
    id: UUID
    invoice_number: str
    booking_id: UUID
    booking_reference: Optional[str]
    payment_id: Optional[UUID]
    amount: float
    currency: str
    status: InvoiceStatus
    base_amount: float
    tax_amount: float
    fee_amount: float
    discount_amount: float
    invoice_date: date
    due_date: date
    paid_date: Optional[datetime]
    billing_name: str
    billing_email: str
    description: Optional[str]
    line_items: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice."""
    status: Optional[InvoiceStatus] = None
    paid_date: Optional[datetime] = None


