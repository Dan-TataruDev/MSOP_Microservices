"""
Models for metrics and KPI storage.

Design:
- Pre-aggregated metrics for fast reads
- Multiple granularity levels (hourly, daily, monthly)
- Supports time-series queries efficiently
"""
import enum
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Float, Integer, Enum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class MetricType(str, enum.Enum):
    """Types of metrics tracked by the system."""
    # Revenue Metrics
    TOTAL_REVENUE = "total_revenue"
    AVERAGE_ORDER_VALUE = "average_order_value"
    REVENUE_PER_ROOM = "revenue_per_room"
    
    # Booking Metrics
    TOTAL_BOOKINGS = "total_bookings"
    BOOKING_CONVERSION_RATE = "booking_conversion_rate"
    CANCELLATION_RATE = "cancellation_rate"
    AVERAGE_LEAD_TIME = "average_lead_time"
    
    # Occupancy Metrics
    OCCUPANCY_RATE = "occupancy_rate"
    AVERAGE_DAILY_RATE = "average_daily_rate"
    REVPAR = "revpar"  # Revenue per available room
    
    # Guest Metrics
    GUEST_SATISFACTION = "guest_satisfaction"
    NET_PROMOTER_SCORE = "net_promoter_score"
    REPEAT_GUEST_RATE = "repeat_guest_rate"
    
    # Operational Metrics
    HOUSEKEEPING_EFFICIENCY = "housekeeping_efficiency"
    MAINTENANCE_RESPONSE_TIME = "maintenance_response_time"
    CHECK_IN_TIME = "check_in_time"
    
    # Payment Metrics
    PAYMENT_SUCCESS_RATE = "payment_success_rate"
    REFUND_RATE = "refund_rate"
    AVERAGE_PAYMENT_TIME = "average_payment_time"


class Granularity(str, enum.Enum):
    """Time granularity for aggregated metrics."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class MetricSnapshot(Base):
    """
    Pre-aggregated metric snapshots for fast dashboard queries.
    
    This table stores pre-computed metrics at various granularities.
    Data is populated by background aggregation jobs, not real-time.
    """
    __tablename__ = "metric_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Metric identification
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    granularity = Column(Enum(Granularity), nullable=False, index=True)
    
    # Time bucket (start of the period)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    # Metric values
    value = Column(Float, nullable=False)
    count = Column(Integer, default=0)  # Number of data points in aggregation
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    
    # Dimensional breakdown (optional)
    dimensions = Column(JSON, default={})  # e.g., {"room_type": "suite", "channel": "direct"}
    
    # Metadata
    computed_at = Column(DateTime, default=datetime.utcnow)
    data_freshness = Column(DateTime)  # Latest source event timestamp
    
    __table_args__ = (
        # Composite index for efficient dashboard queries
        Index('ix_metric_snapshot_lookup', 'metric_type', 'granularity', 'period_start'),
        # Index for time-range queries
        Index('ix_metric_snapshot_period', 'period_start', 'period_end'),
    )


class RealtimeMetric(Base):
    """
    Near real-time metrics with short TTL.
    
    Updated more frequently for live dashboards.
    Stored separately to not bloat historical data.
    """
    __tablename__ = "realtime_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    
    # Current value
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)  # For trend calculation
    
    # Change indicators
    change_percent = Column(Float, nullable=True)
    trend = Column(String(10), nullable=True)  # "up", "down", "stable"
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_realtime_metric_type', 'metric_type'),
    )
