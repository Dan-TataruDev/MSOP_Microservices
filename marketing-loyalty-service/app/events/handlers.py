"""
Event handlers for incoming events.
"""
import logging
from app.events.consumer import event_consumer

logger = logging.getLogger(__name__)


async def handle_booking_completed(payload: dict) -> None:
    """
    Handle booking completion - award loyalty points.
    
    Note: Points calculation is done here, but the actual
    booking amount comes from the event payload.
    """
    logger.info(f"Handling booking.completed: {payload}")
    # TODO: Award points based on booking amount


async def handle_feedback_analyzed(payload: dict) -> None:
    """
    Handle sentiment analysis completion.
    
    Can trigger retention campaigns for negative sentiment.
    """
    logger.info(f"Handling feedback.analyzed: {payload}")
    # TODO: Check if guest needs retention offer


def register_handlers() -> None:
    """Register all event handlers."""
    event_consumer.register_handler("booking.completed", handle_booking_completed)
    event_consumer.register_handler("feedback.analyzed", handle_feedback_analyzed)
    logger.info("Event handlers registered")


