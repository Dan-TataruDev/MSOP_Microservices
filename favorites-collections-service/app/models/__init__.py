"""
SQLAlchemy models for the Favorites & Collections Service.

This module exports all database models for easy importing elsewhere.
"""

from app.models.favorite import Favorite
from app.models.collection import Collection
from app.models.collection_item import CollectionItem

__all__ = ["Favorite", "Collection", "CollectionItem"]


