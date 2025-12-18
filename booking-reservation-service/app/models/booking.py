"""
Database models for bookings and reservations.
"""
from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, Text, Enum, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum
from app.database import Base


class VenueType(str, enum.Enum):
    """Types of venues that can be booked."""
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    RETAIL = "retail"


class BookingStatus(str, enum.Enum):
    """Booking status lifecycle states."""
    PENDING = "pending"  # Created but not confirmed
    CONFIRMED = "confirmed"  # Confirmed and active
    CHECKED_IN = "checked_in"  # Guest has checked in
    COMPLETED = "completed"  # Booking completed successfully
    CANCELLED = "cancelled"  # Cancelled by guest or business
    NO_SHOW = "no_show"  # Guest didn't show up
    EXPIRED = "expired"  # Booking expired without confirmation


class Booking(Base):
    """
    Main booking entity representing a reservation or booking.
    
    This model owns the entire lifecycle of a booking and is the source of truth
    for booking state. It coordinates with external services (inventory, pricing, payment)
    but does not embed their logic.
    """
    __tablename__ = "bookings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Booking identification
    booking_reference = Column(String(50), unique=True, nullable=False, index=True)
    idempotency_key = Column(String(255), nullable=True, index=True)  # For idempotent operations
    
    # Guest information
    guest_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    guest_name = Column(String(255), nullable=False)
    guest_email = Column(String(255), nullable=False)
    guest_phone = Column(String(50), nullable=True)
    
    # Venue information
    venue_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    venue_type = Column(Enum(VenueType), nullable=False, index=True)
    venue_name = Column(String(255), nullable=False)
    
    # Booking details
    booking_date = Column(DateTime(timezone=True), nullable=False, index=True)
    booking_time = Column(DateTime(timezone=True), nullable=False)  # Start time
    duration_minutes = Column(Integer, nullable=True)  # Duration in minutes (for restaurants, cafes)
    end_time = Column(DateTime(timezone=True), nullable=True)  # Calculated end time
    party_size = Column(Integer, nullable=False)  # Number of guests
    
    # Status and lifecycle
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING, index=True)
    version = Column(Integer, nullable=False, default=1)  # Optimistic locking version
    
    # Pricing (snapshot at booking time, actual pricing from pricing service)
    base_price = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    
    # Payment coordination
    payment_intent_id = Column(String(255), nullable=True)  # Reference to payment service
    payment_status = Column(String(50), nullable=True)  # pending, completed, failed, refunded
    payment_method_id = Column(String(255), nullable=True)
    
    # Inventory coordination
    inventory_item_id = Column(String(255), nullable=True)  # Reference to inventory service
    inventory_reservation_id = Column(String(255), nullable=True)  # Reservation ID from inventory service
    
    # Special requests and notes
    special_requests = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)  # Business-only notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For pending bookings
    
    # Cancellation details
    cancellation_reason = Column(String(255), nullable=True)
    cancelled_by = Column(String(50), nullable=True)  # guest, business, system
    
    # Extra data
    source = Column(String(50), nullable=True)  # web, mobile, phone, walk_in
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    # Relationships
    status_history = relationship("BookingStatusHistory", back_populates="booking", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_booking_guest_date", "guest_id", "booking_date"),
        Index("idx_booking_venue_date", "venue_id", "booking_date"),
        Index("idx_booking_status_date", "status", "booking_date"),
        Index("idx_booking_reference", "booking_reference"),
    )
    
    def __repr__(self):
        return f"<Booking(id={self.id}, reference={self.booking_reference}, status={self.status})>"


class BookingStatusHistory(Base):
    """
    Audit trail of booking status changes.
    Ensures traceability of all status transitions.
    """
    __tablename__ = "booking_status_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    from_status = Column(Enum(BookingStatus), nullable=True)
    to_status = Column(Enum(BookingStatus), nullable=False)
    
    changed_by = Column(String(50), nullable=True)  # guest_id, business_id, system
    reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    booking = relationship("Booking", back_populates="status_history")
    
    __table_args__ = (
        Index("idx_status_history_booking", "booking_id", "created_at"),
    )


class IdempotencyKey(Base):
    """
    Stores idempotency keys to prevent duplicate operations.
    Ensures idempotency for booking creation and updates.
    """
    __tablename__ = "idempotency_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, nullable=False, index=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    
    operation_type = Column(String(50), nullable=False)  # create, update, cancel
    request_hash = Column(String(255), nullable=True)  # Hash of request payload
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        Index("idx_idempotency_key", "key"),
        Index("idx_idempotency_expires", "expires_at"),
    )
