"""
Refund database models.
"""
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, Text, Enum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class RefundStatus(str, enum.Enum):
    """Refund status lifecycle states."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Refund(Base):
    """
    Refund entity representing a payment refund.
    
    Tracks refund requests and processing status.
    """
    __tablename__ = "refunds"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Refund identification
    refund_reference = Column(String(50), unique=True, nullable=False, index=True)
    idempotency_key = Column(String(255), nullable=True, index=True)
    
    # Related entities
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to booking
    booking_reference = Column(String(50), nullable=True, index=True)
    guest_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Refund details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(RefundStatus), nullable=False, default=RefundStatus.PENDING, index=True)
    version = Column(Integer, nullable=False, default=1)  # Optimistic locking
    
    # Refund reason
    reason = Column(Text, nullable=True)
    refund_type = Column(String(50), nullable=False)  # full, partial, cancellation, dispute
    
    # Payment provider abstraction
    provider = Column(String(50), nullable=False)  # stripe, paypal, square, etc.
    provider_refund_id = Column(String(255), nullable=True, index=True)  # Provider's refund ID
    provider_response = Column(JSON, nullable=True)  # Raw provider response (encrypted in production)
    
    # Failure handling
    failure_reason = Column(Text, nullable=True)
    failure_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Extra data
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="refunds")
    
    # Indexes
    __table_args__ = (
        Index("idx_refund_payment", "payment_id", "status"),
        Index("idx_refund_booking", "booking_id", "status"),
        Index("idx_refund_guest", "guest_id", "status"),
        Index("idx_refund_provider", "provider", "provider_refund_id"),
    )
