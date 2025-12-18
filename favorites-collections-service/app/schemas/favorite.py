"""
Pydantic schemas for Favorite operations.

Design decisions:
- Separate schemas for create/update/response to control exposed fields
- place_id is required and validated as non-empty string
- Response includes all fields frontend needs for display
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class FavoriteBase(BaseModel):
    """Base schema with shared favorite fields."""
    
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


class FavoriteCreate(FavoriteBase):
    """
    Schema for creating a new favorite.
    
    Only place_id is required - user_id comes from auth token.
    Note is optional for adding context.
    """
    
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional note about why this place was favorited"
    )


class FavoriteUpdate(BaseModel):
    """
    Schema for updating an existing favorite.
    
    Currently only allows updating the note field.
    place_id cannot be changed (unfavorite and re-favorite instead).
    """
    
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated note for the favorite"
    )


class FavoriteResponse(BaseModel):
    """
    Schema for favorite response.
    
    Includes all fields the frontend needs for display.
    Note: Does NOT include place details - frontend should fetch those separately.
    """
    
    user_id: str = Field(description="Owner's user ID")
    place_id: str = Field(description="The favorited place ID")
    note: Optional[str] = Field(description="User's note about this favorite")
    created_at: datetime = Field(description="When the favorite was created")
    
    # Computed field to help frontend check favorite status
    is_favorited: bool = Field(default=True, description="Always true in response")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "place_id": "place_456",
                "note": "Great coffee shop for working",
                "created_at": "2024-01-15T10:30:00Z",
                "is_favorited": True
            }
        }
    }


class FavoriteStatusResponse(BaseModel):
    """
    Lightweight response for checking if a place is favorited.
    
    Useful for the frontend to show/hide favorite button states
    without fetching full favorite details.
    """
    
    place_id: str
    is_favorited: bool
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "place_id": "place_456",
                "is_favorited": True
            }
        }
    }


class FavoriteListResponse(BaseModel):
    """
    Response for listing multiple favorites.
    
    Uses standard pagination structure.
    """
    
    items: List[FavoriteResponse]
    total: int = Field(description="Total number of favorites")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "user_id": "user_123",
                        "place_id": "place_456",
                        "note": "Great for dates",
                        "created_at": "2024-01-15T10:30:00Z",
                        "is_favorited": True
                    }
                ],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "total_pages": 3,
                "has_next": True,
                "has_prev": False
            }
        }
    }


class BulkFavoriteStatusRequest(BaseModel):
    """
    Request to check favorite status for multiple places at once.
    
    Useful for list views where frontend needs to show favorite
    status for many places without making individual API calls.
    """
    
    place_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of place IDs to check (max 100)"
    )


class BulkFavoriteStatusResponse(BaseModel):
    """
    Response for bulk favorite status check.
    
    Returns a mapping of place_id -> is_favorited for quick lookup.
    """
    
    favorites: dict[str, bool] = Field(
        description="Map of place_id to is_favorited status"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "favorites": {
                    "place_123": True,
                    "place_456": False,
                    "place_789": True
                }
            }
        }
    }
