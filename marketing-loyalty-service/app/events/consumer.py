"""
Event consumer for incoming events.

Listens for events from other services to trigger marketing actions.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumes events from other services.
    
    Listens for:
    - booking.completed: Award loyalty points
    - feedback.analyzed: Update guest eligibility based on sentiment
    - payment.completed: Track spending for tier qualification
    """
    
    def __init__(self):
        self.handlers: Dict[str, callable] = {}
    
    def register_handler(self, event_type: str, handler: callable) -> None:
        """Register a handler for an event type."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for: {event_type}")
    
    async def handle_event(self, event: Dict[str, Any]) -> None:
        """Process an incoming event."""
        event_type = event.get("event_type")
        if event_type in self.handlers:
            await self.handlers[event_type](event.get("payload", {}))
        else:
            logger.debug(f"No handler for event type: {event_type}")


event_consumer = EventConsumer()


