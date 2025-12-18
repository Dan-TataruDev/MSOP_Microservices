"""
Seed script for guest-interaction-service.
Generates guests, interactions, preferences, and identity mappings.
"""
import sys
import os
from datetime import datetime, timedelta
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.guest import Guest, GuestIdentityMapping
from app.models.interaction import Interaction, InteractionType

Base.metadata.create_all(bind=engine)

FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Maria"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
INTERACTION_TYPES = [
    ("view", "venue_view"),
    ("view", "room_view"),
    ("search", "venue_search"),
    ("booking", "booking_created"),
    ("booking", "booking_confirmed"),
    ("order", "order_placed"),
    ("feedback", "feedback_submitted"),
    ("marketing", "email_opened"),
    ("marketing", "promotion_viewed"),
]


def generate_guests(db: Session, num_guests: int = 500):
    """Generate guest records."""
    print(f"Generating {num_guests} guests...")
    
    # First create interaction types (check if they exist first)
    interaction_type_objs = []
    existing_types = {it.name: it for it in db.query(InteractionType).all()}
    
    for category, name in INTERACTION_TYPES:
        if name not in existing_types:
            it = InteractionType(
                name=name,
                description=f"{category} interaction: {name}",
                category=category,
                is_system=True,
            )
            interaction_type_objs.append(it)
        else:
            interaction_type_objs.append(existing_types[name])
    
    if interaction_type_objs:
        new_types = [it for it in interaction_type_objs if it.id is None]
        if new_types:
            db.bulk_save_objects(new_types)
            db.commit()
            print(f"✓ Created {len(new_types)} new interaction types")
        print(f"✓ Using {len(interaction_type_objs)} interaction types (existing + new)")
    
    guests = []
    for i in range(num_guests):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 1000)}@example.com"
        
        guest = Guest(
            email=email,
            name=f"{first_name} {last_name}",
            phone=f"+1{random.randint(2000000000, 9999999999)}",
            status=random.choice(["active", "active", "active", "inactive"]),  # Mostly active
            is_anonymous=random.random() > 0.8,  # 20% anonymous
            consent_marketing=random.random() > 0.4,
            consent_analytics=random.random() > 0.2,
            consent_personalization=random.random() > 0.3,
            last_interaction_at=datetime.utcnow() - timedelta(days=random.randint(0, 90)),
        )
        guests.append(guest)
    
    db.bulk_save_objects(guests)
    db.commit()
    print(f"✓ Created {len(guests)} guests")
    
    # Generate identity mappings
    print("Generating identity mappings...")
    mappings = []
    for guest in guests:
        if not guest.is_anonymous:
            # Email mapping
            mappings.append(GuestIdentityMapping(
                guest_id=guest.id,
                identity_type="email",
                identity_value=guest.email,
                is_primary=True,
            ))
            
            # Session ID mapping
            for _ in range(random.randint(1, 3)):
                mappings.append(GuestIdentityMapping(
                    guest_id=guest.id,
                    identity_type="session_id",
                    identity_value=f"session_{uuid.uuid4()}",
                    is_primary=False,
                ))
            
            # Device ID mapping
            if random.random() > 0.5:
                mappings.append(GuestIdentityMapping(
                    guest_id=guest.id,
                    identity_type="device_id",
                    identity_value=f"device_{uuid.uuid4()}",
                    is_primary=False,
                ))
    
    db.bulk_save_objects(mappings)
    db.commit()
    print(f"✓ Created {len(mappings)} identity mappings")
    
    return guests, interaction_type_objs


def generate_interactions(db: Session, guests: list, interaction_types: list, num_interactions: int = 5000):
    """Generate interaction records."""
    print(f"Generating {num_interactions} interactions...")
    
    interactions = []
    entity_types = ["venue", "room", "table", "booking", "order", "product"]
    
    for i in range(num_interactions):
        guest = random.choice(guests)
        interaction_type = random.choice(interaction_types)
        entity_type = random.choice(entity_types)
        entity_id = str(uuid.uuid4())
        
        occurred_at = datetime.utcnow() - timedelta(days=random.randint(0, 180))
        
        interaction = Interaction(
            guest_id=guest.id,
            interaction_type_id=interaction_type.id,
            entity_type=entity_type,
            entity_id=entity_id,
            context={"search_query": random.choice(["hotel", "restaurant", "spa", "room"])} if interaction_type.category == "search" else None,
            interaction_metadata={
                "device": random.choice(["mobile", "desktop", "tablet"]),
                "browser": random.choice(["chrome", "safari", "firefox"]),
                "ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            },
            source=random.choice(["frontend", "booking_service", "mobile_app"]),
            occurred_at=occurred_at,
        )
        interactions.append(interaction)
    
    db.bulk_save_objects(interactions)
    db.commit()
    print(f"✓ Created {len(interactions)} interactions")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding guest-interaction-service database...")
        print("=" * 60)
        
        guests, interaction_types = generate_guests(db, num_guests=500)
        generate_interactions(db, guests, interaction_types, num_interactions=5000)
        
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

