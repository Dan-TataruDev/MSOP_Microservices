"""
Event publisher for payment and billing events.
Publishes events for downstream consumers (booking service, analytics, etc.).
"""
import json
import logging
from typing import Dict, Any
from datetime import datetime
from uuid import UUID
from app.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes payment and billing lifecycle events for downstream consumers.
    
    Events are consumed by:
    - Booking service (for payment status updates)
    - Analytics service (for reporting)
    - Notification service (for payment confirmations)
    """
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        # In production, initialize RabbitMQ connection here
        logger.info(f"EventPublisher initialized with exchange: {self.exchange}")
    
    def _publish(self, topic: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Internal method to publish events."""
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "payment-billing-service",
            "version": "1.0",
        }
        
        # In production, publish to message broker
        logger.info(f"Publishing event: {event_type} to topic: {topic}")
        logger.debug(f"Event payload: {json.dumps(event, default=str)}")
        
        # TODO: Implement actual message broker publishing
        # channel = self.connection.channel()
        # channel.basic_publish(
        #     exchange=self.exchange,
        #     routing_key=f"{topic}.{event_type}",
        #     body=json.dumps(event),
        #     properties=pika.BasicProperties(delivery_mode=2)
        # )
    
    def publish_payment_initiated(self, payment_id: UUID, payment_data: Dict[str, Any]) -> None:
        """Publish payment initiated event."""
        self._publish(
            topic=settings.event_topic_payment,
            event_type="payment.initiated",
            payload={
                "payment_id": str(payment_id),
                **payment_data,
            }
        )
    
    def publish_payment_completed(self, payment_id: UUID, payment_data: Dict[str, Any]) -> None:
        """Publish payment completed event."""
        self._publish(
            topic=settings.event_topic_payment,
            event_type="payment.completed",
            payload={
                "payment_id": str(payment_id),
                **payment_data,
            }
        )
    
    def publish_payment_failed(self, payment_id: UUID, payment_data: Dict[str, Any]) -> None:
        """Publish payment failed event."""
        self._publish(
            topic=settings.event_topic_payment,
            event_type="payment.failed",
            payload={
                "payment_id": str(payment_id),
                **payment_data,
            }
        )
    
    def publish_refund_initiated(self, refund_id: UUID, refund_data: Dict[str, Any]) -> None:
        """Publish refund initiated event."""
        self._publish(
            topic=settings.event_topic_payment,
            event_type="refund.initiated",
            payload={
                "refund_id": str(refund_id),
                **refund_data,
            }
        )
    
    def publish_refund_completed(self, refund_id: UUID, refund_data: Dict[str, Any]) -> None:
        """Publish refund completed event."""
        self._publish(
            topic=settings.event_topic_payment,
            event_type="refund.completed",
            payload={
                "refund_id": str(refund_id),
                **refund_data,
            }
        )


# Global event publisher instance
event_publisher = EventPublisher()


