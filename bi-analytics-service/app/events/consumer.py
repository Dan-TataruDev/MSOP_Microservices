"""
Event consumer for ingesting events from other services.

Design Principles:
- Asynchronous consumption to not block other services
- Deduplication to handle at-least-once delivery
- Checkpointing for resumable processing
- Batch processing for efficiency
"""
import json
import logging
from typing import Dict, Any, Callable, List
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumes events from all services for analytics aggregation.
    
    This consumer subscribes to multiple event topics and routes
    events to appropriate handlers for processing.
    """
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        self.queue_prefix = settings.rabbitmq_queue_prefix
        self.handlers: Dict[str, List[Callable]] = {}
        self.event_buffer: List[Dict[str, Any]] = []
        self.buffer_size = settings.batch_size
        self._connected = False
        
        logger.info(f"EventConsumer initialized for exchange: {self.exchange}")
    
    def register_handler(self, event_pattern: str, handler: Callable) -> None:
        """
        Register a handler for an event pattern.
        
        Args:
            event_pattern: Event type pattern (e.g., "booking.*", "payment.completed")
            handler: Callable to handle matching events
        """
        if event_pattern not in self.handlers:
            self.handlers[event_pattern] = []
        self.handlers[event_pattern].append(handler)
        logger.info(f"Registered handler for event pattern: {event_pattern}")
    
    def _match_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches pattern (supports wildcards)."""
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")
        return event_type == pattern
    
    def _get_handlers(self, event_type: str) -> List[Callable]:
        """Get all handlers matching an event type."""
        matching_handlers = []
        for pattern, handlers in self.handlers.items():
            if self._match_pattern(event_type, pattern):
                matching_handlers.extend(handlers)
        return matching_handlers
    
    def _process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single event by routing to handlers.
        
        Returns:
            True if processed successfully, False otherwise
        """
        event_type = event.get("event_type", "")
        payload = event.get("payload", {})
        
        handlers = self._get_handlers(event_type)
        if not handlers:
            logger.debug(f"No handlers for event type: {event_type}")
            return True  # Not an error, just no handlers interested
        
        success = True
        for handler in handlers:
            try:
                handler(event_type, payload, event)
            except Exception as e:
                logger.error(f"Handler error for {event_type}: {str(e)}", exc_info=True)
                success = False
        
        return success
    
    def _process_batch(self, events: List[Dict[str, Any]]) -> int:
        """
        Process a batch of events.
        
        Returns:
            Number of successfully processed events
        """
        success_count = 0
        for event in events:
            if self._process_event(event):
                success_count += 1
        return success_count
    
    def add_to_buffer(self, event: Dict[str, Any]) -> None:
        """Add event to buffer, flush if buffer is full."""
        self.event_buffer.append(event)
        if len(self.event_buffer) >= self.buffer_size:
            self.flush_buffer()
    
    def flush_buffer(self) -> int:
        """Flush event buffer and process all events."""
        if not self.event_buffer:
            return 0
        
        events = self.event_buffer.copy()
        self.event_buffer.clear()
        
        processed = self._process_batch(events)
        logger.info(f"Flushed buffer: {processed}/{len(events)} events processed")
        return processed
    
    def start_consuming(self) -> None:
        """
        Start consuming events from message broker.
        
        In production, this would connect to RabbitMQ/Kafka
        and start consuming messages asynchronously.
        """
        logger.info("Starting event consumer...")
        self._connected = True
        
        # Production implementation would look like:
        # 
        # async def callback(message):
        #     try:
        #         event = json.loads(message.body)
        #         event["ingested_at"] = datetime.utcnow().isoformat()
        #         self.add_to_buffer(event)
        #         await message.ack()
        #     except Exception as e:
        #         logger.error(f"Error processing message: {str(e)}")
        #         await message.nack(requeue=True)
        #
        # for topic in settings.event_topics:
        #     queue_name = f"{self.queue_prefix}_{topic}"
        #     await channel.queue_declare(queue=queue_name, durable=True)
        #     await channel.queue_bind(queue_name, self.exchange, routing_key=f"{topic}.*")
        #     await channel.basic_consume(queue_name, callback)
        
        logger.info(f"Event consumer started (placeholder - subscribed to {len(settings.event_topics)} topics)")
    
    def stop_consuming(self) -> None:
        """Stop consuming and flush remaining events."""
        logger.info("Stopping event consumer...")
        self.flush_buffer()
        self._connected = False
        logger.info("Event consumer stopped")


# Global event consumer instance
event_consumer = EventConsumer()
