"""
API routes for Favorite operations.

All endpoints require authentication.
Provides CRUD operations for user favorites with idempotent behavior.
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, get_current_user
from app.services.favorite_service import FavoriteService
from app.schemas.favorite import (
    FavoriteCreate,
    FavoriteUpdate,
    FavoriteResponse,
    FavoriteListResponse,
    FavoriteStatusResponse,
    BulkFavoriteStatusRequest,
    BulkFavoriteStatusResponse,
)
from app.schemas.common import SuccessResponse
from app.exceptions import NotFoundException

router = APIRouter()


@router.get(
    "",
    response_model=FavoriteListResponse,
    summary="List user's favorites",
    description="Get a paginated list of all favorited places for the authenticated user."
)
async def list_favorites(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> FavoriteListResponse:
    """
    List all favorites for the current user.
    
    Returns favorites sorted by most recently added first.
    """
    favorites, total = await FavoriteService.list_favorites(
        db, user.user_id, page, page_size
    )
    
    # Calculate pagination metadata
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return FavoriteListResponse(
        items=[
            FavoriteResponse(
                user_id=fav.user_id,
                place_id=fav.place_id,
                note=fav.note,
                created_at=fav.created_at,
                is_favorited=True
            )
            for fav in favorites
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.post(
    "",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a favorite",
    description="Add a place to the user's favorites. Idempotent - adding an existing favorite is not an error."
)
async def add_favorite(
    data: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> FavoriteResponse:
    """
    Add a place to favorites.
    
    This operation is idempotent:
    - If the place is not favorited, it will be added
    - If the place is already favorited, the note will be updated (if provided)
    - No error is returned for duplicate favorites
    """
    favorite, _ = await FavoriteService.add_favorite(db, user.user_id, data)
    
    return FavoriteResponse(
        user_id=favorite.user_id,
        place_id=favorite.place_id,
        note=favorite.note,
        created_at=favorite.created_at,
        is_favorited=True
    )


@router.get(
    "/{place_id}",
    response_model=FavoriteResponse,
    summary="Get a specific favorite",
    description="Get details of a specific favorite by place ID."
)
async def get_favorite(
    place_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> FavoriteResponse:
    """
    Get a specific favorite by place ID.
    
    Returns 404 if the place is not in the user's favorites.
    """
    favorite = await FavoriteService.get_favorite(db, user.user_id, place_id)
    
    if not favorite:
        raise NotFoundException("Favorite", place_id)
    
    return FavoriteResponse(
        user_id=favorite.user_id,
        place_id=favorite.place_id,
        note=favorite.note,
        created_at=favorite.created_at,
        is_favorited=True
    )


@router.patch(
    "/{place_id}",
    response_model=FavoriteResponse,
    summary="Update a favorite",
    description="Update the note on a favorite."
)
async def update_favorite(
    place_id: str,
    data: FavoriteUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> FavoriteResponse:
    """
    Update a favorite's metadata.
    
    Currently only supports updating the note field.
    """
    favorite = await FavoriteService.update_favorite(
        db, user.user_id, place_id, data
    )
    
    return FavoriteResponse(
        user_id=favorite.user_id,
        place_id=favorite.place_id,
        note=favorite.note,
        created_at=favorite.created_at,
        is_favorited=True
    )


@router.delete(
    "/{place_id}",
    response_model=SuccessResponse,
    summary="Remove a favorite",
    description="Remove a place from favorites. Idempotent - removing a non-existent favorite is not an error."
)
async def remove_favorite(
    place_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> SuccessResponse:
    """
    Remove a place from favorites.
    
    This operation is idempotent - removing a place that's not
    favorited will still return success.
    
    Uses soft delete by default for data recovery.
    """
    removed = await FavoriteService.remove_favorite(db, user.user_id, place_id)
    
    return SuccessResponse(
        success=True,
        message="Favorite removed" if removed else "Place was not in favorites"
    )


@router.get(
    "/{place_id}/status",
    response_model=FavoriteStatusResponse,
    summary="Check favorite status",
    description="Check if a specific place is favorited by the user."
)
async def check_favorite_status(
    place_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> FavoriteStatusResponse:
    """
    Check if a place is in the user's favorites.
    
    Lightweight endpoint for UI status indicators.
    """
    is_favorited = await FavoriteService.check_favorite_status(
        db, user.user_id, place_id
    )
    
    return FavoriteStatusResponse(
        place_id=place_id,
        is_favorited=is_favorited
    )


@router.post(
    "/bulk-status",
    response_model=BulkFavoriteStatusResponse,
    summary="Check favorite status for multiple places",
    description="Efficiently check favorite status for multiple places at once."
)
async def bulk_check_favorite_status(
    data: BulkFavoriteStatusRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> BulkFavoriteStatusResponse:
    """
    Check favorite status for multiple places at once.
    
    Useful for list views where the frontend needs to show
    favorite buttons/icons for many places.
    
    Limited to 100 place IDs per request.
    """
    favorites = await FavoriteService.bulk_check_favorite_status(
        db, user.user_id, data.place_ids
    )
    
    return BulkFavoriteStatusResponse(favorites=favorites)


@router.post(
    "/{place_id}/toggle",
    response_model=FavoriteStatusResponse,
    summary="Toggle favorite status",
    description="Toggle a place's favorite status - favorites if not favorited, unfavorites if already favorited."
)
async def toggle_favorite(
    place_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> FavoriteStatusResponse:
    """
    Toggle favorite status for a place.
    
    Convenience endpoint for heart button interactions:
    - If not favorited, adds to favorites
    - If favorited, removes from favorites
    
    Returns the new favorite status.
    """
    is_favorited, _ = await FavoriteService.toggle_favorite(
        db, user.user_id, place_id
    )
    
    return FavoriteStatusResponse(
        place_id=place_id,
        is_favorited=is_favorited
    )


