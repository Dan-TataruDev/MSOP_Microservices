"""
Seed script for favorites-collections-service.
Generates favorites and collections with items.
Uses async sessions as this service uses async SQLAlchemy.
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine, Base
from app.models.favorite import Favorite
from app.models.collection import Collection, generate_public_id
from app.models.collection_item import CollectionItem

USER_IDS = [f"user_{uuid.uuid4()}" for _ in range(300)]
PLACE_IDS = [f"place_{uuid.uuid4()}" for _ in range(500)]

COLLECTION_NAMES = [
    "Summer Trip Ideas", "Date Night Spots", "Business Lunch Venues",
    "Family Friendly", "Romantic Getaways", "Weekend Escapes",
    "Budget Options", "Luxury Experiences", "Hidden Gems",
    "Beach Destinations", "Mountain Retreats", "City Breaks",
    "Foodie Adventures", "Spa & Wellness", "Adventure Travel",
]


async def generate_favorites(db: AsyncSession, num_favorites: int = 2000):
    """Generate favorite records."""
    print(f"Generating {num_favorites} favorites...")
    
    favorites = []
    # Ensure each user-place combination is unique
    used_combinations = set()
    
    for i in range(num_favorites):
        user_id = random.choice(USER_IDS)
        place_id = random.choice(PLACE_IDS)
        
        # Check if this combination already exists
        while (user_id, place_id) in used_combinations:
            place_id = random.choice(PLACE_IDS)
        
        used_combinations.add((user_id, place_id))
        
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
        deleted_at = None if random.random() > 0.1 else created_at + timedelta(days=random.randint(1, 30))
        
        favorite = Favorite(
            user_id=user_id,
            place_id=place_id,
            created_at=created_at,
            deleted_at=deleted_at,
            note=random.choice([None, "Great place!", "Want to visit", "Recommended by friend", "Perfect for dates"]),
        )
        favorites.append(favorite)
    
    db.add_all(favorites)
    await db.commit()
    print(f"✓ Created {len(favorites)} favorites")


async def generate_collections(db: AsyncSession, num_collections: int = 500):
    """Generate collection records with items."""
    print(f"Generating {num_collections} collections...")
    
    collections = []
    for i in range(num_collections):
        user_id = random.choice(USER_IDS)
        name = random.choice(COLLECTION_NAMES) if i < len(COLLECTION_NAMES) else f"Collection {i+1}"
        
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
        deleted_at = None if random.random() > 0.05 else created_at + timedelta(days=random.randint(1, 30))
        
        collection = Collection(
            user_id=user_id,
            public_id=generate_public_id(),
            name=name,
            description=random.choice([
                None,
                f"A curated list of {name.lower()}",
                "My personal favorites",
                "Places I want to visit",
            ]),
            cover_image_url=random.choice([
                None,
                f"https://example.com/images/{random.randint(1, 100)}.jpg",
            ]),
            is_public=random.random() > 0.7,  # 30% public
            created_at=created_at,
            deleted_at=deleted_at,
        )
        collections.append(collection)
    
    db.add_all(collections)
    await db.commit()
    print(f"✓ Created {len(collections)} collections")
    
    # Generate collection items
    print("Generating collection items...")
    items = []
    for collection in collections:
        if collection.deleted_at is None:  # Only add items to active collections
            num_items = random.randint(3, 20)
            used_place_ids = set()
            
            for position in range(num_items):
                place_id = random.choice(PLACE_IDS)
                # Ensure unique places per collection
                while place_id in used_place_ids:
                    place_id = random.choice(PLACE_IDS)
                used_place_ids.add(place_id)
                
                added_at = collection.created_at + timedelta(days=random.randint(0, 30))
                deleted_at = None if random.random() > 0.1 else added_at + timedelta(days=random.randint(1, 10))
                
                item = CollectionItem(
                    collection_id=collection.id,
                    place_id=place_id,
                    position=position,
                    note=random.choice([None, "Must visit", "Highly rated", "Great reviews"]),
                    added_at=added_at,
                    deleted_at=deleted_at,
                )
                items.append(item)
    
    db.add_all(items)
    await db.commit()
    print(f"✓ Created {len(items)} collection items")


async def main():
    """Main function to seed the database."""
    # Create tables first
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        try:
            print("=" * 60)
            print("Seeding favorites-collections-service database...")
            print("=" * 60)
            
            await generate_favorites(db, num_favorites=2000)
            await generate_collections(db, num_collections=500)
            
            print("=" * 60)
            print("✓ Database seeding completed successfully!")
            print("=" * 60)
        except Exception as e:
            print(f"✗ Error seeding database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())

