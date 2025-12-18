"""
Loyalty program database models.

Tracks loyalty programs, member tiers, and points balances.
"""
from sqlalchemy import Column, String, DateTime, Integer, Enum, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class LoyaltyTier(str, enum.Enum):
    """Loyalty program tiers."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class LoyaltyProgram(Base):
    """Loyalty program configuration."""
    __tablename__ = "loyalty_programs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Points earning rates (points per currency unit spent)
    base_earn_rate = Column(Float, default=1.0)
    
    # Tier thresholds (points required)
    silver_threshold = Column(Integer, default=1000)
    gold_threshold = Column(Integer, default=5000)
    platinum_threshold = Column(Integer, default=15000)
    
    # Tier multipliers
    silver_multiplier = Column(Float, default=1.25)
    gold_multiplier = Column(Float, default=1.5)
    platinum_multiplier = Column(Float, default=2.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    members = relationship("LoyaltyMember", back_populates="program")


class LoyaltyMember(Base):
    """
    Loyalty program membership for a guest.
    
    Note: Points transactions reference external entities (bookings, campaigns)
    but don't embed their rules.
    """
    __tablename__ = "loyalty_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guest_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("loyalty_programs.id"), nullable=False)
    
    # Current status
    tier = Column(Enum(LoyaltyTier), default=LoyaltyTier.BRONZE)
    points_balance = Column(Integer, default=0)
    lifetime_points = Column(Integer, default=0)
    
    # Timestamps
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    tier_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    program = relationship("LoyaltyProgram", back_populates="members")


class PointsTransaction(Base):
    """Record of points earned or redeemed."""
    __tablename__ = "points_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("loyalty_members.id"), nullable=False, index=True)
    
    # Transaction details
    points = Column(Integer, nullable=False)  # Positive = earned, Negative = redeemed
    description = Column(String(255), nullable=False)
    
    # Reference to source (booking, campaign, manual adjustment)
    source_type = Column(String(50), nullable=False)  # "booking", "campaign", "manual"
    source_id = Column(UUID(as_uuid=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


