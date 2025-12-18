"""
Collection model - represents a user-created collection of places.

Design decisions:
- UUID primary key for security (no sequential IDs)
- Separate public_id for shareable links (can be regenerated)
- Soft delete support for data recovery
- is_public flag controls visibility to non-owners
- Cover image stored as URL (actual image hosted elsewhere)
"""

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, DateTime, Boolean, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

if TYPE_CHECKING:
    from app.models.collection_item import CollectionItem


def generate_public_id() -> str:
    """
    Generate a URL-safe public identifier for sharing.
    
    Uses a shorter format than full UUID for cleaner URLs.
    Example: "abc123xy" instead of full UUID.
    """
    return uuid.uuid4().hex[:12]


class Collection(Base):
    """
    A user-created collection of places.
    
    Collections are like playlists for places - users can organize
    places into themed groups like "Date Night Spots" or "Business Lunch".
    
    Key features:
    - Private by default, can be made public for sharing
    - Has a separate public_id for shareable URLs
    - Supports cover image and description for rich display
    - Soft delete support for accidental deletion recovery
    """
    
    __tablename__ = "collections"
    
    # Primary key - UUID for security
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Internal unique identifier"
    )
    
    # Owner reference
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="User ID from the authentication service"
    )
    
    # Public sharing identifier - shorter than UUID for cleaner URLs
    # Can be regenerated if user wants to invalidate old share links
    public_id: Mapped[str] = mapped_column(
        String(12),
        unique=True,
        nullable=False,
        default=generate_public_id,
        comment="Public identifier for sharing (e.g., 'abc123xy')"
    )
    
    # Collection metadata
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Collection name (e.g., 'Summer Trip')"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional collection description"
    )
    
    cover_image_url: Mapped[Optional[str]] = mapped_column(
        String(2048),
        nullable=True,
        comment="URL to cover image (hosted externally)"
    )
    
    # Visibility settings
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the collection is publicly accessible via public_id"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Soft delete support
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Soft delete timestamp, null if active"
    )
    
    # Relationships
    items: Mapped[List["CollectionItem"]] = relationship(
        "CollectionItem",
        back_populates="collection",
        lazy="selectin",
        order_by="CollectionItem.position"
    )
    
    # Indexes
    __table_args__ = (
        # Index for listing user's collections
        Index("ix_collections_user_id_created_at", "user_id", "created_at"),
        # Index for public collection lookups
        Index("ix_collections_public_id_is_public", "public_id", "is_public"),
        # Index for filtering out soft-deleted records
        Index("ix_collections_deleted_at", "deleted_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, name={self.name}, user_id={self.user_id})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if this collection has been soft deleted."""
        return self.deleted_at is not None
    
    @property
    def item_count(self) -> int:
        """Get the number of non-deleted items in this collection."""
        return len([item for item in self.items if not item.is_deleted])


