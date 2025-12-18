"""Event consumer for booking, housekeeping, and supplier events."""
import logging
from typing import Dict, Any, Callable
from app.config import settings

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes events from booking, housekeeping, and supplier services."""
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        self.handlers: Dict[str, Callable] = {}
        logger.info(f"EventConsumer initialized with exchange: {self.exchange}")
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event: {event_type}")
    
    def handle_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Process incoming event."""
        if event_type in self.handlers:
            try:
                self.handlers[event_type](payload)
            except Exception as e:
                logger.error(f"Error handling event {event_type}: {str(e)}", exc_info=True)
        else:
            logger.warning(f"No handler registered for event: {event_type}")
    
    def start_consuming(self) -> None:
        """Start consuming events from message broker."""
        logger.info("Starting event consumer (placeholder - not connected to broker)")
        # TODO: Implement actual message broker consumer


event_consumer = EventConsumer()


