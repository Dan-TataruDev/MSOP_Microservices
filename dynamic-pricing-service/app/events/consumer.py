"""
Event Consumer for the Dynamic Pricing Service.

Listens for events from other services:
- Booking Service: booking created/cancelled (to track price acceptance)
- Inventory Service: availability changes (to update demand data)
- Analytics Service: demand signals and forecasts
"""
import json
import logging
import threading
from typing import Callable, Dict, Any

import pika
from pika.exceptions import AMQPError

from app.config import settings

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumes events from RabbitMQ.
    
    Runs in a background thread to handle incoming events.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.handlers: Dict[str, Callable] = {}
        self._running = False
        self._thread = None
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for an event type."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event: {event_type}")
    
    def start(self):
        """Start consuming events in a background thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()
        logger.info("Event consumer started")
    
    def stop(self):
        """Stop consuming events."""
        self._running = False
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        logger.info("Event consumer stopped")
    
    def _consume(self):
        """Main consumer loop."""
        retry_count = 0
        max_retries = 10
        
        while self._running:
            try:
                self._setup_consumer()
                retry_count = 0  # Reset on successful connection
                logger.info("Successfully connected to RabbitMQ")
                self.channel.start_consuming()
            except (AMQPError, ConnectionError, OSError) as e:
                retry_count += 1
                if retry_count <= max_retries:
                    wait_time = min(5 * retry_count, 30)  # Exponential backoff, max 30s
                    logger.warning(
                        f"Failed to connect to RabbitMQ (attempt {retry_count}/{max_retries}): {e}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    if self._running:
                        import time
                        time.sleep(wait_time)
                else:
                    logger.error(
                        f"Max retries reached. RabbitMQ consumer will not start. "
                        f"Service will continue without event consumption. "
                        f"To fix: Start RabbitMQ with 'docker-compose up rabbitmq'"
                    )
                    # Wait longer before trying again (every 60 seconds)
                    if self._running:
                        import time
                        time.sleep(60)
                        retry_count = 0  # Reset to allow retry after long wait
            except Exception as e:
                logger.error(f"Unexpected error in consumer: {e}")
                if self._running:
                    import time
                    time.sleep(10)
    
    def _setup_consumer(self):
        """Set up the RabbitMQ consumer."""
        # Close existing connection if any
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
            except:
                pass
        
        params = pika.URLParameters(settings.rabbitmq_url)
        # Set connection timeout
        params.connection_attempts = 3
        params.retry_delay = 2
        
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        
        # Declare exchange
        self.channel.exchange_declare(
            exchange=settings.rabbitmq_exchange,
            exchange_type="topic",
            durable=True,
        )
        
        # Declare queue for this service
        queue_name = f"{settings.rabbitmq_queue_prefix}_events"
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        # Bind to relevant topics
        bindings = [
            f"{settings.event_topic_booking}.#",    # All booking events
            f"{settings.event_topic_inventory}.#",  # All inventory events
            "analytics.demand.#",                    # Demand analytics
        ]
        
        for binding in bindings:
            self.channel.queue_bind(
                exchange=settings.rabbitmq_exchange,
                queue=queue_name,
                routing_key=binding,
            )
        
        # Set up consumer
        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._handle_message,
        )
        
        logger.info(f"Consumer set up on queue: {queue_name}")
    
    def _handle_message(self, channel, method, properties, body):
        """Handle incoming message."""
        try:
            message = json.loads(body)
            event_type = message.get("event_type")
            data = message.get("data", {})
            
            logger.debug(f"Received event: {event_type}")
            
            # Find and call handler
            handler = self.handlers.get(event_type)
            if handler:
                handler(data)
            else:
                logger.debug(f"No handler for event type: {event_type}")
            
            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


