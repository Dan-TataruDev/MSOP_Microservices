"""
Pydantic schemas for Collection and CollectionItem operations.

Design decisions:
- Collections have full CRUD operations
- Collection items are managed through collection endpoints
- Public collections have a separate response schema (limited fields)
- Position-based reordering for drag-and-drop support
"""

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, HttpUrl


# =============================================================================
# Collection Item Schemas
# =============================================================================

class CollectionItemBase(BaseModel):
    """Base schema for collection items."""
    
    place_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Opaque place identifier from external service"
    )
    
    @field_validator("place_id")
    @classmethod
    def validate_place_id(cls, v: str) -> str:
        """Ensure place_id is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("place_id cannot be empty")
        return v.strip()


class CollectionItemAdd(CollectionItemBase):
    """
    Schema for adding a place to a collection.
    
    Position is optional - if not provided, item is added at the end.
    """
    
    note: Optional[str] = Field(
        None,
        max_length=1000,
        description="Note about this place in this collection"
    )
    position: Optional[int] = Field(
        None,
        ge=0,
        description="Position in the collection (optional, defaults to end)"
    )


class CollectionItemUpdate(BaseModel):
    """Schema for updating a collection item."""
    
    note: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated note"
    )
    position: Optional[int] = Field(
        None,
        ge=0,
        description="New position in the collection"
    )


class CollectionItemResponse(BaseModel):
    """
    Schema for collection item in responses.
    
    Note: Does NOT include place details - frontend fetches those separately.
    """
    
    id: uuid.UUID = Field(description="Item ID")
    place_id: str = Field(description="Place ID")
    note: Optional[str] = Field(description="User's note for this item")
    position: int = Field(description="Position in the collection")
    added_at: datetime = Field(description="When the item was added")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "place_id": "place_456",
                "note": "Must try the pasta!",
                "position": 0,
                "added_at": "2024-01-15T10:30:00Z"
            }
        }
    }


class CollectionItemReorder(BaseModel):
    """
    Schema for reordering items in a collection.
    
    Frontend sends the new order of item IDs, and the service
    updates positions accordingly.
    """
    
    item_ids: List[uuid.UUID] = Field(
        ...,
        min_length=1,
        description="Ordered list of item IDs representing new order"
    )


# =============================================================================
# Collection Schemas
# =============================================================================

class CollectionBase(BaseModel):
    """Base schema with shared collection fields."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Collection name"
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Collection name cannot be empty")
        return v.strip()


class CollectionCreate(CollectionBase):
    """
    Schema for creating a new collection.
    
    Collections are private by default.
    """
    
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Collection description"
    )
    cover_image_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="URL to cover image"
    )
    is_public: bool = Field(
        default=False,
        description="Whether the collection is publicly accessible"
    )


class CollectionUpdate(BaseModel):
    """
    Schema for updating an existing collection.
    
    All fields are optional - only provided fields are updated.
    """
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New collection name"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="New description"
    )
    cover_image_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="New cover image URL"
    )
    is_public: Optional[bool] = Field(
        None,
        description="Update visibility"
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Ensure name is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError("Collection name cannot be empty")
        return v.strip() if v else v


class CollectionResponse(BaseModel):
    """
    Full collection response for authenticated owner.
    
    Includes all fields including management URLs.
    """
    
    id: uuid.UUID = Field(description="Collection ID")
    user_id: str = Field(description="Owner's user ID")
    public_id: str = Field(description="Public sharing identifier")
    name: str = Field(description="Collection name")
    description: Optional[str] = Field(description="Collection description")
    cover_image_url: Optional[str] = Field(description="Cover image URL")
    is_public: bool = Field(description="Whether publicly accessible")
    item_count: int = Field(description="Number of places in collection")
    items: List[CollectionItemResponse] = Field(
        default=[],
        description="Places in this collection"
    )
    created_at: datetime = Field(description="When created")
    updated_at: datetime = Field(description="When last updated")
    
    # Computed field for share URL
    share_url: Optional[str] = Field(
        None,
        description="URL for sharing (only if public)"
    )
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "public_id": "abc123def456",
                "name": "Date Night Spots",
                "description": "Romantic restaurants for special occasions",
                "cover_image_url": "https://example.com/image.jpg",
                "is_public": True,
                "item_count": 5,
                "items": [],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T15:45:00Z",
                "share_url": "/public/collections/abc123def456"
            }
        }
    }


class CollectionSummaryResponse(BaseModel):
    """
    Lightweight collection response for list views.
    
    Excludes items to keep response size small.
    """
    
    id: uuid.UUID = Field(description="Collection ID")
    public_id: str = Field(description="Public sharing identifier")
    name: str = Field(description="Collection name")
    description: Optional[str] = Field(description="Collection description")
    cover_image_url: Optional[str] = Field(description="Cover image URL")
    is_public: bool = Field(description="Whether publicly accessible")
    item_count: int = Field(description="Number of places in collection")
    created_at: datetime = Field(description="When created")
    updated_at: datetime = Field(description="When last updated")
    
    model_config = {
        "from_attributes": True
    }


class CollectionListResponse(BaseModel):
    """
    Paginated list of collections.
    """
    
    items: List[CollectionSummaryResponse]
    total: int = Field(description="Total number of collections")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")


class PublicCollectionResponse(BaseModel):
    """
    Collection response for public (unauthenticated) access.
    
    Shows limited fields - no user_id or management info.
    Used for shared collection links.
    """
    
    public_id: str = Field(description="Public identifier")
    name: str = Field(description="Collection name")
    description: Optional[str] = Field(description="Collection description")
    cover_image_url: Optional[str] = Field(description="Cover image URL")
    item_count: int = Field(description="Number of places")
    items: List[CollectionItemResponse] = Field(
        default=[],
        description="Places in this collection (just IDs)"
    )
    created_at: datetime = Field(description="When created")
    
    # Indicates if the viewer is the owner (for edit button visibility)
    is_owner: bool = Field(
        default=False,
        description="Whether the current user owns this collection"
    )
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "public_id": "abc123def456",
                "name": "Date Night Spots",
                "description": "Romantic restaurants",
                "cover_image_url": "https://example.com/image.jpg",
                "item_count": 5,
                "items": [],
                "created_at": "2024-01-15T10:30:00Z",
                "is_owner": False
            }
        }
    }


class RegeneratePublicIdResponse(BaseModel):
    """Response after regenerating a collection's public ID."""
    
    old_public_id: str = Field(description="Previous public ID (now invalid)")
    new_public_id: str = Field(description="New public ID for sharing")
    message: str = Field(
        default="Public ID regenerated. Old share links will no longer work.",
        description="Informational message"
    )


