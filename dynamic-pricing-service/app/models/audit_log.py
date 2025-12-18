"""
Audit Log model for comprehensive price decision auditing.

All pricing-related actions are logged for:
- Regulatory compliance
- Business analytics
- Dispute resolution
- System debugging
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Enum, Text, JSON, Index
)
import uuid

from app.database import Base, GUID


class AuditAction(str, enum.Enum):
    """Types of auditable actions."""
    # Price calculations
    PRICE_CALCULATED = "price_calculated"
    PRICE_SERVED = "price_served"
    PRICE_ACCEPTED = "price_accepted"
    PRICE_REJECTED = "price_rejected"
    PRICE_EXPIRED = "price_expired"
    
    # Rule management
    RULE_CREATED = "rule_created"
    RULE_UPDATED = "rule_updated"
    RULE_ACTIVATED = "rule_activated"
    RULE_DEACTIVATED = "rule_deactivated"
    RULE_DELETED = "rule_deleted"
    
    # Base price management
    BASE_PRICE_CREATED = "base_price_created"
    BASE_PRICE_UPDATED = "base_price_updated"
    BASE_PRICE_DELETED = "base_price_deleted"
    
    # System events
    AI_MODEL_CALLED = "ai_model_called"
    AI_MODEL_FAILED = "ai_model_failed"
    FALLBACK_TRIGGERED = "fallback_triggered"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    
    # Administrative
    MANUAL_OVERRIDE = "manual_override"
    BULK_UPDATE = "bulk_update"
    CONFIG_CHANGED = "config_changed"


class PriceAuditLog(Base):
    """
    Price Audit Log entity.
    
    Immutable log of all pricing-related actions.
    """
    __tablename__ = "price_audit_logs"
    
    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    action_description = Column(Text, nullable=True)
    
    # Entity reference
    entity_type = Column(String(50), nullable=False)  # price_decision, pricing_rule, base_price
    entity_id = Column(GUID, nullable=True, index=True)
    entity_reference = Column(String(100), nullable=True)
    
    # Actor
    actor_type = Column(String(50), nullable=False)  # system, user, service
    actor_id = Column(String(100), nullable=True)
    actor_name = Column(String(255), nullable=True)
    
    # Context
    venue_id = Column(GUID, nullable=True, index=True)
    venue_type = Column(String(50), nullable=True)
    booking_id = Column(GUID, nullable=True, index=True)
    guest_id = Column(GUID, nullable=True)
    
    # Change tracking
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    changes = Column(JSON, nullable=True)  # Diff of changes
    
    # Request context
    request_id = Column(String(100), nullable=True)  # Correlation ID
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional data
    extra_data = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_audit_action_created", "action", "created_at"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_venue_created", "venue_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<PriceAuditLog {self.action}: {self.entity_type}/{self.entity_id}>"
