"""
API endpoints for dashboards and KPIs.

These endpoints are optimized for read-heavy workloads:
- Pre-aggregated data for fast response
- Caching headers for CDN/browser caching
- Efficient database queries using read replicas
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_read_db
from app.services.metrics_service import MetricsService
from app.schemas.metrics import (
    KPIDashboard, MetricResponse, TimeSeriesData, 
    DashboardFilter, MetricQuery, AggregatedMetric
)
from app.models.metrics import MetricType, Granularity

router = APIRouter()


@router.get("/dashboard", response_model=KPIDashboard)
def get_kpi_dashboard(
    date_from: Optional[datetime] = Query(None, description="Start date for metrics"),
    date_to: Optional[datetime] = Query(None, description="End date for metrics"),
    compare: bool = Query(True, description="Compare to previous period"),
    db: Session = Depends(get_read_db)
):
    """
    Get the main KPI dashboard with all key metrics.
    
    This endpoint returns pre-aggregated metrics optimized for
    fast dashboard rendering. Data freshness depends on
    aggregation interval (typically 5-15 minutes).
    
    Response includes:
    - Revenue KPIs (total revenue, AOV, RevPAR)
    - Booking KPIs (total bookings, conversion rate, cancellations)
    - Occupancy KPIs (occupancy rate, ADR)
    - Guest satisfaction KPIs (ratings, NPS)
    - Operational KPIs (payment success, housekeeping efficiency)
    """
    service = MetricsService(db)
    return service.get_kpi_dashboard(
        date_from=date_from,
        date_to=date_to,
        compare_to_previous=compare
    )


@router.get("/metrics/{metric_type}", response_model=MetricResponse)
def get_metric(
    metric_type: MetricType,
    granularity: Granularity = Query(Granularity.DAILY),
    db: Session = Depends(get_read_db)
):
    """
    Get a single metric's current value with trend information.
    
    Returns the latest value for the specified metric,
    along with change percentage and trend direction.
    """
    service = MetricsService(db)
    metric = service.get_metric(metric_type, granularity)
    
    if not metric:
        raise HTTPException(
            status_code=404, 
            detail=f"Metric {metric_type.value} not found"
        )
    
    return metric


@router.get("/metrics/{metric_type}/timeseries", response_model=TimeSeriesData)
def get_metric_timeseries(
    metric_type: MetricType,
    granularity: Granularity = Query(Granularity.DAILY),
    period_start: datetime = Query(..., description="Start of period"),
    period_end: datetime = Query(..., description="End of period"),
    db: Session = Depends(get_read_db)
):
    """
    Get time series data for a metric.
    
    Used for rendering charts and graphs on the dashboard.
    Returns data points at the specified granularity.
    """
    service = MetricsService(db)
    return service.get_time_series(
        metric_type=metric_type,
        granularity=granularity,
        period_start=period_start,
        period_end=period_end
    )


@router.post("/metrics/query")
def query_metrics(
    query: MetricQuery,
    db: Session = Depends(get_read_db)
):
    """
    Query multiple metrics with filters.
    
    Allows fetching multiple metrics in a single request
    with optional dimensional filtering.
    """
    service = MetricsService(db)
    results = {}
    
    for metric_type in query.metric_types:
        if query.include_time_series:
            results[metric_type.value] = service.get_time_series(
                metric_type=metric_type,
                granularity=query.granularity,
                period_start=query.period_start,
                period_end=query.period_end,
                dimensions=query.dimensions
            )
        else:
            metric = service.get_metric(metric_type, query.granularity)
            if metric:
                results[metric_type.value] = metric
    
    return {
        "query": {
            "period_start": query.period_start,
            "period_end": query.period_end,
            "granularity": query.granularity.value
        },
        "results": results
    }


@router.get("/dashboard/revenue")
def get_revenue_dashboard(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_read_db)
):
    """
    Get revenue-focused dashboard data.
    
    Includes detailed revenue metrics and breakdowns.
    """
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=30)
    
    service = MetricsService(db)
    
    revenue_metrics = [
        MetricType.TOTAL_REVENUE,
        MetricType.AVERAGE_ORDER_VALUE,
        MetricType.REVPAR,
        MetricType.REVENUE_PER_ROOM
    ]
    
    metrics = {}
    for metric_type in revenue_metrics:
        metric = service.get_metric(metric_type)
        if metric:
            metrics[metric_type.value] = metric
    
    # Get time series for main revenue metric (will generate mock if no data)
    revenue_trend = service.get_time_series(
        MetricType.TOTAL_REVENUE,
        Granularity.DAILY,
        date_from,
        date_to
    )
    
    return {
        "period": {"start": date_from, "end": date_to},
        "metrics": metrics,
        "revenue_trend": revenue_trend
    }


@router.get("/dashboard/operations")
def get_operations_dashboard(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_read_db)
):
    """
    Get operations-focused dashboard data.
    
    Includes operational efficiency metrics.
    """
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=7)
    
    service = MetricsService(db)
    
    ops_metrics = [
        MetricType.PAYMENT_SUCCESS_RATE,
        MetricType.HOUSEKEEPING_EFFICIENCY,
        MetricType.MAINTENANCE_RESPONSE_TIME,
        MetricType.CHECK_IN_TIME
    ]
    
    metrics = {}
    for metric_type in ops_metrics:
        metric = service.get_metric(metric_type)
        if metric:
            metrics[metric_type.value] = metric
    
    return {
        "period": {"start": date_from, "end": date_to},
        "metrics": metrics
    }
