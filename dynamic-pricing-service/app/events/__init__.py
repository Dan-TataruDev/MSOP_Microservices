"""
Event handling for the Dynamic Pricing Service.

Publishes:
- Price decision events
- Price change notifications
- Demand update acknowledgments

Consumes:
- Booking events (to track price acceptance)
- Inventory events (availability changes)
- Analytics events (demand signals)
"""
from app.events.publisher import event_publisher
from app.events.consumer import EventConsumer
from app.events.handlers import PricingEventHandlers

__all__ = [
    "event_publisher",
    "EventConsumer",
    "PricingEventHandlers",
]


