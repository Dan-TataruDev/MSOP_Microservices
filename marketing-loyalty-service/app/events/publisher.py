"""
Event publisher for campaign engagement events.

Publishes events for downstream consumers (analytics, notifications).
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
    Publishes marketing and loyalty events.
    
    Events are consumed by:
    - Analytics service (for campaign performance dashboards)
    - Notification service (for engagement alerts)
    """
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
    
    def _publish(self, topic: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Internal method to publish events."""
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "marketing-loyalty-service",
            "version": "1.0",
        }
        logger.info(f"Publishing event: {event_type}")
        logger.debug(f"Event payload: {json.dumps(event, default=str)}")
        # TODO: Implement actual RabbitMQ publishing
    
    # Campaign Events
    def publish_campaign_created(self, campaign_id: UUID, campaign_data: Dict[str, Any]) -> None:
        """Publish campaign creation event."""
        self._publish(settings.event_topic_campaigns, "campaign.created", {
            "campaign_id": str(campaign_id), **campaign_data
        })
    
    def publish_campaign_activated(self, campaign_id: UUID) -> None:
        """Publish campaign activation event."""
        self._publish(settings.event_topic_campaigns, "campaign.activated", {
            "campaign_id": str(campaign_id)
        })
    
    # Offer Events (Campaign Engagement)
    def publish_offer_presented(self, offer_id: UUID, guest_id: UUID, campaign_id: UUID = None) -> None:
        """Publish when an offer is shown to a guest."""
        self._publish(settings.event_topic_campaigns, "offer.presented", {
            "offer_id": str(offer_id),
            "guest_id": str(guest_id),
            "campaign_id": str(campaign_id) if campaign_id else None,
        })
    
    def publish_offer_claimed(self, offer_id: UUID, guest_id: UUID, campaign_id: UUID = None) -> None:
        """Publish when a guest claims an offer."""
        self._publish(settings.event_topic_campaigns, "offer.claimed", {
            "offer_id": str(offer_id),
            "guest_id": str(guest_id),
            "campaign_id": str(campaign_id) if campaign_id else None,
        })
    
    def publish_offer_redeemed(self, offer_id: UUID, guest_id: UUID, booking_id: UUID) -> None:
        """Publish when an offer is redeemed on a booking."""
        self._publish(settings.event_topic_campaigns, "offer.redeemed", {
            "offer_id": str(offer_id),
            "guest_id": str(guest_id),
            "booking_id": str(booking_id),
        })
    
    # Loyalty Events
    def publish_points_earned(self, guest_id: UUID, points: int, source_type: str) -> None:
        """Publish points earned event."""
        self._publish(settings.event_topic_loyalty, "points.earned", {
            "guest_id": str(guest_id),
            "points": points,
            "source_type": source_type,
        })
    
    def publish_tier_upgraded(self, guest_id: UUID, old_tier: str, new_tier: str) -> None:
        """Publish loyalty tier upgrade event."""
        self._publish(settings.event_topic_loyalty, "tier.upgraded", {
            "guest_id": str(guest_id),
            "old_tier": old_tier,
            "new_tier": new_tier,
        })


event_publisher = EventPublisher()


