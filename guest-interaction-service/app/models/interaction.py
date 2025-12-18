"""
Interaction history database models.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class InteractionType(Base):
    """
    Defines types of interactions (view, search, booking, order, etc.).
    """
    __tablename__ = "interaction_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)  # view, search, booking, order, feedback, marketing
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Interaction(Base):
    """
    Guest interaction history model.
    Tracks all guest interactions across the platform.
    """
    __tablename__ = "interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type_id = Column(UUID(as_uuid=True), ForeignKey("interaction_types.id"), nullable=False, index=True)
    
    # Interaction data
    entity_type = Column(String(100), nullable=True, index=True)  # venue, product, booking, order, etc.
    entity_id = Column(String(255), nullable=True, index=True)  # ID of the interacted entity
    
    # Context and metadata
    context = Column(JSONB, nullable=True)  # Additional context (search query, filters, etc.)
    interaction_metadata = Column(JSONB, nullable=True)  # Device info, session info, etc.
    
    # Source information
    source = Column(String(50), nullable=False, default="frontend")  # frontend, booking_service, order_service, etc.
    source_event_id = Column(String(255), nullable=True)  # ID of the event that triggered this interaction
    
    # Timestamp
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    guest = relationship("Guest", back_populates="interactions")
    interaction_type = relationship("InteractionType")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_interaction_guest_type", "guest_id", "interaction_type_id", "occurred_at"),
        Index("idx_interaction_entity", "entity_type", "entity_id"),
        Index("idx_interaction_occurred", "occurred_at"),
    )
