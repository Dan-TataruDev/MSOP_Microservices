"""
API routes for public (unauthenticated) access to shared collections.

These endpoints allow anyone with a public_id to view shared collections.
No authentication required, but authenticated users get additional info.
"""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, get_optional_user
from app.services.collection_service import CollectionService
from app.schemas.collection import (
    PublicCollectionResponse,
    CollectionItemResponse,
)
from app.exceptions import NotFoundException

router = APIRouter()


@router.get(
    "/collections/{public_id}",
    response_model=PublicCollectionResponse,
    summary="Get public collection",
    description="Access a shared collection via its public ID. No authentication required."
)
async def get_public_collection(
    public_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[CurrentUser] = Depends(get_optional_user)
) -> PublicCollectionResponse:
    """
    Get a public collection by its public_id.
    
    This endpoint is accessible without authentication for sharing.
    
    Features:
    - No authentication required for viewing
    - If authenticated, shows is_owner flag for edit button visibility
    - Only returns collections marked as public
    - Returns 404 for non-public or non-existent collections
    
    Note: This endpoint only returns place IDs, not place details.
    The frontend should fetch place details from the appropriate service.
    """
    collection = await CollectionService.get_collection_by_public_id(
        db, public_id, include_items=True
    )
    
    if not collection:
        # Return generic 404 to avoid revealing whether collection exists but is private
        raise NotFoundException("Collection", public_id)
    
    # Determine if the viewing user is the owner
    is_owner = user is not None and user.user_id == collection.user_id
    
    return PublicCollectionResponse(
        public_id=collection.public_id,
        name=collection.name,
        description=collection.description,
        cover_image_url=collection.cover_image_url,
        item_count=collection.item_count,
        items=[
            CollectionItemResponse(
                id=item.id,
                place_id=item.place_id,
                note=item.note,
                position=item.position,
                added_at=item.added_at
            )
            for item in sorted(collection.items, key=lambda x: x.position)
        ],
        created_at=collection.created_at,
        is_owner=is_owner
    )


@router.head(
    "/collections/{public_id}",
    summary="Check if public collection exists",
    description="Check if a public collection exists without fetching full data."
)
async def check_public_collection_exists(
    public_id: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Check if a public collection exists.
    
    Returns 200 if exists, 404 if not.
    Useful for link validation without fetching the full collection.
    """
    collection = await CollectionService.get_collection_by_public_id(
        db, public_id, include_items=False
    )
    
    if not collection:
        raise NotFoundException("Collection", public_id)
    
    # HEAD request - no body returned
    return None


