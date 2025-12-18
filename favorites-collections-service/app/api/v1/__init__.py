"""
API v1 routers.

This module provides versioned API endpoints.
Version prefix is added in main.py during router registration.
"""

from fastapi import APIRouter

from app.api.v1.favorites import router as favorites_router
from app.api.v1.collections import router as collections_router
from app.api.v1.public import router as public_router

# Main v1 router that combines all sub-routers
router = APIRouter()

# Include sub-routers with appropriate prefixes and tags
router.include_router(
    favorites_router,
    prefix="/favorites",
    tags=["Favorites"]
)

router.include_router(
    collections_router,
    prefix="/collections",
    tags=["Collections"]
)

router.include_router(
    public_router,
    prefix="/public",
    tags=["Public"]
)

__all__ = ["router"]


