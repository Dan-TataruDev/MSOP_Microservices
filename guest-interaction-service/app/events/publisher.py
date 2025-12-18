"""
Event publisher for publishing guest-related events.
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
    Publishes events related to guest profile, preferences, and interactions.
    In production, this would integrate with RabbitMQ, Kafka, or similar.
    """
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        # In production, initialize RabbitMQ connection here
        # self.connection = pika.BlockingConnection(...)
        logger.info(f"EventPublisher initialized with exchange: {self.exchange}")
    
    def _publish(self, topic: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Internal method to publish events."""
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "guest-interaction-service",
            "version": "1.0",
        }
        
        # In production, publish to message broker
        # For now, just log
        logger.info(f"Publishing event: {event_type} to topic: {topic}")
        logger.debug(f"Event payload: {json.dumps(event, default=str)}")
        
        # TODO: Implement actual message broker publishing
        # channel = self.connection.channel()
        # channel.basic_publish(
        #     exchange=self.exchange,
        #     routing_key=f"{topic}.{event_type}",
        #     body=json.dumps(event),
        #     properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        # )
    
    def publish_profile_created(self, guest_id: UUID, guest_data: Dict[str, Any]) -> None:
        """Publish guest profile created event."""
        self._publish(
            topic="guest",
            event_type="profile.created",
            payload={
                "guest_id": str(guest_id),
                "guest_data": guest_data,
            }
        )
    
    def publish_profile_updated(self, guest_id: UUID, changes: Dict[str, Any]) -> None:
        """Publish guest profile updated event."""
        self._publish(
            topic="guest",
            event_type="profile.updated",
            payload={
                "guest_id": str(guest_id),
                "changes": changes,
            }
        )
    
    def publish_preferences_updated(
        self, 
        guest_id: UUID, 
        preference_key: str, 
        old_value: Any, 
        new_value: Any
    ) -> None:
        """Publish preferences updated event."""
        self._publish(
            topic="guest",
            event_type="preferences.updated",
            payload={
                "guest_id": str(guest_id),
                "preference_key": preference_key,
                "old_value": old_value,
                "new_value": new_value,
            }
        )
    
    def publish_interaction_recorded(
        self, 
        guest_id: UUID, 
        interaction_type: str, 
        entity_type: Optional[str], 
        entity_id: Optional[str]
    ) -> None:
        """Publish interaction recorded event."""
        self._publish(
            topic="guest",
            event_type="interaction.recorded",
            payload={
                "guest_id": str(guest_id),
                "interaction_type": interaction_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
            }
        )
    
    def publish_data_exported(self, guest_id: UUID) -> None:
        """Publish data export event (GDPR)."""
        self._publish(
            topic="guest",
            event_type="data.exported",
            payload={
                "guest_id": str(guest_id),
            }
        )
    
    def publish_data_deleted(self, guest_id: UUID) -> None:
        """Publish data deletion event (GDPR)."""
        self._publish(
            topic="guest",
            event_type="data.deleted",
            payload={
                "guest_id": str(guest_id),
            }
        )
    
    def publish_consent_updated(self, guest_id: UUID, consent_type: str, value: bool) -> None:
        """Publish consent update event."""
        self._publish(
            topic="guest",
            event_type="consent.updated",
            payload={
                "guest_id": str(guest_id),
                "consent_type": consent_type,
                "value": value,
            }
        )


# Global event publisher instance
event_publisher = EventPublisher()
