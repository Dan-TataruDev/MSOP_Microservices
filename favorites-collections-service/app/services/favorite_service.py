"""
Service layer for Favorite operations.

Design decisions:
- Idempotent operations: favoriting an already-favorited place is a no-op
- Soft delete: unfavoriting marks deleted_at instead of removing the row
- This allows restoring favorites and preserves analytics data
- All queries filter out soft-deleted records by default
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteUpdate, FavoriteResponse
from app.exceptions import NotFoundException


class FavoriteService:
    """
    Service for managing user favorites.
    
    All methods are class methods that take a database session,
    making them easy to use in dependency injection.
    """
    
    @staticmethod
    async def get_favorite(
        db: AsyncSession,
        user_id: str,
        place_id: str,
        include_deleted: bool = False
    ) -> Optional[Favorite]:
        """
        Get a specific favorite by user_id and place_id.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            place_id: Place identifier
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            Favorite if found, None otherwise
        """
        query = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.place_id == place_id
        )
        
        if not include_deleted:
            query = query.where(Favorite.deleted_at.is_(None))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_favorites(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Favorite], int]:
        """
        List all favorites for a user with pagination.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (list of favorites, total count)
        """
        # Base query filters
        base_filter = and_(
            Favorite.user_id == user_id,
            Favorite.deleted_at.is_(None)
        )
        
        # Get total count
        count_query = select(func.count()).select_from(Favorite).where(base_filter)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results, ordered by most recent first
        offset = (page - 1) * page_size
        query = (
            select(Favorite)
            .where(base_filter)
            .order_by(Favorite.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        result = await db.execute(query)
        favorites = list(result.scalars().all())
        
        return favorites, total
    
    @staticmethod
    async def add_favorite(
        db: AsyncSession,
        user_id: str,
        data: FavoriteCreate
    ) -> Tuple[Favorite, bool]:
        """
        Add a place to user's favorites.
        
        This operation is idempotent:
        - If the favorite doesn't exist, create it
        - If it exists but is soft-deleted, restore it
        - If it exists and is active, update the note (no error)
        
        Args:
            db: Database session
            user_id: Owner's user ID
            data: Favorite creation data
            
        Returns:
            Tuple of (Favorite, was_created)
            was_created is True if this was a new favorite
        """
        # Check for existing favorite (including soft-deleted)
        existing = await FavoriteService.get_favorite(
            db, user_id, data.place_id, include_deleted=True
        )
        
        if existing:
            if existing.deleted_at is not None:
                # Restore soft-deleted favorite
                existing.deleted_at = None
                existing.note = data.note
                existing.created_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(existing)
                return existing, True
            else:
                # Already favorited - update note if provided (idempotent)
                if data.note is not None:
                    existing.note = data.note
                    await db.commit()
                    await db.refresh(existing)
                return existing, False
        
        # Create new favorite
        favorite = Favorite(
            user_id=user_id,
            place_id=data.place_id,
            note=data.note
        )
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        
        return favorite, True
    
    @staticmethod
    async def update_favorite(
        db: AsyncSession,
        user_id: str,
        place_id: str,
        data: FavoriteUpdate
    ) -> Favorite:
        """
        Update a favorite's metadata (currently just the note).
        
        Args:
            db: Database session
            user_id: Owner's user ID
            place_id: Place identifier
            data: Update data
            
        Returns:
            Updated Favorite
            
        Raises:
            NotFoundException: If favorite doesn't exist
        """
        favorite = await FavoriteService.get_favorite(db, user_id, place_id)
        
        if not favorite:
            raise NotFoundException("Favorite", place_id)
        
        # Update fields
        if data.note is not None:
            favorite.note = data.note
        
        await db.commit()
        await db.refresh(favorite)
        
        return favorite
    
    @staticmethod
    async def remove_favorite(
        db: AsyncSession,
        user_id: str,
        place_id: str,
        hard_delete: bool = False
    ) -> bool:
        """
        Remove a place from user's favorites.
        
        This operation is idempotent - removing a non-existent favorite
        is not an error.
        
        Args:
            db: Database session
            user_id: Owner's user ID
            place_id: Place identifier
            hard_delete: If True, permanently delete; if False, soft delete
            
        Returns:
            True if a favorite was removed, False if it didn't exist
        """
        favorite = await FavoriteService.get_favorite(db, user_id, place_id)
        
        if not favorite:
            # Idempotent - already not favorited
            return False
        
        if hard_delete:
            await db.delete(favorite)
        else:
            favorite.deleted_at = datetime.now(timezone.utc)
        
        await db.commit()
        return True
    
    @staticmethod
    async def check_favorite_status(
        db: AsyncSession,
        user_id: str,
        place_id: str
    ) -> bool:
        """
        Check if a place is favorited by a user.
        
        Args:
            db: Database session
            user_id: User ID
            place_id: Place identifier
            
        Returns:
            True if favorited, False otherwise
        """
        favorite = await FavoriteService.get_favorite(db, user_id, place_id)
        return favorite is not None
    
    @staticmethod
    async def bulk_check_favorite_status(
        db: AsyncSession,
        user_id: str,
        place_ids: List[str]
    ) -> Dict[str, bool]:
        """
        Check favorite status for multiple places at once.
        
        Efficient for list views where frontend needs to show
        favorite status for many places.
        
        Args:
            db: Database session
            user_id: User ID
            place_ids: List of place identifiers
            
        Returns:
            Dict mapping place_id to is_favorited status
        """
        if not place_ids:
            return {}
        
        # Query for existing favorites
        query = select(Favorite.place_id).where(
            Favorite.user_id == user_id,
            Favorite.place_id.in_(place_ids),
            Favorite.deleted_at.is_(None)
        )
        
        result = await db.execute(query)
        favorited_places = set(result.scalars().all())
        
        # Build response dict
        return {
            place_id: place_id in favorited_places
            for place_id in place_ids
        }
    
    @staticmethod
    async def toggle_favorite(
        db: AsyncSession,
        user_id: str,
        place_id: str,
        note: Optional[str] = None
    ) -> Tuple[bool, bool]:
        """
        Toggle favorite status for a place.
        
        Convenience method that favorites if not favorited,
        or unfavorites if already favorited.
        
        Args:
            db: Database session
            user_id: User ID
            place_id: Place identifier
            note: Note to add if favoriting
            
        Returns:
            Tuple of (is_now_favorited, was_changed)
        """
        existing = await FavoriteService.get_favorite(db, user_id, place_id)
        
        if existing:
            # Unfavorite
            await FavoriteService.remove_favorite(db, user_id, place_id)
            return False, True
        else:
            # Favorite
            data = FavoriteCreate(place_id=place_id, note=note)
            await FavoriteService.add_favorite(db, user_id, data)
            return True, True
    
    @staticmethod
    async def get_favorite_count(
        db: AsyncSession,
        user_id: str
    ) -> int:
        """
        Get total count of user's favorites.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of favorites
        """
        query = select(func.count()).select_from(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.deleted_at.is_(None)
        )
        
        result = await db.execute(query)
        return result.scalar() or 0


