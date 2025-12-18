"""
Event publisher for booking lifecycle events.
Publishes events for downstream consumers (analytics, personalization, housekeeping, marketing).
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from app.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes booking lifecycle events for downstream consumers.
    
    Events are consumed by:
    - Analytics service (for reporting)
    - Personalization service (for recommendations)
    - Housekeeping service (for operational tasks)
    - Marketing service (for campaigns)
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
            "source": "booking-reservation-service",
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
    
    def publish_booking_created(self, booking_id: UUID, booking_data: Dict[str, Any]) -> None:
        """Publish booking created event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.created",
            payload={
                "booking_id": str(booking_id),
                "booking_reference": booking_data.get("booking_reference"),
                "guest_id": str(booking_data.get("guest_id")),
                "venue_id": str(booking_data.get("venue_id")),
                "venue_type": booking_data.get("venue_type"),
                "booking_time": booking_data.get("booking_time").isoformat() if booking_data.get("booking_time") else None,
                "party_size": booking_data.get("party_size"),
                "total_price": str(booking_data.get("total_price")),
                "currency": booking_data.get("currency"),
                "status": booking_data.get("status"),
            }
        )
    
    def publish_booking_updated(self, booking_id: UUID, changes: Dict[str, Any]) -> None:
        """Publish booking updated event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.updated",
            payload={
                "booking_id": str(booking_id),
                "changes": changes,
            }
        )
    
    def publish_booking_cancelled(
        self,
        booking_id: UUID,
        booking_reference: str,
        guest_id: UUID,
        venue_id: UUID,
        reason: Optional[str],
        cancelled_by: str
    ) -> None:
        """Publish booking cancelled event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.cancelled",
            payload={
                "booking_id": str(booking_id),
                "booking_reference": booking_reference,
                "guest_id": str(guest_id),
                "venue_id": str(venue_id),
                "reason": reason,
                "cancelled_by": cancelled_by,
            }
        )
    
    def publish_booking_status_changed(
        self,
        booking_id: UUID,
        booking_reference: str,
        from_status: str,
        to_status: str,
        changed_by: str
    ) -> None:
        """Publish booking status changed event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.status_changed",
            payload={
                "booking_id": str(booking_id),
                "booking_reference": booking_reference,
                "from_status": from_status,
                "to_status": to_status,
                "changed_by": changed_by,
            }
        )
    
    def publish_booking_confirmed(self, booking_id: UUID, booking_data: Dict[str, Any]) -> None:
        """Publish booking confirmed event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.confirmed",
            payload={
                "booking_id": str(booking_id),
                "booking_reference": booking_data.get("booking_reference"),
                "guest_id": str(booking_data.get("guest_id")),
                "venue_id": str(booking_data.get("venue_id")),
                "booking_time": booking_data.get("booking_time").isoformat() if booking_data.get("booking_time") else None,
            }
        )
    
    def publish_booking_checked_in(self, booking_id: UUID, booking_reference: str, venue_id: UUID) -> None:
        """Publish booking checked in event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.checked_in",
            payload={
                "booking_id": str(booking_id),
                "booking_reference": booking_reference,
                "venue_id": str(venue_id),
            }
        )
    
    def publish_booking_completed(self, booking_id: UUID, booking_reference: str, venue_id: UUID) -> None:
        """Publish booking completed event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.completed",
            payload={
                "booking_id": str(booking_id),
                "booking_reference": booking_reference,
                "venue_id": str(venue_id),
            }
        )
    
    def publish_booking_expired(self, booking_id: UUID, booking_reference: str) -> None:
        """Publish booking expired event."""
        self._publish(
            topic=settings.event_topic_booking,
            event_type="booking.expired",
            payload={
                "booking_id": str(booking_id),
                "booking_reference": booking_reference,
            }
        )


# Global event publisher instance
event_publisher = EventPublisher()


