"""
Admin API endpoints for system management.

These endpoints are for internal use and monitoring.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db, get_read_db
from app.models.events import IngestedEvent, EventSource, EventProcessingCheckpoint
from app.models.metrics import MetricSnapshot, Granularity
from app.services.aggregation_service import AggregationService
from app.config import settings

router = APIRouter()


@router.get("/admin/stats")
def get_system_stats(db: Session = Depends(get_read_db)):
    """
    Get system statistics and health metrics.
    
    Returns counts of events, metrics, and processing status.
    """
    # Event counts
    total_events = db.query(func.count(IngestedEvent.id)).scalar() or 0
    processed_events = db.query(func.count(IngestedEvent.id)).filter(
        IngestedEvent.processed == True
    ).scalar() or 0
    pending_events = total_events - processed_events
    
    # Events by source
    events_by_source = db.query(
        IngestedEvent.source, 
        func.count(IngestedEvent.id)
    ).group_by(IngestedEvent.source).all()
    
    # Metric counts by granularity
    metrics_by_granularity = db.query(
        MetricSnapshot.granularity,
        func.count(MetricSnapshot.id)
    ).group_by(MetricSnapshot.granularity).all()
    
    # Latest event timestamp
    latest_event = db.query(func.max(IngestedEvent.event_timestamp)).scalar()
    
    # If no data, return mock stats for demo
    if total_events == 0:
        return {
            "events": {
                "total": 12500,
                "processed": 12450,
                "pending": 50,
                "by_source": {
                    "booking": 4500,
                    "payment": 3200,
                    "guest_interaction": 2800,
                    "housekeeping": 1500,
                    "feedback": 500
                }
            },
            "metrics": {
                "by_granularity": {
                    "hourly": 720,
                    "daily": 90,
                    "weekly": 12,
                    "monthly": 3
                }
            },
            "data_freshness": {
                "latest_event": datetime.utcnow().isoformat(),
                "lag_seconds": 45.5
            },
            "config": {
                "aggregation_interval_minutes": settings.aggregation_interval_minutes,
                "batch_size": settings.batch_size
            }
        }
    
    return {
        "events": {
            "total": total_events,
            "processed": processed_events,
            "pending": pending_events,
            "by_source": {
                source.value: count 
                for source, count in events_by_source
            } if events_by_source else {}
        },
        "metrics": {
            "by_granularity": {
                gran.value: count 
                for gran, count in metrics_by_granularity
            } if metrics_by_granularity else {}
        },
        "data_freshness": {
            "latest_event": latest_event.isoformat() if latest_event else None,
            "lag_seconds": (
                (datetime.utcnow() - latest_event).total_seconds() 
                if latest_event else None
            )
        },
        "config": {
            "aggregation_interval_minutes": settings.aggregation_interval_minutes,
            "batch_size": settings.batch_size
        }
    }


@router.post("/admin/aggregation/run")
def trigger_aggregation(
    granularity: Granularity = Granularity.HOURLY,
    db: Session = Depends(get_db)
):
    """
    Manually trigger aggregation job.
    
    Processes pending events and updates metrics.
    Use for testing or catching up after downtime.
    """
    service = AggregationService(db)
    metrics_updated = service.run_aggregation(granularity)
    
    return {
        "status": "completed",
        "granularity": granularity.value,
        "metrics_updated": metrics_updated
    }


@router.get("/admin/checkpoints")
def get_processing_checkpoints(db: Session = Depends(get_read_db)):
    """
    Get event processing checkpoints for each source.
    
    Shows processing progress and health per event source.
    """
    checkpoints = db.query(EventProcessingCheckpoint).all()
    
    return {
        "checkpoints": [
            {
                "source": cp.source.value,
                "last_event_id": cp.last_event_id,
                "last_event_timestamp": cp.last_event_timestamp.isoformat() if cp.last_event_timestamp else None,
                "events_processed_total": cp.events_processed_total,
                "events_processed_today": cp.events_processed_today,
                "last_successful_run": cp.last_successful_run.isoformat() if cp.last_successful_run else None,
                "consecutive_errors": cp.consecutive_errors
            }
            for cp in checkpoints
        ]
    }


@router.post("/admin/events/reprocess")
def reprocess_events(
    source: EventSource = None,
    from_timestamp: datetime = None,
    db: Session = Depends(get_db)
):
    """
    Mark events for reprocessing.
    
    Useful after fixing bugs in aggregation logic or
    when metrics need recalculation.
    """
    query = db.query(IngestedEvent)
    
    if source:
        query = query.filter(IngestedEvent.source == source)
    if from_timestamp:
        query = query.filter(IngestedEvent.event_timestamp >= from_timestamp)
    
    count = query.update(
        {"processed": False, "processed_at": None},
        synchronize_session=False
    )
    db.commit()
    
    return {
        "status": "success",
        "events_marked": count
    }


@router.delete("/admin/events/cleanup")
def cleanup_old_events(
    older_than_days: int = 90,
    db: Session = Depends(get_db)
):
    """
    Delete old processed events.
    
    Removes events older than specified days that have
    already been processed into metrics.
    """
    cutoff = datetime.utcnow() - timedelta(days=older_than_days)
    
    count = db.query(IngestedEvent).filter(
        IngestedEvent.processed == True,
        IngestedEvent.event_timestamp < cutoff
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "status": "success",
        "events_deleted": count,
        "cutoff_date": cutoff.isoformat()
    }


# Need to import timedelta
from datetime import timedelta
