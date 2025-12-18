"""
Guest profile database models.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Guest(Base):
    """
    Main guest profile model.
    Represents a guest identity in the system.
    """
    __tablename__ = "guests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)  # Nullable for anonymous guests
    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=True)  # For authenticated users
    
    # Profile metadata
    status = Column(String(50), default="active", index=True)  # active, inactive, deleted, anonymized
    is_anonymous = Column(Boolean, default=False, index=True)
    
    # Privacy and GDPR
    consent_marketing = Column(Boolean, default=False)
    consent_analytics = Column(Boolean, default=True)
    consent_personalization = Column(Boolean, default=True)
    data_retention_until = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    preferences = relationship("Preference", back_populates="guest", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="guest", cascade="all, delete-orphan")
    identity_mappings = relationship("GuestIdentityMapping", back_populates="guest", cascade="all, delete-orphan")
    segments = relationship("GuestSegment", back_populates="guest", cascade="all, delete-orphan")
    behavior_signals = relationship("BehaviorSignal", back_populates="guest", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_guest_status", "status"),
        Index("idx_guest_anonymous", "is_anonymous"),
        Index("idx_guest_email", "email"),
    )


class GuestIdentityMapping(Base):
    """
    Maps external identity sources to guest IDs.
    Supports anonymous-to-authenticated transitions and multi-device tracking.
    """
    __tablename__ = "guest_identity_mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Identity source information
    identity_type = Column(String(50), nullable=False, index=True)  # session_id, device_id, auth_user_id, email
    identity_value = Column(String(255), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_primary = Column(Boolean, default=False, index=True)
    
    # Relationships
    guest = relationship("Guest", back_populates="identity_mappings")
    
    # Unique constraint: one identity value per type
    __table_args__ = (
        Index("idx_identity_type_value", "identity_type", "identity_value", unique=True),
    )
