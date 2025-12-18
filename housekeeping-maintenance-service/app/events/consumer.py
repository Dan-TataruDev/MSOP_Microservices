"""
Event consumer for booking and inventory events.

This service subscribes to events from other services to trigger operational tasks.
It maintains loose coupling by:
1. Only consuming events - no direct API calls to other services
2. Storing only reference IDs - no duplication of external data
3. Using event schemas as contracts - independent of source implementations
"""
import json
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumes events from booking, inventory, and guest interaction services.
    
    Event Sources:
    - Booking Service: checkout events trigger cleaning tasks
    - Inventory Service: low stock alerts trigger restocking tasks
    - Guest Interaction Service: guest complaints may trigger maintenance
    
    Architecture Notes:
    - Events are consumed via RabbitMQ message broker
    - Each event type has a dedicated handler
    - Failed events are sent to dead-letter queue for retry
    - Event processing is idempotent (handles duplicates)
    """
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        self.queue_prefix = settings.rabbitmq_queue_prefix
        self.handlers: Dict[str, Callable] = {}
        self._processed_events: set = set()  # For deduplication
        logger.info(f"EventConsumer initialized with exchange: {self.exchange}")
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: The event type to handle (e.g., "booking.completed")
            handler: Async callable that processes the event payload
        """
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event: {event_type}")
    
    def _is_duplicate(self, event_id: str) -> bool:
        """Check if event was already processed (idempotency)."""
        if event_id in self._processed_events:
            return True
        # In production, check against persistent storage
        return False
    
    def _mark_processed(self, event_id: str) -> None:
        """Mark event as processed."""
        self._processed_events.add(event_id)
        # In production, persist to database
    
    async def handle_event(self, event_type: str, payload: Dict[str, Any], 
                          event_id: Optional[str] = None) -> bool:
        """
        Process an incoming event.
        
        Args:
            event_type: Type of the event
            payload: Event data
            event_id: Unique event identifier for deduplication
            
        Returns:
            True if event was processed, False if skipped or failed
        """
        # Deduplication check
        if event_id and self._is_duplicate(event_id):
            logger.info(f"Skipping duplicate event: {event_id}")
            return False
        
        if event_type not in self.handlers:
            logger.warning(f"No handler registered for event: {event_type}")
            return False
        
        try:
            await self.handlers[event_type](payload)
            if event_id:
                self._mark_processed(event_id)
            logger.info(f"Successfully processed event: {event_type}")
            return True
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {str(e)}", exc_info=True)
            # In production, send to dead-letter queue
            return False
    
    async def start_consuming(self) -> None:
        """
        Start consuming events from message broker.
        
        Subscribes to the following event types:
        - booking.completed: Guest checked out -> trigger checkout cleaning
        - booking.confirmed: New booking -> prepare room schedule
        - booking.cancelled: Booking cancelled -> adjust cleaning schedule
        - inventory.low_stock: Stock below threshold -> trigger restocking
        - inventory.critical_stock: Critical level -> urgent restocking
        - resource.room_status_changed: Room status update -> sync state
        - guest.complaint_filed: Guest complaint -> potential maintenance
        """
        logger.info("Starting event consumer...")
        
        # Define event subscriptions
        subscriptions = [
            # Booking events
            f"{settings.event_topic_booking}.booking.completed",
            f"{settings.event_topic_booking}.booking.confirmed",
            f"{settings.event_topic_booking}.booking.cancelled",
            f"{settings.event_topic_booking}.booking.checked_in",
            
            # Inventory events
            f"{settings.event_topic_inventory}.inventory.low_stock",
            f"{settings.event_topic_inventory}.inventory.critical_stock",
            f"{settings.event_topic_inventory}.resource.room_status_changed",
            
            # Guest interaction events
            "guest.complaint_filed",
            "guest.maintenance_requested",
        ]
        
        logger.info(f"Subscribing to events: {subscriptions}")
        
        # TODO: Implement actual RabbitMQ consumer
        # In production:
        # connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        # channel = await connection.channel()
        # exchange = await channel.declare_exchange(self.exchange, aio_pika.ExchangeType.TOPIC)
        # queue = await channel.declare_queue(f"{self.queue_prefix}_events", durable=True)
        # for routing_key in subscriptions:
        #     await queue.bind(exchange, routing_key=routing_key)
        # await queue.consume(self._on_message)
    
    async def _on_message(self, message) -> None:
        """
        Process incoming message from broker.
        
        Message format:
        {
            "event_id": "uuid",
            "event_type": "booking.completed",
            "payload": {...},
            "timestamp": "ISO8601",
            "source": "booking-service",
            "version": "1.0"
        }
        """
        try:
            body = json.loads(message.body.decode())
            event_id = body.get("event_id")
            event_type = body.get("event_type")
            payload = body.get("payload", {})
            
            success = await self.handle_event(event_type, payload, event_id)
            
            if success:
                await message.ack()
            else:
                # Requeue for retry or send to DLQ
                await message.nack(requeue=True)
                
        except json.JSONDecodeError:
            logger.error("Failed to decode message body")
            await message.reject()
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            await message.nack(requeue=True)


# Global consumer instance
event_consumer = EventConsumer()
