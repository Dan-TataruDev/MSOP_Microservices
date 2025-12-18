"""
Event handlers for processing events from various services.

Each handler extracts relevant data from events and stores it
for later aggregation into metrics.
"""
import logging
from typing import Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.events.consumer import event_consumer
from app.models.events import IngestedEvent, EventSource
from app.services.aggregation_service import AggregationService

logger = logging.getLogger(__name__)


def _store_event(
    event_type: str,
    source: EventSource,
    payload: Dict[str, Any],
    event: Dict[str, Any]
) -> None:
    """Store event in database for later aggregation."""
    db = SessionLocal()
    try:
        # Extract event ID and timestamp
        event_id = event.get("event_id") or payload.get("id") or str(UUID(int=0))
        event_timestamp = event.get("timestamp")
        if event_timestamp:
            if isinstance(event_timestamp, str):
                event_timestamp = datetime.fromisoformat(event_timestamp.replace("Z", "+00:00"))
        else:
            event_timestamp = datetime.utcnow()
        
        # Check for duplicate (idempotency)
        existing = db.query(IngestedEvent).filter(
            IngestedEvent.event_id == event_id,
            IngestedEvent.source == source
        ).first()
        
        if existing:
            logger.debug(f"Duplicate event ignored: {event_id}")
            return
        
        # Store new event
        ingested = IngestedEvent(
            event_id=event_id,
            event_type=event_type,
            source=source,
            payload=payload,
            event_timestamp=event_timestamp,
        )
        db.add(ingested)
        db.commit()
        
        logger.debug(f"Stored event: {event_type} from {source.value}")
        
    except Exception as e:
        logger.error(f"Error storing event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def handle_booking_event(event_type: str, payload: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    Handle booking-related events.
    
    Events: booking.created, booking.confirmed, booking.cancelled, booking.completed
    """
    _store_event(event_type, EventSource.BOOKING, payload, event)
    
    # Quick metric updates for real-time dashboard
    if event_type == "booking.created":
        logger.info(f"Booking created: {payload.get('booking_reference')}")
    elif event_type == "booking.cancelled":
        logger.info(f"Booking cancelled: {payload.get('booking_reference')}")


def handle_payment_event(event_type: str, payload: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    Handle payment-related events.
    
    Events: payment.initiated, payment.completed, payment.failed, refund.processed
    """
    _store_event(event_type, EventSource.PAYMENT, payload, event)
    
    if event_type == "payment.completed":
        amount = payload.get("amount", 0)
        logger.info(f"Payment completed: ${amount}")


def handle_inventory_event(event_type: str, payload: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    Handle inventory-related events.
    
    Events: room.status_changed, table.reserved, inventory.updated
    """
    _store_event(event_type, EventSource.INVENTORY, payload, event)


def handle_feedback_event(event_type: str, payload: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    Handle feedback and sentiment events.
    
    Events: feedback.submitted, sentiment.analyzed
    """
    _store_event(event_type, EventSource.FEEDBACK, payload, event)
    
    if event_type == "feedback.submitted":
        rating = payload.get("rating")
        logger.info(f"Feedback received: rating={rating}")


def handle_loyalty_event(event_type: str, payload: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    Handle loyalty program events.
    
    Events: loyalty.points_earned, loyalty.tier_changed, loyalty.redemption
    """
    _store_event(event_type, EventSource.LOYALTY, payload, event)


def handle_housekeeping_event(event_type: str, payload: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    Handle housekeeping and maintenance events.
    
    Events: task.created, task.completed, maintenance.reported, maintenance.resolved
    """
    _store_event(event_type, EventSource.HOUSEKEEPING, payload, event)


def handle_pricing_event(event_type: str, payload: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    Handle dynamic pricing events.
    
    Events: price.updated, rate.optimized
    """
    _store_event(event_type, EventSource.PRICING, payload, event)


def register_handlers() -> None:
    """Register all event handlers."""
    # Booking events
    event_consumer.register_handler("booking.*", handle_booking_event)
    
    # Payment events
    event_consumer.register_handler("payment.*", handle_payment_event)
    event_consumer.register_handler("refund.*", handle_payment_event)
    
    # Inventory events
    event_consumer.register_handler("room.*", handle_inventory_event)
    event_consumer.register_handler("table.*", handle_inventory_event)
    event_consumer.register_handler("inventory.*", handle_inventory_event)
    
    # Feedback events
    event_consumer.register_handler("feedback.*", handle_feedback_event)
    event_consumer.register_handler("sentiment.*", handle_feedback_event)
    
    # Loyalty events
    event_consumer.register_handler("loyalty.*", handle_loyalty_event)
    
    # Housekeeping events
    event_consumer.register_handler("task.*", handle_housekeeping_event)
    event_consumer.register_handler("maintenance.*", handle_housekeeping_event)
    
    # Pricing events
    event_consumer.register_handler("price.*", handle_pricing_event)
    event_consumer.register_handler("rate.*", handle_pricing_event)
    
    logger.info("All event handlers registered")
