"""
Event consumer for feedback processing triggers.
"""
import logging
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumes events that trigger feedback processing.
    
    Listens for:
    - feedback.received: Triggers async sentiment analysis
    - booking.completed: Could trigger feedback request
    """
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        logger.info("EventConsumer initialized")
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register a handler for an event type."""
        self.handlers[event_type] = handler
        logger.info(f"Handler registered for: {event_type}")
    
    def process_message(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Process an incoming message."""
        handler = self.handlers.get(event_type)
        if handler:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Handler error for {event_type}: {e}")
        else:
            logger.warning(f"No handler for event type: {event_type}")
    
    def start(self) -> None:
        """Start consuming messages (called on startup)."""
        logger.info("Event consumer started")
        # TODO: Implement actual message broker consumption
        # connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
        # channel.basic_consume(queue=..., on_message_callback=self._on_message)


# Global event consumer instance
event_consumer = EventConsumer()


