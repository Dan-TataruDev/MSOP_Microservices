"""
Seed script for bi-analytics-service.
Generates events, metrics, and reports.
"""
import sys
import os
from datetime import datetime, timedelta
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.events import IngestedEvent, EventSource, EventProcessingCheckpoint
from app.models.metrics import MetricSnapshot, RealtimeMetric, MetricType, Granularity

Base.metadata.create_all(bind=engine)

EVENT_TYPES = [
    ("booking.created", "booking"),
    ("booking.confirmed", "booking"),
    ("booking.cancelled", "booking"),
    ("payment.completed", "payment"),
    ("payment.failed", "payment"),
    ("inventory.low_stock", "inventory"),
    ("feedback.submitted", "feedback"),
    ("loyalty.points_earned", "loyalty"),
    ("housekeeping.task_completed", "housekeeping"),
    ("pricing.updated", "pricing"),
    ("guest.registered", "guest"),
]


def generate_events(db: Session, num_events: int = 10000):
    """Generate ingested event records."""
    print(f"Generating {num_events} events...")
    
    # Check existing event_id+source combinations to avoid duplicates
    existing_combos = set()
    for row in db.query(IngestedEvent.event_id, IngestedEvent.source).all():
        existing_combos.add((row[0], row[1]))
    
    used_combos = set(existing_combos)
    
    events = []
    for i in range(num_events):
        event_type, source_name = random.choice(EVENT_TYPES)
        source = EventSource[source_name.upper()] if hasattr(EventSource, source_name.upper()) else EventSource.BOOKING
        
        # Generate unique event_id for this source
        while True:
            event_id = f"EVT{random.randint(100000, 999999)}"
            if (event_id, source) not in used_combos:
                used_combos.add((event_id, source))
                break
        
        event_timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 180))
        ingested_at = event_timestamp + timedelta(minutes=random.randint(0, 60))
        processed = random.random() > 0.1  # 90% processed
        processed_at = ingested_at + timedelta(minutes=random.randint(1, 30)) if processed else None
        
        payload = {
            "event_id": str(uuid.uuid4()),
            "timestamp": event_timestamp.isoformat(),
            "data": {
                "booking_id": str(uuid.uuid4()) if "booking" in event_type else None,
                "guest_id": str(uuid.uuid4()),
                "venue_id": str(uuid.uuid4()),
                "amount": random.uniform(50.0, 1000.0) if "payment" in event_type else None,
                "status": random.choice(["completed", "pending", "failed"]),
            }
        }
        
        event = IngestedEvent(
            event_id=event_id,
            event_type=event_type,
            source=source,
            payload=payload,
            event_timestamp=event_timestamp,
            ingested_at=ingested_at,
            processed=processed,
            processed_at=processed_at,
        )
        events.append(event)
    
    db.bulk_save_objects(events)
    db.commit()
    print(f"✓ Created {len(events)} events")
    
    # Generate processing checkpoints
    print("Generating processing checkpoints...")
    checkpoints = []
    for source in EventSource:
        checkpoint = EventProcessingCheckpoint(
            source=source,
            last_event_id=f"EVT{random.randint(100000, 999999)}",
            last_event_timestamp=datetime.utcnow() - timedelta(minutes=random.randint(0, 60)),
            events_processed_total=random.randint(1000, 100000),
            events_processed_today=random.randint(0, 1000),
            last_successful_run=datetime.utcnow() - timedelta(minutes=random.randint(0, 60)),
            consecutive_errors=0 if random.random() > 0.1 else random.randint(1, 5),
        )
        checkpoints.append(checkpoint)
    
    db.bulk_save_objects(checkpoints)
    db.commit()
    print(f"✓ Created {len(checkpoints)} processing checkpoints")


