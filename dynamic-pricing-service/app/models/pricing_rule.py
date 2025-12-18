"""
Pricing Rule model for defining dynamic pricing logic.

Rules can be:
- Seasonal (Christmas, Summer, etc.)
- Time-based (Peak hours, weekends)
- Demand-based (High occupancy surges)
- Event-based (Special events, holidays)
- Customer-based (Loyalty tiers, repeat guests)
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Enum, Boolean, 
    Integer, Numeric, JSON, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
import uuid

from app.database import Base, GUID


class RuleType(str, enum.Enum):
    """Types of pricing rules."""
    SEASONAL = "seasonal"           # Season-based pricing
    TIME_BASED = "time_based"       # Hour/day of week based
    DEMAND = "demand"               # Occupancy/demand based
    EVENT = "event"                 # Special events
    CUSTOMER_TIER = "customer_tier" # Loyalty tier discounts
    EARLY_BIRD = "early_bird"       # Advance booking discounts
    LAST_MINUTE = "last_minute"     # Last-minute deals
    PACKAGE = "package"             # Bundle pricing
    PROMOTIONAL = "promotional"     # Time-limited promotions
    DYNAMIC_AI = "dynamic_ai"       # AI-driven dynamic adjustment


class RuleStatus(str, enum.Enum):
    """Status of a pricing rule."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class RuleCondition(str, enum.Enum):
    """Condition operators for rule matching."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"


class RuleAction(str, enum.Enum):
    """Actions to apply when rule matches."""
    MULTIPLY = "multiply"           # Multiply base price
    ADD = "add"                     # Add fixed amount
    SUBTRACT = "subtract"           # Subtract fixed amount
    SET = "set"                     # Set to fixed price
    PERCENTAGE_INCREASE = "percentage_increase"
    PERCENTAGE_DECREASE = "percentage_decrease"


class PricingRule(Base):
    """
    Pricing Rule entity.
    
    Defines conditions and actions for dynamic price adjustments.
    Rules are evaluated in priority order.
    """
    __tablename__ = "pricing_rules"
    
    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # Rule identification
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule type and status
    rule_type = Column(Enum(RuleType), nullable=False, index=True)
    status = Column(Enum(RuleStatus), default=RuleStatus.DRAFT, nullable=False, index=True)
    
    # Priority (lower number = higher priority)
    priority = Column(Integer, default=100, nullable=False, index=True)
    
    # Applicability
    venue_types = Column(JSON, nullable=True)  # List of venue types this applies to
    venue_ids = Column(JSON, nullable=True)    # Specific venue IDs (null = all)
    
    # Conditions (JSON structure)
    # Example: {"field": "booking_date", "operator": "between", "values": ["2024-12-20", "2024-12-31"]}
    conditions = Column(JSON, nullable=False, default=list)
    
    # Action configuration
    action_type = Column(Enum(RuleAction), nullable=False)
    action_value = Column(Numeric(10, 4), nullable=False)  # Multiplier, amount, or percentage
    
    # Price boundaries for this rule
    min_price = Column(Numeric(12, 2), nullable=True)  # Floor price
    max_price = Column(Numeric(12, 2), nullable=True)  # Ceiling price
    
    # Stacking behavior
    is_stackable = Column(Boolean, default=True)  # Can combine with other rules
    exclusive_group = Column(String(50), nullable=True)  # Only one rule per group applies
    
    # Validity period
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    
    # Day/time restrictions (JSON)
    # Example: {"days": [0, 1, 2, 3, 4], "hours": {"start": 9, "end": 17}}
    time_restrictions = Column(JSON, nullable=True)
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    
    # Metadata
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_pricing_rules_status_priority", "status", "priority"),
        Index("ix_pricing_rules_type_status", "rule_type", "status"),
        Index("ix_pricing_rules_validity", "valid_from", "valid_until"),
    )
    
    def is_active(self) -> bool:
        """Check if rule is currently active and within validity period."""
        if self.status != RuleStatus.ACTIVE:
            return False
        
        now = datetime.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        
        return True
    
    def __repr__(self):
        return f"<PricingRule {self.rule_code}: {self.name}>"


