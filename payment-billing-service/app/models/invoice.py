"""
Invoice database models.
"""
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, Text, Enum, Index, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status lifecycle states."""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    """
    Invoice entity representing a billing document.
    
    Provides structured billing information for guests and businesses.
    """
    __tablename__ = "invoices"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Invoice identification
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Related entities
    booking_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to booking
    booking_reference = Column(String(50), nullable=True, index=True)
    payment_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Reference to payment
    guest_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Invoice details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT, index=True)
    
    # Breakdown
    base_amount = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    fee_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Dates
    invoice_date = Column(Date, nullable=False, server_default=func.current_date())
    due_date = Column(Date, nullable=False)
    paid_date = Column(DateTime(timezone=True), nullable=True)
    
    # Billing information
    billing_name = Column(String(255), nullable=False)
    billing_email = Column(String(255), nullable=False)
    billing_address = Column(Text, nullable=True)
    
    # Invoice content
    description = Column(Text, nullable=True)
    line_items = Column(JSON, nullable=True)  # Array of line items
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    
    # Extra data
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_invoice_booking", "booking_id", "status"),
        Index("idx_invoice_guest", "guest_id", "status"),
        Index("idx_invoice_status_date", "status", "due_date"),
    )
