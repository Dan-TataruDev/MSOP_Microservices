"""
Event handlers for feedback processing.
"""
import logging
from typing import Dict, Any
from app.events.consumer import event_consumer
from app.database import SessionLocal
from app.services.sentiment_service import SentimentService

logger = logging.getLogger(__name__)


def handle_feedback_received(payload: Dict[str, Any]) -> None:
    """
    Handle feedback.received event - triggers async analysis.
    
    This handler is called when new feedback is submitted.
    In production, this would be processed by a background worker.
    """
    feedback_id = payload.get("feedback_id")
    logger.info(f"Processing feedback.received for: {feedback_id}")
    
    # In production: Queue for batch processing or process immediately based on load
    # For now, just log - actual processing done by batch scheduler


def handle_analysis_batch_trigger(payload: Dict[str, Any]) -> None:
    """
    Handle batch processing trigger.
    
    Called by scheduler to process pending feedback items.
    """
    db = SessionLocal()
    try:
        service = SentimentService(db)
        processed = service.process_batch()
        logger.info(f"Batch processing completed: {processed} items")
    finally:
        db.close()


def register_handlers() -> None:
    """Register all event handlers."""
    event_consumer.register_handler("feedback.received", handle_feedback_received)
    event_consumer.register_handler("analysis.batch.trigger", handle_analysis_batch_trigger)
    logger.info("Event handlers registered")


