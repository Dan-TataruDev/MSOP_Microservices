"""
API routes for Collection operations.

All endpoints require authentication.
Provides CRUD operations for collections and their items.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, get_current_user
from app.services.collection_service import CollectionService
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionSummaryResponse,
    CollectionListResponse,
    CollectionItemAdd,
    CollectionItemUpdate,
    CollectionItemResponse,
    CollectionItemReorder,
    RegeneratePublicIdResponse,
)
from app.schemas.common import SuccessResponse

router = APIRouter()


# =============================================================================
# Collection CRUD Endpoints
# =============================================================================

@router.get(
    "",
    response_model=CollectionListResponse,
    summary="List user's collections",
    description="Get a paginated list of all collections for the authenticated user."
)
async def list_collections(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> CollectionListResponse:
    """
    List all collections for the current user.
    
    Returns collections sorted by most recently updated first.
    Does not include collection items - use GET /collections/{id} for full details.
    """
    collections, total = await CollectionService.list_user_collections(
        db, user.user_id, page, page_size, include_items=False
    )
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return CollectionListResponse(
        items=[
            CollectionSummaryResponse(
                id=c.id,
                public_id=c.public_id,
                name=c.name,
                description=c.description,
                cover_image_url=c.cover_image_url,
                is_public=c.is_public,
                item_count=c.item_count,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in collections
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
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a collection",
    description="Create a new collection for the authenticated user."
)
async def create_collection(
    data: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> CollectionResponse:
    """
    Create a new collection.
    
    Collections are private by default. Set is_public=true to enable sharing.
    """
    collection = await CollectionService.create_collection(db, user.user_id, data)
    
    return _build_collection_response(collection)


@router.get(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Get a collection",
    description="Get full details of a collection including all items."
)
async def get_collection(
    collection_id: uuid.UUID = Path(..., description="Collection ID"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> CollectionResponse:
    """
    Get a collection by ID with all its items.
    
    Only the owner can access their collections via this endpoint.
    For public collections, use the /public endpoint.
    """
    from app.exceptions import NotFoundException, ForbiddenException
    
    collection = await CollectionService.get_collection(
        db, collection_id, include_items=True
    )
    
    if not collection:
        raise NotFoundException("Collection", str(collection_id))
    
    if collection.user_id != user.user_id:
        raise ForbiddenException("You can only view your own collections")
    
    return _build_collection_response(collection)


@router.patch(
    "/{collection_id}",
    response_model=CollectionResponse,
    summary="Update a collection",
    description="Update collection metadata. Only provided fields are updated."
)
async def update_collection(
    collection_id: uuid.UUID,
    data: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> CollectionResponse:
    """
    Update a collection's metadata.
    
    Only the owner can update their collections.
    All fields are optional - only provided fields will be updated.
    """
    collection = await CollectionService.update_collection(
        db, collection_id, user.user_id, data
    )
    
    return _build_collection_response(collection)


@router.delete(
    "/{collection_id}",
    response_model=SuccessResponse,
    summary="Delete a collection",
    description="Delete a collection and all its items."
)
async def delete_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> SuccessResponse:
    """
    Delete a collection.
    
    Uses soft delete by default for data recovery.
    Only the owner can delete their collections.
    """
    await CollectionService.delete_collection(db, collection_id, user.user_id)
    
    return SuccessResponse(success=True, message="Collection deleted")


@router.post(
    "/{collection_id}/regenerate-public-id",
    response_model=RegeneratePublicIdResponse,
    summary="Regenerate public ID",
    description="Generate a new public ID, invalidating all existing share links."
)
async def regenerate_public_id(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> RegeneratePublicIdResponse:
    """
    Regenerate the collection's public_id.
    
    This invalidates all existing share links. Use this if you want
    to revoke access for anyone who has the old link.
    """
    old_id, new_id = await CollectionService.regenerate_public_id(
        db, collection_id, user.user_id
    )
    
    return RegeneratePublicIdResponse(
        old_public_id=old_id,
        new_public_id=new_id
    )


# =============================================================================
# Collection Item Endpoints
# =============================================================================

@router.post(
    "/{collection_id}/items",
    response_model=CollectionItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to collection",
    description="Add a place to a collection. Idempotent - adding an existing place updates the note."
)
async def add_item_to_collection(
    collection_id: uuid.UUID,
    data: CollectionItemAdd,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> CollectionItemResponse:
    """
    Add a place to a collection.
    
    This operation is idempotent:
    - If the place is not in the collection, it will be added
    - If the place is already in the collection, the note will be updated
    
    Position is optional - if not provided, the item is added at the end.
    """
    item, _ = await CollectionService.add_item_to_collection(
        db, collection_id, user.user_id, data
    )
    
    return CollectionItemResponse(
        id=item.id,
        place_id=item.place_id,
        note=item.note,
        position=item.position,
        added_at=item.added_at
    )


@router.patch(
    "/{collection_id}/items/{item_id}",
    response_model=CollectionItemResponse,
    summary="Update collection item",
    description="Update an item's note or position within the collection."
)
async def update_collection_item(
    collection_id: uuid.UUID,
    item_id: uuid.UUID,
    data: CollectionItemUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> CollectionItemResponse:
    """
    Update a collection item's metadata.
    
    Can update the note and/or position.
    For bulk reordering, use the reorder endpoint instead.
    """
    item = await CollectionService.update_collection_item(
        db, item_id, user.user_id, data
    )
    
    return CollectionItemResponse(
        id=item.id,
        place_id=item.place_id,
        note=item.note,
        position=item.position,
        added_at=item.added_at
    )


@router.delete(
    "/{collection_id}/items/{item_id}",
    response_model=SuccessResponse,
    summary="Remove item from collection",
    description="Remove an item from a collection by item ID."
)
async def remove_collection_item(
    collection_id: uuid.UUID,
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> SuccessResponse:
    """
    Remove an item from a collection.
    
    Uses soft delete by default for data recovery.
    """
    await CollectionService.remove_item_from_collection(
        db, item_id, user.user_id
    )
    
    return SuccessResponse(success=True, message="Item removed from collection")


@router.delete(
    "/{collection_id}/places/{place_id}",
    response_model=SuccessResponse,
    summary="Remove place from collection",
    description="Remove a place from a collection by place ID (alternative to item ID)."
)
async def remove_place_from_collection(
    collection_id: uuid.UUID,
    place_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> SuccessResponse:
    """
    Remove a place from a collection by place_id.
    
    Alternative to the item ID endpoint when you only have the place_id.
    This operation is idempotent.
    """
    removed = await CollectionService.remove_place_from_collection(
        db, collection_id, place_id, user.user_id
    )
    
    return SuccessResponse(
        success=True,
        message="Place removed from collection" if removed else "Place was not in collection"
    )


@router.put(
    "/{collection_id}/items/reorder",
    response_model=List[CollectionItemResponse],
    summary="Reorder collection items",
    description="Reorder all items in a collection. Provide the complete list of item IDs in the desired order."
)
async def reorder_collection_items(
    collection_id: uuid.UUID,
    data: CollectionItemReorder,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> List[CollectionItemResponse]:
    """
    Reorder items in a collection.
    
    Expects a complete list of all item IDs in the desired order.
    The list must contain exactly all non-deleted items in the collection.
    
    This is designed for drag-and-drop reordering interfaces.
    """
    items = await CollectionService.reorder_collection_items(
        db, collection_id, user.user_id, data.item_ids
    )
    
    return [
        CollectionItemResponse(
            id=item.id,
            place_id=item.place_id,
            note=item.note,
            position=item.position,
            added_at=item.added_at
        )
        for item in items
    ]


# =============================================================================
# Utility Endpoints
# =============================================================================

@router.get(
    "/containing/{place_id}",
    response_model=List[uuid.UUID],
    summary="Find collections containing a place",
    description="Get IDs of all user's collections that contain a specific place."
)
async def find_collections_containing_place(
    place_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
) -> List[uuid.UUID]:
    """
    Find which of the user's collections contain a specific place.
    
    Useful for "Add to collection" UI with checkmarks showing
    which collections already contain the place.
    """
    collection_ids = await CollectionService.check_place_in_collections(
        db, user.user_id, place_id
    )
    
    return collection_ids


# =============================================================================
# Helper Functions
# =============================================================================

def _build_collection_response(collection) -> CollectionResponse:
    """Build a CollectionResponse from a Collection model."""
    return CollectionResponse(
        id=collection.id,
        user_id=collection.user_id,
        public_id=collection.public_id,
        name=collection.name,
        description=collection.description,
        cover_image_url=collection.cover_image_url,
        is_public=collection.is_public,
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
        updated_at=collection.updated_at,
        share_url=f"/public/collections/{collection.public_id}" if collection.is_public else None
    )


