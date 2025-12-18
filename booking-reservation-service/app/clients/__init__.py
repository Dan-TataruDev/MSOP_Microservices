"""
External service clients for coordination.
These clients communicate with other microservices via HTTP,
but do not embed their business logic.
"""
from app.clients.inventory_client import InventoryClient
from app.clients.pricing_client import PricingClient
from app.clients.payment_client import PaymentClient

__all__ = ["InventoryClient", "PricingClient", "PaymentClient"]


