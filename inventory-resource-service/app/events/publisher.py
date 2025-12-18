"""Event publisher for inventory alerts and resource status changes."""
import json
import logging
from typing import Dict, Any
from datetime import datetime
from uuid import UUID
from app.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes inventory and resource events for downstream consumers."""
    
    def __init__(self):
        self.exchange = settings.rabbitmq_exchange
        logger.info(f"EventPublisher initialized with exchange: {self.exchange}")
    
    def _publish(self, topic: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Internal method to publish events."""
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "inventory-resource-service",
            "version": "1.0",
        }
        logger.info(f"Publishing event: {event_type} to topic: {topic}")
        logger.debug(f"Event payload: {json.dumps(event, default=str)}")
        # TODO: Implement actual message broker publishing
    
    def publish_low_stock_alert(self, item_data: Dict[str, Any]) -> None:
        """Emit alert when stock falls below low threshold."""
        self._publish(
            topic=settings.event_topic_inventory,
            event_type="inventory.low_stock",
            payload=item_data
        )
    
    def publish_critical_stock_alert(self, item_data: Dict[str, Any]) -> None:
        """Emit alert when stock falls below critical threshold."""
        self._publish(
            topic=settings.event_topic_inventory,
            event_type="inventory.critical_stock",
            payload=item_data
        )
    
    def publish_restock_required(self, item_data: Dict[str, Any]) -> None:
        """Emit event requesting restock from suppliers."""
        self._publish(
            topic=settings.event_topic_inventory,
            event_type="inventory.restock_required",
            payload=item_data
        )
    
    def publish_stock_updated(self, item_id: UUID, transaction_data: Dict[str, Any]) -> None:
        """Emit event when stock level changes."""
        self._publish(
            topic=settings.event_topic_inventory,
            event_type="inventory.stock_updated",
            payload={"item_id": str(item_id), **transaction_data}
        )
    
    def publish_room_status_changed(self, room_id: UUID, old_status: str, new_status: str) -> None:
        """Emit event when room status changes."""
        self._publish(
            topic=settings.event_topic_inventory,
            event_type="resource.room_status_changed",
            payload={"room_id": str(room_id), "old_status": old_status, "new_status": new_status}
        )
    
    def publish_table_status_changed(self, table_id: UUID, old_status: str, new_status: str) -> None:
        """Emit event when table status changes."""
        self._publish(
            topic=settings.event_topic_inventory,
            event_type="resource.table_status_changed",
            payload={"table_id": str(table_id), "old_status": old_status, "new_status": new_status}
        )


event_publisher = EventPublisher()


