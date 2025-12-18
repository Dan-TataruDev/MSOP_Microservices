"""
Pydantic schemas for request/response validation.

This module exports all schemas for easy importing elsewhere.
"""

from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    SuccessResponse,
    MessageResponse,
)
from app.schemas.favorite import (
    FavoriteCreate,
    FavoriteUpdate,
    FavoriteResponse,
    FavoriteListResponse,
)
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionListResponse,
    CollectionItemAdd,
    CollectionItemUpdate,
    CollectionItemResponse,
    CollectionItemReorder,
    PublicCollectionResponse,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    "SuccessResponse",
    "MessageResponse",
    # Favorites
    "FavoriteCreate",
    "FavoriteUpdate",
    "FavoriteResponse",
    "FavoriteListResponse",
    # Collections
    "CollectionCreate",
    "CollectionUpdate",
    "CollectionResponse",
    "CollectionListResponse",
    "CollectionItemAdd",
    "CollectionItemUpdate",
    "CollectionItemResponse",
    "CollectionItemReorder",
    "PublicCollectionResponse",
]


