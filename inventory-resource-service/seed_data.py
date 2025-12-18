"""
Seed script for inventory-resource-service.
Generates rooms, tables, and inventory items with transactions.
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.room import Room, RoomStatus, RoomType
from app.models.table import Table, TableStatus
from app.models.inventory import InventoryItem, StockTransaction, ItemCategory, TransactionType

Base.metadata.create_all(bind=engine)

VENUE_IDS = [str(uuid.uuid4()) for _ in range(10)]
ROOM_TYPES = list(RoomType)
TABLE_SECTIONS = ["main", "patio", "private", "window", "bar", "outdoor"]


def generate_rooms(db: Session, num_rooms: int = 500):
    """Generate room records."""
    print(f"Generating {num_rooms} rooms...")
    
    rooms = []
    for i in range(num_rooms):
        venue_id = random.choice(VENUE_IDS)
        floor = random.randint(1, 10)
        room_number = f"{floor}{random.randint(1, 50):02d}"
        
        room = Room(
            room_number=room_number,
            venue_id=uuid.UUID(venue_id),
            room_type=random.choice(ROOM_TYPES),
            status=random.choice(list(RoomStatus)),
            floor=floor,
            capacity=random.choice([2, 2, 2, 4, 4, 6, 8]),  # More 2-person rooms
            is_active=random.random() > 0.05,  # 95% active
        )
        rooms.append(room)
    
    db.bulk_save_objects(rooms)
    db.commit()
    print(f"✓ Created {len(rooms)} rooms")


def generate_tables(db: Session, num_tables: int = 300):
    """Generate table records."""
    print(f"Generating {num_tables} tables...")
    
    tables = []
    for i in range(num_tables):
        venue_id = random.choice(VENUE_IDS)
        table_number = f"T{random.randint(1, 100)}"
        
        table = Table(
            table_number=table_number,
            venue_id=uuid.UUID(venue_id),
            status=random.choice(list(TableStatus)),
            capacity=random.choice([2, 2, 4, 4, 4, 6, 8, 10]),
            min_capacity=1,
            section=random.choice(TABLE_SECTIONS),
            is_active=True,
        )
        tables.append(table)
    
    db.bulk_save_objects(tables)
    db.commit()
    print(f"✓ Created {len(tables)} tables")


def generate_inventory(db: Session, num_items: int = 200):
    """Generate inventory items and transactions."""
    print(f"Generating {num_items} inventory items...")
    
    items = []
    item_names = [
        "Towels", "Bed Sheets", "Pillows", "Toilet Paper", "Shampoo", "Soap",
        "Coffee", "Tea", "Sugar", "Milk", "Cleaning Supplies", "Trash Bags",
        "Light Bulbs", "Batteries", "First Aid Kit", "Fire Extinguisher",
        "Hand Sanitizer", "Face Masks", "Gloves", "Aprons", "Uniforms",
        "Dish Soap", "Sponges", "Paper Towels", "Napkins", "Cups", "Plates",
        "Cutlery", "Glassware", "Tablecloths", "Candles", "Flowers"
    ]
    
    for i in range(num_items):
        sku = f"SKU{random.randint(10000, 99999)}"
        name = random.choice(item_names)
        category = random.choice(list(ItemCategory))
        
        # Set appropriate quantities based on category
        if category in [ItemCategory.CONSUMABLE, ItemCategory.FOOD_BEVERAGE]:
            quantity = random.randint(50, 500)
            low_threshold = 50
            critical_threshold = 20
        else:
            quantity = random.randint(10, 100)
            low_threshold = 10
            critical_threshold = 5
        
        item = InventoryItem(
            sku=sku,
            name=name,
            description=f"Standard {name.lower()} for hospitality use",
            category=category,
            quantity=quantity,
            unit=random.choice(["units", "boxes", "packs", "liters", "kg"]),
            low_threshold=low_threshold,
            critical_threshold=critical_threshold,
            reorder_quantity=random.randint(50, 200),
            unit_cost=Decimal(random.uniform(1.0, 50.0)),
            venue_id=uuid.UUID(random.choice(VENUE_IDS)) if random.random() > 0.3 else None,
            storage_location=random.choice(["Main Storage", "Kitchen", "Housekeeping", "Basement", "Warehouse"]),
        )
        items.append(item)
    
    db.bulk_save_objects(items)
    db.commit()
    print(f"✓ Created {len(items)} inventory items")
    
    # Generate stock transactions
    print("Generating stock transactions...")
    transactions = []
    for item in items:
        # Initial restock
        transactions.append(StockTransaction(
            item_id=item.id,
            transaction_type=TransactionType.RESTOCK,
            quantity_change=item.quantity,
            quantity_after=item.quantity,
            reference_type="initial",
            notes="Initial stock",
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 180)),
        ))
        
        # Some usage transactions
        for _ in range(random.randint(5, 20)):
            usage_qty = random.randint(1, 20)
            new_quantity = max(0, item.quantity - usage_qty)
            transactions.append(StockTransaction(
                item_id=item.id,
                transaction_type=TransactionType.USAGE,
                quantity_change=-usage_qty,
                quantity_after=new_quantity,
                reference_type=random.choice(["booking", "housekeeping", "daily_use"]),
                notes=random.choice(["Daily usage", "Guest checkout", "Regular maintenance"]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            ))
            item.quantity = new_quantity
        
        # Some restocks
        for _ in range(random.randint(2, 5)):
            restock_qty = random.randint(20, 100)
            item.quantity += restock_qty
            transactions.append(StockTransaction(
                item_id=item.id,
                transaction_type=TransactionType.RESTOCK,
                quantity_change=restock_qty,
                quantity_after=item.quantity,
                reference_type="supplier",
                notes="Restocked from supplier",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            ))
    
    db.bulk_save_objects(transactions)
    db.commit()
    print(f"✓ Created {len(transactions)} stock transactions")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding inventory-resource-service database...")
        print("=" * 60)
        
        generate_rooms(db, num_rooms=500)
        generate_tables(db, num_tables=300)
        generate_inventory(db, num_items=200)
        
        print("=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

