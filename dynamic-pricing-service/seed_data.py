"""
Seed script for dynamic-pricing-service.
Generates base prices and pricing rules.
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
from app.models.base_price import BasePrice, VenueType

Base.metadata.create_all(bind=engine)

VENUE_IDS = [str(uuid.uuid4()) for _ in range(20)]
VENUE_TYPES = list(VenueType)
PRODUCT_CATEGORIES = ["room", "table", "spa", "event_space", "amenity", "service"]


def generate_base_prices(db: Session, num_prices: int = 300):
    """Generate base price records."""
    print(f"Generating {num_prices} base prices...")
    
    prices = []
    for i in range(num_prices):
        venue_id = random.choice(VENUE_IDS)
        venue_type = random.choice(VENUE_TYPES)
        
        # Set base price based on venue type
        if venue_type == VenueType.HOTEL:
            base_price = Decimal(random.uniform(100.0, 500.0))
            price_type = "per_night"
        elif venue_type == VenueType.RESTAURANT:
            base_price = Decimal(random.uniform(50.0, 200.0))
            price_type = "per_person"
        elif venue_type == VenueType.CAFE:
            base_price = Decimal(random.uniform(20.0, 80.0))
            price_type = "per_person"
        else:
            base_price = Decimal(random.uniform(30.0, 300.0))
            price_type = "per_unit"
        
        min_price = base_price * Decimal("0.7")
        max_price = base_price * Decimal("2.0")
        
        price = BasePrice(
            venue_id=uuid.UUID(venue_id),
            venue_type=venue_type,
            venue_name=f"{venue_type.value.title()} Venue {random.randint(1, 100)}",
            product_id=uuid.uuid4() if random.random() > 0.5 else None,
            product_name=random.choice(["Standard Room", "Deluxe Room", "Suite", "Table", "Event Space"]) if random.random() > 0.5 else None,
            product_category=random.choice(PRODUCT_CATEGORIES) if random.random() > 0.5 else None,
            base_price=base_price,
            currency="USD",
            price_type=price_type,
            unit_description=f"{price_type.replace('_', ' ')}",
            min_price=min_price,
            max_price=max_price,
            tax_rate=Decimal("0.10"),
            tax_included=random.random() > 0.7,
            valid_from=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
            valid_until=datetime.utcnow() + timedelta(days=random.randint(30, 365)) if random.random() > 0.3 else None,
            is_active=random.random() > 0.1,  # 90% active
        )
        prices.append(price)
    
    db.bulk_save_objects(prices)
    db.commit()
    print(f"✓ Created {len(prices)} base prices")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding dynamic-pricing-service database...")
        print("=" * 60)
        
        generate_base_prices(db, num_prices=300)
        
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

