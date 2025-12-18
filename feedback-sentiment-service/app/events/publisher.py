"""
Event publisher for feedback and sentiment events.
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
    Publishes feedback and sentiment events for downstream consumers.
    
    Events are consumed by:
    - Analytics service (for dashboards)
    - Marketing service (for campaigns)
    - Notification service (for alerts on negative feedback)
    """
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        logger.info(f"EventPublisher initialized with exchange: {self.exchange}")
    
    def _publish(self, topic: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Internal method to publish events."""
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "feedback-sentiment-service",
            "version": "1.0",
        }
        
        logger.info(f"Publishing event: {event_type} to topic: {topic}")
        logger.debug(f"Event payload: {json.dumps(event, default=str)}")
        
        # TODO: Implement actual message broker publishing
        # channel.basic_publish(exchange=self.exchange, routing_key=f"{topic}.{event_type}", body=json.dumps(event))
    
    def publish_feedback_received(self, feedback_id: UUID, feedback_data: Dict[str, Any]) -> None:
        """Publish feedback received event (triggers async analysis)."""
        self._publish(
            topic=settings.event_topic_feedback,
            event_type="feedback.received",
            payload={"feedback_id": str(feedback_id), **feedback_data}
        )
    
    def publish_analysis_completed(self, feedback_id: UUID, analysis_data: Dict[str, Any]) -> None:
        """Publish analysis completed event."""
        self._publish(
            topic=settings.event_topic_feedback,
            event_type="feedback.analyzed",
            payload={"feedback_id": str(feedback_id), **analysis_data}
        )
    
    def publish_negative_feedback_alert(self, feedback_id: UUID, alert_data: Dict[str, Any]) -> None:
        """Publish alert for very negative feedback (needs attention)."""
        self._publish(
            topic=settings.event_topic_insights,
            event_type="feedback.alert.negative",
            payload={"feedback_id": str(feedback_id), **alert_data}
        )
    
    def publish_insights_updated(self, venue_id: UUID, summary_data: Dict[str, Any]) -> None:
        """Publish insights update for analytics consumers."""
        self._publish(
            topic=settings.event_topic_insights,
            event_type="insights.updated",
            payload={"venue_id": str(venue_id), **summary_data}
        )


# Global event publisher instance
event_publisher = EventPublisher()


