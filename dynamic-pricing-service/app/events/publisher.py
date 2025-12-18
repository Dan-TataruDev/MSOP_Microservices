"""
Event Publisher for the Dynamic Pricing Service.

Publishes pricing events to the message broker for
consumption by other services (Booking, Analytics, etc.).
"""
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

import pika
from pika.exceptions import AMQPError

from app.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes pricing events to RabbitMQ.
    
    Events are published to a topic exchange for flexible routing.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = settings.rabbitmq_exchange
    
    def _get_channel(self):
        """Get or create a RabbitMQ channel."""
        if self.channel is None or self.channel.is_closed:
            try:
                params = pika.URLParameters(settings.rabbitmq_url)
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                
                # Declare exchange
                self.channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type="topic",
                    durable=True,
                )
            except AMQPError as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
        
        return self.channel
    
    def _publish(self, routing_key: str, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish an event to the message broker."""
        try:
            channel = self._get_channel()
            
            message = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "source": settings.app_name,
                "data": data,
            }
            
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=json.dumps(message, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type="application/json",
                ),
            )
            
            logger.debug(f"Published event: {event_type} to {routing_key}")
            return True
            
        except AMQPError as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            self.channel = None
            return False
    
    # =========================================================================
    # Price Decision Events
    # =========================================================================
    
    def publish_price_calculated(
        self,
        decision_reference: str,
        venue_id: UUID,
        venue_type: str,
        total_price: float,
        currency: str,
        source: str,
        valid_until: datetime,
    ) -> bool:
        """Publish event when a price is calculated."""
        return self._publish(
            routing_key=f"{settings.event_topic_pricing}.calculated",
            event_type="price.calculated",
            data={
                "decision_reference": decision_reference,
                "venue_id": str(venue_id),
                "venue_type": venue_type,
                "total_price": total_price,
                "currency": currency,
                "pricing_source": source,
                "valid_until": valid_until.isoformat(),
            },
        )
    
    def publish_price_accepted(
        self,
        decision_reference: str,
        booking_id: UUID,
        booking_reference: str,
        total_price: float,
    ) -> bool:
        """Publish event when a price is accepted (booking created)."""
        return self._publish(
            routing_key=f"{settings.event_topic_pricing}.accepted",
            event_type="price.accepted",
            data={
                "decision_reference": decision_reference,
                "booking_id": str(booking_id),
                "booking_reference": booking_reference,
                "total_price": total_price,
            },
        )
    
    def publish_price_expired(
        self, decision_reference: str, venue_id: UUID
    ) -> bool:
        """Publish event when a price quote expires."""
        return self._publish(
            routing_key=f"{settings.event_topic_pricing}.expired",
            event_type="price.expired",
            data={
                "decision_reference": decision_reference,
                "venue_id": str(venue_id),
            },
        )
    
    # =========================================================================
    # Rule Events
    # =========================================================================
    
    def publish_rule_activated(
        self, rule_code: str, rule_type: str, venues_affected: Optional[list] = None
    ) -> bool:
        """Publish event when a pricing rule is activated."""
        return self._publish(
            routing_key=f"{settings.event_topic_pricing}.rule.activated",
            event_type="pricing_rule.activated",
            data={
                "rule_code": rule_code,
                "rule_type": rule_type,
                "venues_affected": venues_affected,
            },
        )
    
    def publish_rule_deactivated(self, rule_code: str) -> bool:
        """Publish event when a pricing rule is deactivated."""
        return self._publish(
            routing_key=f"{settings.event_topic_pricing}.rule.deactivated",
            event_type="pricing_rule.deactivated",
            data={
                "rule_code": rule_code,
            },
        )
    
    # =========================================================================
    # Demand Events
    # =========================================================================
    
    def publish_demand_updated(
        self,
        venue_id: UUID,
        venue_type: str,
        demand_level: str,
        occupancy_rate: float,
    ) -> bool:
        """Publish event when demand data is updated."""
        return self._publish(
            routing_key=f"{settings.event_topic_demand}.updated",
            event_type="demand.updated",
            data={
                "venue_id": str(venue_id),
                "venue_type": venue_type,
                "demand_level": demand_level,
                "occupancy_rate": occupancy_rate,
            },
        )
    
    def close(self):
        """Close the connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


# Singleton instance
event_publisher = EventPublisher()


