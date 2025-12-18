"""
CollectionItem model - represents a place within a collection.

Design decisions:
- Separate table allows a place to be in multiple collections
- Position field enables custom ordering within collections
- Unique constraint on (collection_id, place_id) prevents duplicates
- Soft delete independent from collection soft delete
- Added_at timestamp separate from position for sorting options
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

if TYPE_CHECKING:
    from app.models.collection import Collection


class CollectionItem(Base):
    """
    Represents a place within a collection.
    
    This is a junction table that connects collections to places,
    with additional metadata like position and notes.
    
    Key features:
    - Position field for custom ordering (drag-and-drop reordering)
    - Optional note for per-collection context about the place
    - Soft delete allows restoration without losing position
    """
    
    __tablename__ = "collection_items"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for this collection item"
    )
    
    # Foreign key to collection
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
        comment="Parent collection ID"
    )
    
    # Reference to external place
    place_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Opaque place identifier from external service"
    )
    
    # Position for ordering within collection
    # Using integer allows easy reordering (e.g., swap positions)
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Position within the collection (lower = earlier)"
    )
    
    # Optional user note specific to this place in this collection
    note: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="User's note about this place in this collection"
    )
    
    # Timestamps
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When the place was added to this collection"
    )
    
    # Soft delete support
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Soft delete timestamp, null if active"
    )
    
    # Relationships
    collection: Mapped["Collection"] = relationship(
        "Collection",
        back_populates="items"
    )
    
    # Constraints and indexes
    __table_args__ = (
        # A place can only be in a collection once
        UniqueConstraint(
            "collection_id", "place_id",
            name="uq_collection_items_collection_place"
        ),
        # Index for fetching items in a collection
        Index("ix_collection_items_collection_id_position", "collection_id", "position"),
        # Index for finding all collections containing a place
        Index("ix_collection_items_place_id", "place_id"),
        # Index for filtering out soft-deleted items
        Index("ix_collection_items_deleted_at", "deleted_at"),
    )
    
    def __repr__(self) -> str:
        return f"<CollectionItem(id={self.id}, collection_id={self.collection_id}, place_id={self.place_id})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if this item has been soft deleted."""
        return self.deleted_at is not None


