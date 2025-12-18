"""
Service layer for Collection and CollectionItem operations.

Design decisions:
- Collections are private by default with optional public sharing
- public_id can be regenerated to invalidate old share links
- Items have positions for custom ordering (drag-and-drop)
- Soft delete for collections and items for data recovery
- Ownership checks on all mutating operations
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.collection import Collection, generate_public_id
from app.models.collection_item import CollectionItem
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionItemAdd,
    CollectionItemUpdate,
)
from app.exceptions import (
    NotFoundException,
    ForbiddenException,
    ConflictException,
    ValidationException,
)


class CollectionService:
    """
    Service for managing collections and collection items.
    
    Provides methods for:
    - CRUD operations on collections
    - Adding/removing items from collections
    - Reordering items within collections
    - Public collection access
    """
    
    # =========================================================================
    # Collection CRUD Operations
    # =========================================================================
    
    @staticmethod
    async def get_collection(
        db: AsyncSession,
        collection_id: uuid.UUID,
        include_deleted: bool = False,
        include_items: bool = True
    ) -> Optional[Collection]:
        """
        Get a collection by ID.
        
        Args:
            db: Database session
            collection_id: Collection UUID
            include_deleted: Whether to include soft-deleted collections
            include_items: Whether to eagerly load items
            
        Returns:
            Collection if found, None otherwise
        """
        query = select(Collection).where(Collection.id == collection_id)
        
        if include_items:
            query = query.options(selectinload(Collection.items))
        
        if not include_deleted:
            query = query.where(Collection.deleted_at.is_(None))
        
        result = await db.execute(query)
        collection = result.scalar_one_or_none()
        
        # Filter out deleted items if loading items
        if collection and include_items:
            collection.items = [
                item for item in collection.items
                if item.deleted_at is None
            ]
        
        return collection
    
    @staticmethod
    async def get_collection_by_public_id(
        db: AsyncSession,
        public_id: str,
        include_items: bool = True
    ) -> Optional[Collection]:
        """
        Get a public collection by its public_id.
        
        Only returns collections that are marked as public.
        
        Args:
            db: Database session
            public_id: Public sharing identifier
            include_items: Whether to eagerly load items
            
        Returns:
            Collection if found and public, None otherwise
        """
        query = select(Collection).where(
            Collection.public_id == public_id,
            Collection.is_public == True,
            Collection.deleted_at.is_(None)
        )
        
        if include_items:
            query = query.options(selectinload(Collection.items))
        
        result = await db.execute(query)
        collection = result.scalar_one_or_none()
        
        # Filter out deleted items
        if collection and include_items:
            collection.items = [
                item for item in collection.items
                if item.deleted_at is None
            ]
        
        return collection
    
    @staticmethod
    async def list_user_collections(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        include_items: bool = False
    ) -> Tuple[List[Collection], int]:
        """
        List all collections for a user with pagination.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            include_items: Whether to include collection items
            
        Returns:
            Tuple of (list of collections, total count)
        """
        base_filter = and_(
            Collection.user_id == user_id,
            Collection.deleted_at.is_(None)
        )
        
        # Get total count
        count_query = select(func.count()).select_from(Collection).where(base_filter)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        offset = (page - 1) * page_size
        query = (
            select(Collection)
            .where(base_filter)
            .order_by(Collection.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        if include_items:
            query = query.options(selectinload(Collection.items))
        
        result = await db.execute(query)
        collections = list(result.scalars().all())
        
        # Calculate item counts (filter out deleted items)
        for collection in collections:
            if include_items:
                collection.items = [
                    item for item in collection.items
                    if item.deleted_at is None
                ]
        
        return collections, total
    
    @staticmethod
    async def create_collection(
        db: AsyncSession,
        user_id: str,
        data: CollectionCreate
    ) -> Collection:
        """
        Create a new collection.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            data: Collection creation data
            
        Returns:
            Created Collection
        """
        collection = Collection(
            user_id=user_id,
            name=data.name,
            description=data.description,
            cover_image_url=data.cover_image_url,
            is_public=data.is_public
        )
        
        db.add(collection)
        await db.commit()
        await db.refresh(collection)
        
        # Initialize empty items list
        collection.items = []
        
        return collection
    
    @staticmethod
    async def update_collection(
        db: AsyncSession,
        collection_id: uuid.UUID,
        user_id: str,
        data: CollectionUpdate
    ) -> Collection:
        """
        Update a collection.
        
        Only the owner can update their collections.
        
        Args:
            db: Database session
            collection_id: Collection UUID
            user_id: Requesting user's ID (for ownership check)
            data: Update data
            
        Returns:
            Updated Collection
            
        Raises:
            NotFoundException: If collection doesn't exist
            ForbiddenException: If user doesn't own the collection
        """
        collection = await CollectionService.get_collection(
            db, collection_id, include_items=True
        )
        
        if not collection:
            raise NotFoundException("Collection", str(collection_id))
        
        if collection.user_id != user_id:
            raise ForbiddenException("You can only update your own collections")
        
        # Update provided fields
        if data.name is not None:
            collection.name = data.name
        if data.description is not None:
            collection.description = data.description
        if data.cover_image_url is not None:
            collection.cover_image_url = data.cover_image_url
        if data.is_public is not None:
            collection.is_public = data.is_public
        
        collection.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(collection)
        
        return collection
    
    @staticmethod
    async def delete_collection(
        db: AsyncSession,
        collection_id: uuid.UUID,
        user_id: str,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a collection.
        
        Soft delete by default for data recovery.
        
        Args:
            db: Database session
            collection_id: Collection UUID
            user_id: Requesting user's ID (for ownership check)
            hard_delete: If True, permanently delete
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundException: If collection doesn't exist
            ForbiddenException: If user doesn't own the collection
        """
        collection = await CollectionService.get_collection(
            db, collection_id, include_items=False
        )
        
        if not collection:
            raise NotFoundException("Collection", str(collection_id))
        
        if collection.user_id != user_id:
            raise ForbiddenException("You can only delete your own collections")
        
        if hard_delete:
            await db.delete(collection)
        else:
            collection.deleted_at = datetime.now(timezone.utc)
        
        await db.commit()
        return True
    
    @staticmethod
    async def regenerate_public_id(
        db: AsyncSession,
        collection_id: uuid.UUID,
        user_id: str
    ) -> Tuple[str, str]:
        """
        Regenerate a collection's public_id.
        
        This invalidates all existing share links.
        
        Args:
            db: Database session
            collection_id: Collection UUID
            user_id: Requesting user's ID (for ownership check)
            
        Returns:
            Tuple of (old_public_id, new_public_id)
            
        Raises:
            NotFoundException: If collection doesn't exist
            ForbiddenException: If user doesn't own the collection
        """
        collection = await CollectionService.get_collection(
            db, collection_id, include_items=False
        )
        
        if not collection:
            raise NotFoundException("Collection", str(collection_id))
        
        if collection.user_id != user_id:
            raise ForbiddenException("You can only modify your own collections")
        
        old_public_id = collection.public_id
        collection.public_id = generate_public_id()
        collection.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        return old_public_id, collection.public_id
    
    # =========================================================================
    # Collection Item Operations
    # =========================================================================
    
    @staticmethod
    async def get_collection_item(
        db: AsyncSession,
        item_id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[CollectionItem]:
        """
        Get a collection item by ID.
        
        Args:
            db: Database session
            item_id: Item UUID
            include_deleted: Whether to include soft-deleted items
            
        Returns:
            CollectionItem if found, None otherwise
        """
        query = select(CollectionItem).where(CollectionItem.id == item_id)
        
        if not include_deleted:
            query = query.where(CollectionItem.deleted_at.is_(None))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_item_to_collection(
        db: AsyncSession,
        collection_id: uuid.UUID,
        user_id: str,
        data: CollectionItemAdd
    ) -> Tuple[CollectionItem, bool]:
        """
        Add a place to a collection.
        
        Idempotent: if the place is already in the collection,
        updates the note instead of erroring.
        
        Args:
            db: Database session
            collection_id: Collection UUID
            user_id: Requesting user's ID (for ownership check)
            data: Item data
            
        Returns:
            Tuple of (CollectionItem, was_created)
            
        Raises:
            NotFoundException: If collection doesn't exist
            ForbiddenException: If user doesn't own the collection
        """
        collection = await CollectionService.get_collection(
            db, collection_id, include_items=True
        )
        
        if not collection:
            raise NotFoundException("Collection", str(collection_id))
        
        if collection.user_id != user_id:
            raise ForbiddenException("You can only add items to your own collections")
        
        # Check for existing item (including deleted)
        query = select(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.place_id == data.place_id
        )
        result = await db.execute(query)
        existing_item = result.scalar_one_or_none()
        
        if existing_item:
            if existing_item.deleted_at is not None:
                # Restore soft-deleted item
                existing_item.deleted_at = None
                existing_item.note = data.note
                existing_item.added_at = datetime.now(timezone.utc)
                if data.position is not None:
                    existing_item.position = data.position
                await db.commit()
                await db.refresh(existing_item)
                return existing_item, True
            else:
                # Already exists - update note (idempotent)
                if data.note is not None:
                    existing_item.note = data.note
                    await db.commit()
                    await db.refresh(existing_item)
                return existing_item, False
        
        # Determine position
        if data.position is not None:
            position = data.position
        else:
            # Add to end
            max_position = max(
                (item.position for item in collection.items),
                default=-1
            )
            position = max_position + 1
        
        # Create new item
        item = CollectionItem(
            collection_id=collection_id,
            place_id=data.place_id,
            note=data.note,
            position=position
        )
        
        db.add(item)
        
        # Update collection's updated_at
        collection.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(item)
        
        return item, True
    
    @staticmethod
    async def update_collection_item(
        db: AsyncSession,
        item_id: uuid.UUID,
        user_id: str,
        data: CollectionItemUpdate
    ) -> CollectionItem:
        """
        Update a collection item.
        
        Args:
            db: Database session
            item_id: Item UUID
            user_id: Requesting user's ID (for ownership check)
            data: Update data
            
        Returns:
            Updated CollectionItem
            
        Raises:
            NotFoundException: If item doesn't exist
            ForbiddenException: If user doesn't own the collection
        """
        item = await CollectionService.get_collection_item(db, item_id)
        
        if not item:
            raise NotFoundException("Collection item", str(item_id))
        
        # Check collection ownership
        collection = await CollectionService.get_collection(
            db, item.collection_id, include_items=False
        )
        
        if not collection or collection.user_id != user_id:
            raise ForbiddenException("You can only update items in your own collections")
        
        # Update fields
        if data.note is not None:
            item.note = data.note
        if data.position is not None:
            item.position = data.position
        
        collection.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(item)
        
        return item
    
    @staticmethod
    async def remove_item_from_collection(
        db: AsyncSession,
        item_id: uuid.UUID,
        user_id: str,
        hard_delete: bool = False
    ) -> bool:
        """
        Remove an item from a collection.
        
        Args:
            db: Database session
            item_id: Item UUID
            user_id: Requesting user's ID (for ownership check)
            hard_delete: If True, permanently delete
            
        Returns:
            True if removed
            
        Raises:
            NotFoundException: If item doesn't exist
            ForbiddenException: If user doesn't own the collection
        """
        item = await CollectionService.get_collection_item(db, item_id)
        
        if not item:
            raise NotFoundException("Collection item", str(item_id))
        
        # Check collection ownership
        collection = await CollectionService.get_collection(
            db, item.collection_id, include_items=False
        )
        
        if not collection or collection.user_id != user_id:
            raise ForbiddenException("You can only remove items from your own collections")
        
        if hard_delete:
            await db.delete(item)
        else:
            item.deleted_at = datetime.now(timezone.utc)
        
        collection.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        return True
    
    @staticmethod
    async def remove_place_from_collection(
        db: AsyncSession,
        collection_id: uuid.UUID,
        place_id: str,
        user_id: str,
        hard_delete: bool = False
    ) -> bool:
        """
        Remove a place from a collection by place_id.
        
        Alternative to remove_item_from_collection when you don't have the item_id.
        Idempotent - returns False if place wasn't in collection.
        
        Args:
            db: Database session
            collection_id: Collection UUID
            place_id: Place identifier
            user_id: Requesting user's ID (for ownership check)
            hard_delete: If True, permanently delete
            
        Returns:
            True if removed, False if not found
            
        Raises:
            NotFoundException: If collection doesn't exist
            ForbiddenException: If user doesn't own the collection
        """
        collection = await CollectionService.get_collection(
            db, collection_id, include_items=False
        )
        
        if not collection:
            raise NotFoundException("Collection", str(collection_id))
        
        if collection.user_id != user_id:
            raise ForbiddenException("You can only remove items from your own collections")
        
        # Find the item
        query = select(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.place_id == place_id,
            CollectionItem.deleted_at.is_(None)
        )
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            return False
        
        if hard_delete:
            await db.delete(item)
        else:
            item.deleted_at = datetime.now(timezone.utc)
        
        collection.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        return True
    
    @staticmethod
    async def reorder_collection_items(
        db: AsyncSession,
        collection_id: uuid.UUID,
        user_id: str,
        item_ids: List[uuid.UUID]
    ) -> List[CollectionItem]:
        """
        Reorder items in a collection.
        
        Takes a list of item IDs in the desired order and updates
        their positions accordingly.
        
        Args:
            db: Database session
            collection_id: Collection UUID
            user_id: Requesting user's ID (for ownership check)
            item_ids: List of item IDs in desired order
            
        Returns:
            List of reordered CollectionItems
            
        Raises:
            NotFoundException: If collection doesn't exist
            ForbiddenException: If user doesn't own the collection
            ValidationException: If item_ids don't match collection items
        """
        collection = await CollectionService.get_collection(
            db, collection_id, include_items=True
        )
        
        if not collection:
            raise NotFoundException("Collection", str(collection_id))
        
        if collection.user_id != user_id:
            raise ForbiddenException("You can only reorder items in your own collections")
        
        # Validate item_ids match collection items
        existing_ids = {item.id for item in collection.items if not item.is_deleted}
        provided_ids = set(item_ids)
        
        if existing_ids != provided_ids:
            missing = existing_ids - provided_ids
            extra = provided_ids - existing_ids
            raise ValidationException(
                f"Item IDs mismatch. Missing: {len(missing)}, Extra: {len(extra)}"
            )
        
        # Update positions
        item_map = {item.id: item for item in collection.items}
        for position, item_id in enumerate(item_ids):
            item_map[item_id].position = position
        
        collection.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        # Return items in new order
        return sorted(collection.items, key=lambda x: x.position)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    @staticmethod
    async def get_collection_count(
        db: AsyncSession,
        user_id: str
    ) -> int:
        """
        Get total count of user's collections.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of collections
        """
        query = select(func.count()).select_from(Collection).where(
            Collection.user_id == user_id,
            Collection.deleted_at.is_(None)
        )
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    @staticmethod
    async def check_place_in_collections(
        db: AsyncSession,
        user_id: str,
        place_id: str
    ) -> List[uuid.UUID]:
        """
        Find which of the user's collections contain a specific place.
        
        Useful for showing "Add to collection" UI with checkmarks.
        
        Args:
            db: Database session
            user_id: User ID
            place_id: Place identifier
            
        Returns:
            List of collection IDs containing the place
        """
        query = (
            select(CollectionItem.collection_id)
            .join(Collection)
            .where(
                Collection.user_id == user_id,
                Collection.deleted_at.is_(None),
                CollectionItem.place_id == place_id,
                CollectionItem.deleted_at.is_(None)
            )
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())


