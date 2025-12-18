"""
Favorite model - represents a user's favorited place.

Design decisions:
- Uses composite primary key (user_id, place_id) for uniqueness
- Includes soft delete support via deleted_at timestamp
- place_id is an opaque string - this service doesn't validate or store place details
- Timestamps for analytics and sorting
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Favorite(Base):
    """
    Represents a favorited place for a user.
    
    This is a simple many-to-many relationship between users and places,
    where place_id references an external service's place identifier.
    
    The composite primary key ensures a user can only favorite a place once.
    """
    
    __tablename__ = "favorites"
    
    # Composite primary key - a user can only favorite a place once
    user_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        comment="User ID from the authentication service"
    )
    place_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        comment="Opaque place identifier from external service"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When the place was favorited"
    )
    
    # Soft delete support
    # When not None, the favorite is considered deleted
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Soft delete timestamp, null if active"
    )
    
    # Optional: category/type hint for better organization in UI
    # This is user-provided metadata, not the actual place type
    note: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional user note about why they favorited this place"
    )
    
    # Indexes for common queries
    __table_args__ = (
        # Index for listing user's favorites
        Index("ix_favorites_user_id_created_at", "user_id", "created_at"),
        # Index for filtering out soft-deleted records
        Index("ix_favorites_deleted_at", "deleted_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Favorite(user_id={self.user_id}, place_id={self.place_id})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if this favorite has been soft deleted."""
        return self.deleted_at is not None


