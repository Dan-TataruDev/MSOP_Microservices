"""
Offer database models.

Offers are personalized instances of campaigns for specific guests.
This is where eligibility decisions are recorded.
"""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class OfferStatus(str, enum.Enum):
    """Offer lifecycle status."""
    PENDING = "pending"      # Generated, not yet shown
    PRESENTED = "presented"  # Shown to guest
    CLAIMED = "claimed"      # Guest accepted/claimed
    REDEEMED = "redeemed"    # Applied to a booking/transaction
    EXPIRED = "expired"      # Past validity
    DECLINED = "declined"    # Guest declined


class OfferType(str, enum.Enum):
    """Types of personalized offers."""
    DISCOUNT = "discount"
    UPGRADE = "upgrade"
    BONUS_POINTS = "bonus_points"
    COMPLIMENTARY = "complimentary"
    BUNDLE = "bundle"


class Offer(Base):
    """
    Personalized offer for a specific guest.
    
    Offers are generated based on:
    - Active campaigns they're eligible for
    - Insights from personalization/sentiment services
    - Loyalty tier and history
    
    The offer references what action to take but does NOT
    calculate pricing - that's the pricing service's job.
    """
    __tablename__ = "offers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    offer_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Who this offer is for
    guest_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Source campaign (if campaign-based)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True, index=True)
    
    # Offer details
    offer_type = Column(Enum(OfferType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # What to apply (reference, not calculation)
    # e.g., "SUMMER20" discount code, "500" bonus points, "DELUXE" upgrade type
    offer_value = Column(String(100), nullable=False)
    
    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    
    # Status tracking
    status = Column(Enum(OfferStatus), default=OfferStatus.PENDING, index=True)
    
    # When actions occurred
    presented_at = Column(DateTime(timezone=True), nullable=True)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    redeemed_at = Column(DateTime(timezone=True), nullable=True)
    
    # If redeemed, link to what it was applied to
    redeemed_booking_id = Column(UUID(as_uuid=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


