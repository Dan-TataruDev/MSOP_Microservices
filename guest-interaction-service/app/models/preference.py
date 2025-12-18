"""
Preference database models.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class PreferenceCategory(Base):
    """
    Defines categories of preferences (dietary, notification, etc.).
    """
    __tablename__ = "preference_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)  # dietary, notification, category, etc.
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System-defined vs user-defined
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Preference(Base):
    """
    Guest preference model.
    Stores explicit and implicit preferences with versioning support.
    """
    __tablename__ = "preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("preference_categories.id"), nullable=False, index=True)
    
    # Preference data
    key = Column(String(255), nullable=False, index=True)  # e.g., "dietary_restrictions", "favorite_cuisine"
    value = Column(JSONB, nullable=False)  # Flexible JSON value
    value_type = Column(String(50), nullable=False)  # string, array, boolean, number, object
    
    # Preference metadata
    source = Column(String(50), nullable=False, default="explicit")  # explicit, implicit, inferred, system
    confidence = Column(Integer, default=100)  # 0-100, confidence in preference accuracy
    is_active = Column(Boolean, default=True, index=True)
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    guest = relationship("Guest", back_populates="preferences")
    category = relationship("PreferenceCategory")
    history = relationship("PreferenceHistory", back_populates="preference", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_preference_guest_key", "guest_id", "key", "is_active"),
        Index("idx_preference_category", "category_id"),
    )


class PreferenceHistory(Base):
    """
    Historical record of preference changes.
    Supports GDPR compliance and audit trails.
    """
    __tablename__ = "preference_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    preference_id = Column(UUID(as_uuid=True), ForeignKey("preferences.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Historical data
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=False)
    change_reason = Column(String(255), nullable=True)  # user_update, system_inference, merge, etc.
    
    # Metadata
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    changed_by = Column(String(255), nullable=True)  # user_id, system, etc.
    
    # Relationships
    preference = relationship("Preference", back_populates="history")
    
    # Indexes
    __table_args__ = (
        Index("idx_pref_history_pref", "preference_id", "changed_at"),
    )
