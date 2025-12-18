"""
Personalization data database models.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class GuestSegment(Base):
    """
    Guest segmentation model.
    Represents segments a guest belongs to (e.g., "frequent_traveler", "budget_conscious").
    """
    __tablename__ = "guest_segments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Segment information
    segment_name = Column(String(255), nullable=False, index=True)
    segment_category = Column(String(100), nullable=True, index=True)  # behavioral, demographic, preference_based
    confidence = Column(Float, default=1.0)  # 0.0-1.0, confidence in segment assignment
    
    # Metadata
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by = Column(String(100), nullable=False, default="system")  # system, ai_service, manual
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    guest = relationship("Guest", back_populates="segments")
    
    # Indexes
    __table_args__ = (
        Index("idx_segment_guest_active", "guest_id", "is_active"),
        Index("idx_segment_name", "segment_name", "is_active"),
    )


class BehaviorSignal(Base):
    """
    Behavior signals extracted from interactions.
    Provides structured inputs for AI personalization services.
    """
    __tablename__ = "behavior_signals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Signal information
    signal_type = Column(String(100), nullable=False, index=True)  # preference_indicator, trend, pattern, etc.
    signal_name = Column(String(255), nullable=False, index=True)  # e.g., "prefers_italian_cuisine", "books_weekends"
    signal_value = Column(JSONB, nullable=False)  # Signal data
    strength = Column(Float, default=1.0)  # 0.0-1.0, signal strength
    
    # Metadata
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    computed_by = Column(String(100), nullable=False, default="system")
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    guest = relationship("Guest", back_populates="behavior_signals")
    
    # Indexes
    __table_args__ = (
        Index("idx_signal_guest_type", "guest_id", "signal_type", "is_active"),
        Index("idx_signal_name", "signal_name", "is_active"),
    )


class PersonalizationContext(Base):
    """
    Aggregated personalization context for a guest.
    Provides structured inputs to AI-driven personalization services.
    """
    __tablename__ = "personalization_contexts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Context data
    preference_vector = Column(JSONB, nullable=True)  # Structured preference data
    behavior_summary = Column(JSONB, nullable=True)  # Aggregated behavior patterns
    segments = Column(JSONB, nullable=True)  # Active segments
    signals = Column(JSONB, nullable=True)  # Active behavior signals
    
    # Metadata
    version = Column(Integer, default=1, nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    computed_by = Column(String(100), nullable=False, default="system")
    
    # Relationships
    guest = relationship("Guest")
    
    # Indexes
    __table_args__ = (
        Index("idx_context_guest", "guest_id"),
    )
