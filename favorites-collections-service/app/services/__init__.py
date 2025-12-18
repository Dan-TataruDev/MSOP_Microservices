"""
Service layer for business logic.

Services contain the core business logic and interact with the database.
They are independent of the HTTP layer for better testability.
"""

from app.services.favorite_service import FavoriteService
from app.services.collection_service import CollectionService

__all__ = ["FavoriteService", "CollectionService"]


