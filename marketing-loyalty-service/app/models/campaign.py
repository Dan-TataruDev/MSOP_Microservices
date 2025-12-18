"""
Campaign database models.

Campaigns define marketing initiatives with eligibility rules but do NOT
embed pricing or booking logic - those are delegated to respective services.
"""
from sqlalchemy import Column, String, DateTime, Text, Enum, Boolean, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class CampaignStatus(str, enum.Enum):
    """Campaign lifecycle status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class CampaignType(str, enum.Enum):
    """Types of marketing campaigns."""
    PROMOTION = "promotion"      # Discount-based campaigns
    LOYALTY_BONUS = "loyalty_bonus"  # Extra points campaigns
    SEASONAL = "seasonal"        # Holiday/seasonal campaigns
    RETENTION = "retention"      # Win-back campaigns
    ACQUISITION = "acquisition"  # New customer campaigns


class Campaign(Base):
    """
    Campaign entity defining marketing initiatives.
    
    Design principles:
    - Defines WHO is eligible (via eligibility_rules JSON)
    - Defines WHAT the campaign offers (via campaign_config JSON)
    - Does NOT contain pricing calculations (delegated to pricing service)
    - Does NOT contain booking rules (delegated to booking service)
    """
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    campaign_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Campaign definition
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, index=True)
    
    # Targeting: venue/property scope
    venue_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # null = all venues
    
    # Scheduling
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Eligibility rules (JSON for flexibility)
    # Example: {"min_loyalty_tier": "gold", "sentiment_score_min": 0.6, "segments": ["frequent_guest"]}
    eligibility_rules = Column(JSON, default=dict)
    
    # Campaign configuration (what action to trigger, NOT how to calculate it)
    # Example: {"discount_type": "percentage", "discount_code": "SUMMER20", "bonus_points": 500}
    campaign_config = Column(JSON, default=dict)
    
    # Limits
    max_redemptions = Column(Integer, nullable=True)  # null = unlimited
    current_redemptions = Column(Integer, default=0)
    max_per_guest = Column(Integer, default=1)
    
    # Metadata
    priority = Column(Integer, default=0)  # Higher = more priority
    is_stackable = Column(Boolean, default=False)  # Can combine with other campaigns
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)


