"""Events package for data ingestion."""
from app.events.consumer import event_consumer
from app.events.handlers import register_handlers

__all__ = ["event_consumer", "register_handlers"]
