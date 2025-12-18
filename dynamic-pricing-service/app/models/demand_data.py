"""
Demand Data model for storing and tracking demand signals.

Demand data is collected from various sources and used by
the pricing engine to make dynamic adjustments.
"""
import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, String, DateTime, Date, Enum, 
    Integer, Numeric, JSON, Index
)
import uuid

from app.database import Base, GUID


class DemandLevel(str, enum.Enum):
    """Demand level categories."""
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"
    PEAK = "peak"


class DemandData(Base):
    """
    Demand Data entity.
    
    Stores demand signals and metrics used for dynamic pricing.
    Updated regularly from analytics and inventory services.
    """
    __tablename__ = "demand_data"
    
    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # Venue identification
    venue_id = Column(GUID, nullable=False, index=True)
    venue_type = Column(String(50), nullable=False, index=True)
    
    # Time period
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)  # 0-23, null for daily aggregate
    
    # Demand metrics
    demand_level = Column(Enum(DemandLevel), nullable=False, index=True)
    demand_score = Column(Numeric(5, 4), nullable=False)  # 0.0 to 1.0
    
    # Occupancy/availability
    capacity = Column(Integer, nullable=True)
    occupied = Column(Integer, nullable=True)
    occupancy_rate = Column(Numeric(5, 4), nullable=True)  # 0.0 to 1.0
    
    # Booking velocity
    bookings_last_hour = Column(Integer, default=0)
    bookings_last_24h = Column(Integer, default=0)
    cancellations_last_24h = Column(Integer, default=0)
    
    # Historical comparison
    avg_occupancy_same_day = Column(Numeric(5, 4), nullable=True)  # Historical average for same day/time
    demand_vs_historical = Column(Numeric(5, 4), nullable=True)  # Ratio vs historical
    
    # External factors
    is_holiday = Column(String(100), nullable=True)  # Holiday name if applicable
    is_event = Column(String(255), nullable=True)  # Special event description
    weather_impact = Column(Numeric(5, 4), nullable=True)  # -1.0 to 1.0
    
    # Forecast data
    forecasted_demand = Column(Enum(DemandLevel), nullable=True)
    forecast_confidence = Column(Numeric(5, 4), nullable=True)
    
    # Price recommendations
    suggested_multiplier = Column(Numeric(5, 4), nullable=True)
    
    # Source and freshness
    data_source = Column(String(50), nullable=False)  # analytics, inventory, forecast
    data_freshness = Column(DateTime, nullable=False)  # When data was collected
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("ix_demand_venue_date", "venue_id", "date"),
        Index("ix_demand_venue_date_hour", "venue_id", "date", "hour"),
        Index("ix_demand_level_date", "demand_level", "date"),
    )
    
    def __repr__(self):
        return f"<DemandData {self.venue_id} {self.date}: {self.demand_level}>"


