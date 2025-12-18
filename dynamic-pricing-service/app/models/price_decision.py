"""
Price Decision model for tracking and auditing all pricing calculations.

Every price calculation is recorded with full context for:
- Auditability and compliance
- Analytics and model improvement
- Debugging and troubleshooting
- Customer dispute resolution
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Enum, Boolean,
    Integer, Numeric, JSON, Text, ForeignKey, Index
)
import uuid

from app.database import Base, GUID


class DecisionSource(str, enum.Enum):
    """Source of the pricing decision."""
    AI_MODEL = "ai_model"           # AI/ML model calculated
    RULE_ENGINE = "rule_engine"     # Rule-based calculation
    FALLBACK_CACHED = "fallback_cached"  # Cached price used
    FALLBACK_BASE = "fallback_base"      # Base price fallback
    MANUAL_OVERRIDE = "manual_override"  # Admin override
    PROMOTIONAL = "promotional"          # Promotional pricing


class DecisionStatus(str, enum.Enum):
    """Status of the price decision."""
    CALCULATED = "calculated"   # Price was calculated
    SERVED = "served"           # Price was served to client
    ACCEPTED = "accepted"       # Customer accepted (booked)
    REJECTED = "rejected"       # Customer rejected
    EXPIRED = "expired"         # Price quote expired
    INVALIDATED = "invalidated" # Invalidated by admin


class PriceDecision(Base):
    """
    Price Decision entity.
    
    Immutable record of every pricing calculation.
    Each decision is versioned and linked to its predecessor for audit trails.
    """
    __tablename__ = "price_decisions"
    
    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # Decision reference (human-readable)
    decision_reference = Column(String(50), unique=True, nullable=False, index=True)
    
    # Version tracking
    version = Column(Integer, default=1, nullable=False)
    parent_decision_id = Column(GUID, ForeignKey("price_decisions.id"), nullable=True)
    
    # Request context
    venue_id = Column(GUID, nullable=False, index=True)
    venue_type = Column(String(50), nullable=False, index=True)
    venue_name = Column(String(255), nullable=True)
    
    # Booking context
    booking_date = Column(DateTime, nullable=False, index=True)
    booking_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    party_size = Column(Integer, nullable=False)
    
    # Guest context (for personalized pricing)
    guest_id = Column(GUID, nullable=True, index=True)
    guest_tier = Column(String(50), nullable=True)  # Loyalty tier
    
    # =========================================================================
    # Pricing Output
    # =========================================================================
    base_price = Column(Numeric(12, 2), nullable=False)
    
    # Adjustments breakdown
    demand_adjustment = Column(Numeric(12, 2), default=0)
    seasonal_adjustment = Column(Numeric(12, 2), default=0)
    time_adjustment = Column(Numeric(12, 2), default=0)
    loyalty_adjustment = Column(Numeric(12, 2), default=0)
    promotional_adjustment = Column(Numeric(12, 2), default=0)
    ai_adjustment = Column(Numeric(12, 2), default=0)
    
    # Final prices
    subtotal = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    total_price = Column(Numeric(12, 2), nullable=False)
    
    currency = Column(String(3), default="USD", nullable=False)
    
    # =========================================================================
    # Decision Metadata
    # =========================================================================
    source = Column(Enum(DecisionSource), nullable=False, index=True)
    status = Column(Enum(DecisionStatus), default=DecisionStatus.CALCULATED, nullable=False, index=True)
    
    # Confidence and quality metrics
    ai_confidence = Column(Numeric(5, 4), nullable=True)  # 0.0000 to 1.0000
    model_version = Column(String(50), nullable=True)
    
    # Rules that were applied
    applied_rules = Column(JSON, nullable=True)  # List of rule IDs and their effects
    
    # Demand and context data at decision time
    demand_data = Column(JSON, nullable=True)
    # Example: {"occupancy_rate": 0.85, "forecast": "high", "competing_events": [...]}
    
    # AI model input/output (for debugging and improvement)
    ai_input = Column(JSON, nullable=True)
    ai_output = Column(JSON, nullable=True)
    
    # Full breakdown for transparency
    price_breakdown = Column(JSON, nullable=True)
    # Example: {"base": 100, "peak_hours": +20, "high_demand": +15, "loyalty_discount": -10}
    
    # Validity
    valid_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=False)  # Price quote expiration
    
    # Processing metrics
    calculation_time_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    served_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    
    # Linked booking (if price was accepted)
    booking_id = Column(GUID, nullable=True, index=True)
    booking_reference = Column(String(50), nullable=True)
    
    # Request metadata
    request_id = Column(String(100), nullable=True)  # Correlation ID
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_price_decisions_venue_date", "venue_id", "booking_date"),
        Index("ix_price_decisions_source_status", "source", "status"),
        Index("ix_price_decisions_created", "created_at"),
    )
    
    def is_valid(self) -> bool:
        """Check if price decision is still valid."""
        now = datetime.utcnow()
        return (
            self.status in [DecisionStatus.CALCULATED, DecisionStatus.SERVED]
            and self.valid_until > now
        )
    
    def __repr__(self):
        return f"<PriceDecision {self.decision_reference}: {self.total_price} {self.currency}>"


