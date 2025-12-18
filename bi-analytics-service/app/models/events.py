"""
Models for storing ingested events.

Design:
- Raw event storage for audit and reprocessing
- Partitioned by time for efficient data lifecycle management
- Indexed for aggregation queries
"""
import enum
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Text, Enum, Index, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class EventSource(str, enum.Enum):
    """Source services for events."""
    BOOKING = "booking"
    PAYMENT = "payment"
    INVENTORY = "inventory"
    FEEDBACK = "feedback"
    LOYALTY = "loyalty"
    HOUSEKEEPING = "housekeeping"
    PRICING = "pricing"
    GUEST = "guest"


class IngestedEvent(Base):
    """
    Raw events ingested from other services.
    
    This table acts as a staging area for event data.
    Events are processed and aggregated into metrics.
    Old events are periodically archived/deleted based on retention policy.
    """
    __tablename__ = "ingested_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Event identification
    event_id = Column(String(100), nullable=False, index=True)  # Original event ID
    event_type = Column(String(100), nullable=False, index=True)  # e.g., "booking.created"
    source = Column(Enum(EventSource), nullable=False, index=True)
    
    # Event data
    payload = Column(JSON, nullable=False)  # Full event payload
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False, index=True)  # When event occurred
    ingested_at = Column(DateTime, default=datetime.utcnow)  # When we received it
    
    # Processing status
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)
    
    __table_args__ = (
        # Composite index for event deduplication
        Index('ix_event_dedup', 'event_id', 'source', unique=True),
        # Index for processing queue
        Index('ix_event_processing', 'processed', 'event_timestamp'),
        # Index for source-based queries
        Index('ix_event_source_type', 'source', 'event_type', 'event_timestamp'),
    )


class EventProcessingCheckpoint(Base):
    """
    Tracks processing progress for each event source.
    
    Used to resume processing after service restart
    and to track data freshness per source.
    """
    __tablename__ = "event_processing_checkpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source = Column(Enum(EventSource), nullable=False, unique=True)
    
    # Last processed event
    last_event_id = Column(String(100), nullable=True)
    last_event_timestamp = Column(DateTime, nullable=True)
    
    # Processing stats
    events_processed_total = Column(Integer, default=0)
    events_processed_today = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    # Health indicators
    last_successful_run = Column(DateTime, nullable=True)
    consecutive_errors = Column(Integer, default=0)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
