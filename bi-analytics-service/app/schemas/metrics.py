"""
Schemas for metrics and KPI API responses.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.metrics import MetricType, Granularity


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series."""
    timestamp: datetime
    value: float
    count: Optional[int] = None


class TimeSeriesData(BaseModel):
    """Time series data for charts."""
    metric_type: MetricType
    granularity: Granularity
    data_points: List[TimeSeriesDataPoint]
    period_start: datetime
    period_end: datetime


class AggregatedMetric(BaseModel):
    """Aggregated metric with statistics."""
    metric_type: MetricType
    value: float
    count: int = 0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    change_percent: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    period_start: datetime
    period_end: datetime
    dimensions: Dict[str, Any] = {}


class MetricResponse(BaseModel):
    """Response for single metric query."""
    metric_type: MetricType
    current_value: float
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    trend: Optional[str] = None
    updated_at: datetime
    data_freshness: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KPICard(BaseModel):
    """Single KPI card for dashboard."""
    id: str
    title: str
    metric_type: MetricType
    value: float
    formatted_value: str  # e.g., "$12,345" or "87.5%"
    unit: Optional[str] = None
    change_percent: Optional[float] = None
    trend: Optional[str] = None
    sparkline: Optional[List[float]] = None  # Mini chart data
    updated_at: datetime


class KPIDashboard(BaseModel):
    """Complete KPI dashboard response."""
    dashboard_id: str = "main"
    title: str = "Business Intelligence Dashboard"
    generated_at: datetime
    data_freshness: Optional[datetime] = None
    
    # Revenue KPIs
    revenue_kpis: List[KPICard] = []
    
    # Booking KPIs
    booking_kpis: List[KPICard] = []
    
    # Occupancy KPIs
    occupancy_kpis: List[KPICard] = []
    
    # Guest Satisfaction KPIs
    satisfaction_kpis: List[KPICard] = []
    
    # Operational KPIs
    operational_kpis: List[KPICard] = []


class MetricQuery(BaseModel):
    """Query parameters for metric retrieval."""
    metric_types: List[MetricType]
    granularity: Granularity = Granularity.DAILY
    period_start: datetime
    period_end: datetime
    dimensions: Optional[Dict[str, Any]] = None
    include_time_series: bool = False


class DashboardFilter(BaseModel):
    """Filters for dashboard data."""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    room_types: Optional[List[str]] = None
    channels: Optional[List[str]] = None
    compare_to_previous: bool = True
