"""
HTTP clients for external service communication.
"""
from app.clients.inventory_client import InventoryClient
from app.clients.analytics_client import AnalyticsClient

__all__ = [
    "InventoryClient",
    "AnalyticsClient",
]


