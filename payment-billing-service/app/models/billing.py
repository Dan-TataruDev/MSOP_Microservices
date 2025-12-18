"""
Billing record database models.
"""
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, Text, Enum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class BillingRecord(Base):
    """
    Billing record representing a financial transaction record.
    
    Links payments to bookings and provides audit trail for financial operations.
    """
    __tablename__ = "billing_records"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Related entities
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to booking
    booking_reference = Column(String(50), nullable=True, index=True)
    guest_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Billing details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    billing_type = Column(String(50), nullable=False)  # payment, refund, adjustment, fee
    
    # Breakdown
    base_amount = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    fee_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Extra data
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    billed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    payment = relationship("Payment", back_populates="billing_records")
    
    # Indexes
    __table_args__ = (
        Index("idx_billing_booking", "booking_id", "billed_at"),
        Index("idx_billing_guest", "guest_id", "billed_at"),
        Index("idx_billing_type", "billing_type", "billed_at"),
    )
