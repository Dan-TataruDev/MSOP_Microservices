"""
API v1 routers for the Dynamic Pricing Service.
"""
from app.api.v1.pricing import router as pricing_router
from app.api.v1.rules import router as rules_router
from app.api.v1.decisions import router as decisions_router
from app.api.v1.base_prices import router as base_prices_router

__all__ = [
    "pricing_router",
    "rules_router",
    "decisions_router",
    "base_prices_router",
]