def generate_metrics(db: Session):
    """Generate metric snapshot and realtime metric records."""
    print("Generating metric snapshots...")
    
    snapshots = []
    metric_types = list(MetricType)
    granularities = list(Granularity)
    
    # Generate snapshots for the last 90 days
    for day_offset in range(90):
        period_start = datetime.utcnow() - timedelta(days=day_offset)
        
        # Daily snapshots
        for metric_type in metric_types[:10]:  # First 10 metric types
            period_end = period_start + timedelta(days=1)
            
            # Generate realistic values based on metric type
            if "revenue" in metric_type.value:
                value = random.uniform(10000.0, 100000.0)
            elif "rate" in metric_type.value or "percentage" in metric_type.value:
                value = random.uniform(0.0, 1.0)
            elif "count" in metric_type.value or "total" in metric_type.value:
                value = random.uniform(100.0, 1000.0)
            else:
                value = random.uniform(10.0, 500.0)
            
            snapshot = MetricSnapshot(
                metric_type=metric_type,
                granularity=Granularity.DAILY,
                period_start=period_start,
                period_end=period_end,
                value=value,
                count=random.randint(50, 500),
                min_value=value * 0.8,
                max_value=value * 1.2,
                dimensions={"venue_type": random.choice(["hotel", "restaurant", "cafe"])},
                computed_at=period_end + timedelta(hours=1),
                data_freshness=period_end,
            )
            snapshots.append(snapshot)
        
        # Weekly snapshots (every 7 days)
        if day_offset % 7 == 0:
            for metric_type in metric_types[:5]:
                period_end = period_start + timedelta(days=7)
                value = random.uniform(50000.0, 500000.0)
                
                snapshot = MetricSnapshot(
                    metric_type=metric_type,
                    granularity=Granularity.WEEKLY,
                    period_start=period_start,
                    period_end=period_end,
                    value=value,
                    count=random.randint(500, 5000),
                    min_value=value * 0.7,
                    max_value=value * 1.3,
                    computed_at=period_end + timedelta(hours=2),
                    data_freshness=period_end,
                )
                snapshots.append(snapshot)
        
        # Monthly snapshots (every 30 days)
        if day_offset % 30 == 0:
            for metric_type in metric_types[:5]:
                period_end = period_start + timedelta(days=30)
                value = random.uniform(200000.0, 2000000.0)
                
                snapshot = MetricSnapshot(
                    metric_type=metric_type,
                    granularity=Granularity.MONTHLY,
                    period_start=period_start,
                    period_end=period_end,
                    value=value,
                    count=random.randint(2000, 20000),
                    min_value=value * 0.6,
                    max_value=value * 1.4,
                    computed_at=period_end + timedelta(hours=3),
                    data_freshness=period_end,
                )
                snapshots.append(snapshot)
    
    db.bulk_save_objects(snapshots)
    db.commit()
    print(f"✓ Created {len(snapshots)} metric snapshots")
    
    # Generate realtime metrics
    print("Generating realtime metrics...")
    realtime_metrics = []
    for metric_type in metric_types[:15]:  # First 15 metric types
        if "revenue" in metric_type.value:
            value = random.uniform(10000.0, 100000.0)
        elif "rate" in metric_type.value or "percentage" in metric_type.value:
            value = random.uniform(0.0, 1.0)
        else:
            value = random.uniform(100.0, 1000.0)
        
        previous_value = value * random.uniform(0.9, 1.1)
        change_percent = ((value - previous_value) / previous_value) * 100 if previous_value > 0 else 0
        trend = "up" if change_percent > 0 else "down" if change_percent < 0 else "stable"
        
        metric = RealtimeMetric(
            metric_type=metric_type,
            value=value,
            previous_value=previous_value,
            change_percent=change_percent,
            trend=trend,
            updated_at=datetime.utcnow() - timedelta(minutes=random.randint(0, 60)),
        )
        realtime_metrics.append(metric)
    
    db.bulk_save_objects(realtime_metrics)
    db.commit()
    print(f"✓ Created {len(realtime_metrics)} realtime metrics")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding bi-analytics-service database...")
        print("=" * 60)
        
        generate_events(db, num_events=10000)
        generate_metrics(db)
        
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

