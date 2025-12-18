"""
Payment database models.
"""
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, Text, Enum, Index, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum
from app.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status lifecycle states."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, enum.Enum):
    """Payment methods supported."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CASH = "cash"


class Payment(Base):
    """
    Main payment entity representing a payment transaction.
    
    This model owns the payment lifecycle and is the source of truth
    for payment state. It abstracts payment provider details and only
    exposes safe, sanitized data to the frontend.
    """
    __tablename__ = "payments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Payment identification
    payment_reference = Column(String(50), unique=True, nullable=False, index=True)
    idempotency_key = Column(String(255), nullable=True, index=True)  # For idempotent operations
    
    # Related entities (references, not foreign keys - service isolation)
    booking_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to booking
    booking_reference = Column(String(50), nullable=True, index=True)
    guest_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)
    version = Column(Integer, nullable=False, default=1)  # Optimistic locking
    
    # Payment provider abstraction
    provider = Column(String(50), nullable=False)  # stripe, paypal, square, etc.
    provider_payment_id = Column(String(255), nullable=True, index=True)  # Provider's payment ID
    provider_response = Column(JSON, nullable=True)  # Raw provider response (encrypted in production)
    
    # Sensitive data (encrypted in production)
    # Never expose these fields to frontend
    card_last4 = Column(String(4), nullable=True)  # Last 4 digits only
    card_brand = Column(String(50), nullable=True)  # visa, mastercard, etc.
    payment_intent_id = Column(String(255), nullable=True)  # For 3D Secure flows
    
    # Payment extra data
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional data (venue_id, etc.)
    
    # Failure handling
    failure_reason = Column(Text, nullable=True)
    failure_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Webhook tracking
    webhook_received_at = Column(DateTime(timezone=True), nullable=True)
    webhook_processed = Column(Boolean, default=False)
    
    # Relationships
    refunds = relationship("Refund", back_populates="payment", cascade="all, delete-orphan")
    billing_records = relationship("BillingRecord", back_populates="payment", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_payment_booking", "booking_id", "status"),
        Index("idx_payment_guest", "guest_id", "status"),
        Index("idx_payment_provider", "provider", "provider_payment_id"),
        Index("idx_payment_status_created", "status", "created_at"),
    )
