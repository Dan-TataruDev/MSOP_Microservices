"""
Base Price model for storing standard/base prices per venue.

Base prices serve as the foundation for dynamic pricing calculations.
They represent the "normal" price before any dynamic adjustments.
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Enum, Boolean,
    Integer, Numeric, JSON, Text, Index
)
import uuid

from app.database import Base, GUID


class VenueType(str, enum.Enum):
    """Types of venues supported by the platform."""
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    RETAIL = "retail"
    SPA = "spa"
    EVENT_SPACE = "event_space"


class BasePrice(Base):
    """
    Base Price entity.
    
    Stores the standard pricing for venues/products.
    This is the starting point for all dynamic price calculations.
    """
    __tablename__ = "base_prices"
    
    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # Venue identification
    venue_id = Column(GUID, nullable=False, index=True)
    venue_type = Column(Enum(VenueType), nullable=False, index=True)
    venue_name = Column(String(255), nullable=True)
    
    # Product/service identification (for granular pricing)
    product_id = Column(GUID, nullable=True, index=True)
    product_name = Column(String(255), nullable=True)
    product_category = Column(String(100), nullable=True)
    
    # Pricing
    base_price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Price type
    price_type = Column(String(50), default="per_unit")  # per_unit, per_hour, per_night, per_person
    unit_description = Column(String(100), nullable=True)  # "per night", "per person", etc.
    
    # Minimum and maximum prices (guardrails)
    min_price = Column(Numeric(12, 2), nullable=True)
    max_price = Column(Numeric(12, 2), nullable=True)
    
    # Tax configuration
    tax_rate = Column(Numeric(5, 4), default=0.10)  # Default 10%
    tax_included = Column(Boolean, default=False)
    
    # Validity period
    valid_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=True)
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Extra data
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_base_prices_venue_product", "venue_id", "product_id"),
        Index("ix_base_prices_venue_type_active", "venue_type", "is_active"),
    )
    
    def get_effective_price(self) -> tuple:
        """Get effective price considering validity."""
        now = datetime.utcnow()
        if not self.is_active:
            return None, "inactive"
        if self.valid_until and now > self.valid_until:
            return None, "expired"
        return self.base_price, "valid"
    
    def __repr__(self):
        return f"<BasePrice {self.venue_id}: {self.base_price} {self.currency}>"
