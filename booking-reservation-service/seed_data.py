"""
Seed script for booking-reservation-service.
Generates a large amount of realistic booking data.
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.booking import Booking, BookingStatus, BookingStatusHistory, VenueType, IdempotencyKey

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Sample data
VENUE_IDS = [str(uuid.uuid4()) for _ in range(10)]
GUEST_IDS = [str(uuid.uuid4()) for _ in range(200)]
VENUE_NAMES = [
    "Grand Hotel Downtown", "Seaside Resort", "Mountain View Lodge", "City Center Hotel",
    "Riverside Inn", "Sunset Restaurant", "Ocean Breeze Cafe", "Garden Terrace",
    "Urban Eatery", "Luxury Suites", "Business Hotel", "Family Resort"
]
GUEST_NAMES = [
    "John Smith", "Jane Doe", "Michael Johnson", "Sarah Williams", "David Brown",
    "Emily Davis", "Robert Miller", "Lisa Anderson", "James Wilson", "Maria Garcia",
    "William Martinez", "Jennifer Taylor", "Richard Thomas", "Patricia Jackson",
    "Joseph White", "Linda Harris", "Thomas Martin", "Barbara Thompson"
]
STATUSES = list(BookingStatus)
VENUE_TYPES = list(VenueType)


def generate_booking_reference(used_refs: set):
    """Generate a unique booking reference."""
    while True:
        ref = f"BK{random.randint(100000, 999999)}"
        if ref not in used_refs:
            used_refs.add(ref)
            return ref


def generate_booking(db: Session, num_bookings: int = 1000):
    """Generate booking records."""
    print(f"Generating {num_bookings} bookings...")
    
    bookings = []
    for i in range(num_bookings):
        # Random dates in the past 6 months and future 6 months
        days_offset = random.randint(-180, 180)
        booking_date = datetime.utcnow() + timedelta(days=days_offset)
        
        # Booking time (for restaurants/cafes)
        if random.random() > 0.5:  # 50% chance it's a restaurant/cafe
            hour = random.randint(11, 22)
            minute = random.choice([0, 15, 30, 45])
            booking_time = booking_date.replace(hour=hour, minute=minute)
            duration_minutes = random.choice([60, 90, 120, 150])
            end_time = booking_time + timedelta(minutes=duration_minutes)
            venue_type = random.choice([VenueType.RESTAURANT, VenueType.CAFE])
        else:
            # Hotel booking
            booking_time = booking_date.replace(hour=15, minute=0)
            duration_minutes = None
            end_time = booking_date + timedelta(days=random.randint(1, 7))
            venue_type = VenueType.HOTEL
        
        status = random.choice(STATUSES)
        guest_id = random.choice(GUEST_IDS)
        venue_id = random.choice(VENUE_IDS)
        
        # Pricing
        base_price = Decimal(random.randint(50, 500))
        tax_amount = base_price * Decimal("0.10")
        discount_amount = Decimal(random.randint(0, 50)) if random.random() > 0.7 else Decimal(0)
        total_price = base_price + tax_amount - discount_amount
        
        # Timestamps based on status
        confirmed_at = booking_date + timedelta(minutes=random.randint(5, 30)) if status in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN, BookingStatus.COMPLETED] else None
        checked_in_at = booking_time + timedelta(minutes=random.randint(0, 30)) if status in [BookingStatus.CHECKED_IN, BookingStatus.COMPLETED] else None
        completed_at = end_time if status == BookingStatus.COMPLETED else None
        cancelled_at = booking_date + timedelta(hours=random.randint(1, 48)) if status == BookingStatus.CANCELLED else None
        expires_at = booking_date + timedelta(minutes=15) if status == BookingStatus.PENDING else None
        
        booking = Booking(
            booking_reference=generate_booking_reference(used_refs),
            guest_id=uuid.UUID(guest_id),
            guest_name=random.choice(GUEST_NAMES),
            guest_email=f"guest{random.randint(1, 1000)}@example.com",
            guest_phone=f"+1{random.randint(2000000000, 9999999999)}",
            venue_id=uuid.UUID(venue_id),
            venue_type=venue_type,
            venue_name=random.choice(VENUE_NAMES),
            booking_date=booking_date,
            booking_time=booking_time,
            duration_minutes=duration_minutes,
            end_time=end_time,
            party_size=random.randint(1, 8),
            status=status,
            base_price=base_price,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_price=total_price,
            currency="USD",
            payment_status="completed" if status in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN, BookingStatus.COMPLETED] else "pending",
            special_requests=random.choice([None, "Window seat please", "Quiet room", "Late checkout", "High chair needed"]),
            confirmed_at=confirmed_at,
            checked_in_at=checked_in_at,
            completed_at=completed_at,
            cancelled_at=cancelled_at,
            expires_at=expires_at,
            source=random.choice(["web", "mobile", "phone", "walk_in"]),
        )
        bookings.append(booking)
    
    db.bulk_save_objects(bookings)
    db.commit()
    print(f"✓ Created {len(bookings)} bookings")
    
    # Generate status history for some bookings
    print("Generating booking status history...")
    status_history_records = []
    for booking in bookings[:500]:  # Add history for first 500 bookings
        if booking.status != BookingStatus.PENDING:
            # Add initial pending status
            status_history_records.append(BookingStatusHistory(
                booking_id=booking.id,
                from_status=None,
                to_status=BookingStatus.PENDING,
                changed_by="system",
                reason="Booking created",
                created_at=booking.created_at
            ))
            
            # Add transition to current status
            if booking.status != BookingStatus.PENDING:
                status_history_records.append(BookingStatusHistory(
                    booking_id=booking.id,
                    from_status=BookingStatus.PENDING,
                    to_status=booking.status,
                    changed_by="guest" if booking.status == BookingStatus.CANCELLED else "system",
                    reason=random.choice(["Payment received", "Guest confirmed", "Auto-confirmed", "Guest cancelled"]),
                    created_at=booking.confirmed_at or booking.created_at + timedelta(minutes=10)
                ))
    
    db.bulk_save_objects(status_history_records)
    db.commit()
    print(f"✓ Created {len(status_history_records)} status history records")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding booking-reservation-service database...")
        print("=" * 60)
        
        generate_booking(db, num_bookings=2000)
        
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

