"""
Service for retrieving and computing metrics.

Design:
- Read-optimized queries using pre-aggregated data
- Caching for frequently accessed metrics
- Support for real-time and historical metrics
- Mock data generation for demo purposes
"""
import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.metrics import MetricSnapshot, RealtimeMetric, MetricType, Granularity
from app.schemas.metrics import (
    MetricResponse, KPIDashboard, KPICard, TimeSeriesData, 
    TimeSeriesDataPoint, AggregatedMetric
)

logger = logging.getLogger(__name__)


class MetricsService:
    """Service for metric retrieval and KPI computation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_metric(
        self, 
        metric_type: MetricType,
        granularity: Granularity = Granularity.DAILY
    ) -> Optional[MetricResponse]:
        """Get the latest value for a specific metric."""
        # Try real-time metric first
        realtime = self.db.query(RealtimeMetric).filter(
            RealtimeMetric.metric_type == metric_type
        ).first()
        
        if realtime:
            return MetricResponse(
                metric_type=metric_type,
                current_value=realtime.value,
                previous_value=realtime.previous_value,
                change_percent=realtime.change_percent,
                trend=realtime.trend,
                updated_at=realtime.updated_at,
            )
        
        # Fall back to latest snapshot
        snapshot = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.metric_type == metric_type,
            MetricSnapshot.granularity == granularity
        ).order_by(MetricSnapshot.period_start.desc()).first()
        
        if snapshot:
            return MetricResponse(
                metric_type=metric_type,
                current_value=snapshot.value,
                updated_at=snapshot.computed_at,
                data_freshness=snapshot.data_freshness,
            )
        
        # Generate mock data for demo
        return self._generate_mock_metric(metric_type)
    
    def get_time_series(
        self,
        metric_type: MetricType,
        granularity: Granularity,
        period_start: datetime,
        period_end: datetime,
        dimensions: Optional[Dict[str, Any]] = None
    ) -> TimeSeriesData:
        """Get time series data for charts."""
        query = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.metric_type == metric_type,
            MetricSnapshot.granularity == granularity,
            MetricSnapshot.period_start >= period_start,
            MetricSnapshot.period_end <= period_end
        )
        
        if dimensions:
            # Filter by dimensions if provided
            for key, value in dimensions.items():
                query = query.filter(
                    MetricSnapshot.dimensions[key].astext == str(value)
                )
        
        snapshots = query.order_by(MetricSnapshot.period_start).all()
        
        # If no data, generate mock time series
        if not snapshots:
            return self._generate_mock_time_series(metric_type, granularity, period_start, period_end)
        
        data_points = [
            TimeSeriesDataPoint(
                timestamp=s.period_start,
                value=s.value,
                count=s.count
            )
            for s in snapshots
        ]
        
        return TimeSeriesData(
            metric_type=metric_type,
            granularity=granularity,
            data_points=data_points,
            period_start=period_start,
            period_end=period_end
        )
    
    def get_kpi_dashboard(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        compare_to_previous: bool = True
    ) -> KPIDashboard:
        """Get complete KPI dashboard with all metrics."""
        if not date_to:
            date_to = datetime.utcnow()
        if not date_from:
            date_from = date_to - timedelta(days=30)
        
        dashboard = KPIDashboard(
            generated_at=datetime.utcnow(),
        )
        
        # Revenue KPIs
        dashboard.revenue_kpis = [
            self._build_kpi_card(
                "total_revenue", "Total Revenue", MetricType.TOTAL_REVENUE,
                date_from, date_to, "$", compare_to_previous
            ),
            self._build_kpi_card(
                "avg_order_value", "Avg Order Value", MetricType.AVERAGE_ORDER_VALUE,
                date_from, date_to, "$", compare_to_previous
            ),
            self._build_kpi_card(
                "revpar", "RevPAR", MetricType.REVPAR,
                date_from, date_to, "$", compare_to_previous
            ),
        ]
        
        # Booking KPIs
        dashboard.booking_kpis = [
            self._build_kpi_card(
                "total_bookings", "Total Bookings", MetricType.TOTAL_BOOKINGS,
                date_from, date_to, None, compare_to_previous
            ),
            self._build_kpi_card(
                "conversion_rate", "Conversion Rate", MetricType.BOOKING_CONVERSION_RATE,
                date_from, date_to, "%", compare_to_previous
            ),
            self._build_kpi_card(
                "cancellation_rate", "Cancellation Rate", MetricType.CANCELLATION_RATE,
                date_from, date_to, "%", compare_to_previous
            ),
        ]
        
        # Occupancy KPIs
        dashboard.occupancy_kpis = [
            self._build_kpi_card(
                "occupancy_rate", "Occupancy Rate", MetricType.OCCUPANCY_RATE,
                date_from, date_to, "%", compare_to_previous
            ),
            self._build_kpi_card(
                "adr", "Average Daily Rate", MetricType.AVERAGE_DAILY_RATE,
                date_from, date_to, "$", compare_to_previous
            ),
        ]
        
        # Satisfaction KPIs
        dashboard.satisfaction_kpis = [
            self._build_kpi_card(
                "guest_satisfaction", "Guest Satisfaction", MetricType.GUEST_SATISFACTION,
                date_from, date_to, "/5", compare_to_previous
            ),
            self._build_kpi_card(
                "nps", "Net Promoter Score", MetricType.NET_PROMOTER_SCORE,
                date_from, date_to, None, compare_to_previous
            ),
        ]
        
        # Operational KPIs
        dashboard.operational_kpis = [
            self._build_kpi_card(
                "payment_success", "Payment Success Rate", MetricType.PAYMENT_SUCCESS_RATE,
                date_from, date_to, "%", compare_to_previous
            ),
            self._build_kpi_card(
                "housekeeping_efficiency", "Housekeeping Efficiency", MetricType.HOUSEKEEPING_EFFICIENCY,
                date_from, date_to, "%", compare_to_previous
            ),
        ]
        
        # Remove None entries (metrics with no data)
        dashboard.revenue_kpis = [k for k in dashboard.revenue_kpis if k]
        dashboard.booking_kpis = [k for k in dashboard.booking_kpis if k]
        dashboard.occupancy_kpis = [k for k in dashboard.occupancy_kpis if k]
        dashboard.satisfaction_kpis = [k for k in dashboard.satisfaction_kpis if k]
        dashboard.operational_kpis = [k for k in dashboard.operational_kpis if k]
        
        return dashboard
    
    def _build_kpi_card(
        self,
        id: str,
        title: str,
        metric_type: MetricType,
        date_from: datetime,
        date_to: datetime,
        unit: Optional[str],
        compare_to_previous: bool
    ) -> Optional[KPICard]:
        """Build a single KPI card with optional comparison."""
        metric = self.get_metric(metric_type)
        
        if not metric:
            # Return placeholder with zero value
            return KPICard(
                id=id,
                title=title,
                metric_type=metric_type,
                value=0,
                formatted_value=self._format_value(0, unit),
                unit=unit,
                updated_at=datetime.utcnow()
            )
        
        # Get sparkline data (last 7 days)
        sparkline_data = self._get_sparkline(metric_type, 7)
        
        return KPICard(
            id=id,
            title=title,
            metric_type=metric_type,
            value=metric.current_value,
            formatted_value=self._format_value(metric.current_value, unit),
            unit=unit,
            change_percent=metric.change_percent,
            trend=metric.trend,
            sparkline=sparkline_data,
            updated_at=metric.updated_at
        )
    
    def _format_value(self, value: float, unit: Optional[str]) -> str:
        """Format metric value for display."""
        if unit == "$":
            return f"${value:,.2f}"
        elif unit == "%":
            return f"{value:.1f}%"
        elif unit == "/5":
            return f"{value:.1f}/5"
        else:
            if value >= 1000000:
                return f"{value/1000000:.1f}M"
            elif value >= 1000:
                return f"{value/1000:.1f}K"
            return f"{value:,.0f}"
    
    def _get_sparkline(self, metric_type: MetricType, days: int) -> List[float]:
        """Get sparkline data for a metric."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        snapshots = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.metric_type == metric_type,
            MetricSnapshot.granularity == Granularity.DAILY,
            MetricSnapshot.period_start >= start_date
        ).order_by(MetricSnapshot.period_start).all()
        
        if snapshots:
            return [s.value for s in snapshots]
        
        # Generate mock sparkline data
        base_value = self._get_mock_base_value(metric_type)
        sparkline = []
        current_value = base_value
        for _ in range(days):
            # Add some variation
            change = random.uniform(-0.05, 0.05) * current_value
            current_value = max(0, current_value + change)
            sparkline.append(round(current_value, 2))
        return sparkline
    
    def _generate_mock_metric(self, metric_type: MetricType) -> MetricResponse:
        """Generate realistic mock data for a metric."""
        base_value = self._get_mock_base_value(metric_type)
        previous_value = base_value * random.uniform(0.85, 1.15)
        change_percent = ((base_value - previous_value) / previous_value) * 100 if previous_value > 0 else 0
        
        if abs(change_percent) < 2:
            trend = "stable"
        elif change_percent > 0:
            trend = "up"
        else:
            trend = "down"
        
        return MetricResponse(
            metric_type=metric_type,
            current_value=round(base_value, 2),
            previous_value=round(previous_value, 2),
            change_percent=round(change_percent, 2),
            trend=trend,
            updated_at=datetime.utcnow(),
            data_freshness=datetime.utcnow()
        )
    
    def _generate_mock_time_series(
        self,
        metric_type: MetricType,
        granularity: Granularity,
        period_start: datetime,
        period_end: datetime
    ) -> TimeSeriesData:
        """Generate mock time series data for charts."""
        base_value = self._get_mock_base_value(metric_type)
        data_points = []
        current_date = period_start
        current_value = base_value
        
        # Calculate step based on granularity
        if granularity == Granularity.HOURLY:
            step = timedelta(hours=1)
        elif granularity == Granularity.DAILY:
            step = timedelta(days=1)
        elif granularity == Granularity.WEEKLY:
            step = timedelta(weeks=1)
        else:  # MONTHLY
            step = timedelta(days=30)
        
        while current_date <= period_end:
            # Add realistic variation with some trend
            variation = random.uniform(-0.08, 0.08) * current_value
            # Slight upward trend over time
            trend_factor = 1 + (random.uniform(0, 0.02))
            current_value = max(0, current_value * trend_factor + variation)
            
            data_points.append(TimeSeriesDataPoint(
                timestamp=current_date,
                value=round(current_value, 2),
                count=random.randint(10, 100)
            ))
            
            current_date += step
        
        return TimeSeriesData(
            metric_type=metric_type,
            granularity=granularity,
            data_points=data_points,
            period_start=period_start,
            period_end=period_end
        )
    
    def _get_mock_base_value(self, metric_type: MetricType) -> float:
        """Get realistic base value for a metric type."""
        mock_values = {
            # Revenue Metrics
            MetricType.TOTAL_REVENUE: 125000.0,
            MetricType.AVERAGE_ORDER_VALUE: 185.50,
            MetricType.REVENUE_PER_ROOM: 320.00,
            MetricType.REVPAR: 285.75,
            
            # Booking Metrics
            MetricType.TOTAL_BOOKINGS: 1250,
            MetricType.BOOKING_CONVERSION_RATE: 12.5,
            MetricType.CANCELLATION_RATE: 4.2,
            MetricType.AVERAGE_LEAD_TIME: 14.5,
            
            # Occupancy Metrics
            MetricType.OCCUPANCY_RATE: 78.5,
            MetricType.AVERAGE_DAILY_RATE: 245.00,
            
            # Guest Metrics
            MetricType.GUEST_SATISFACTION: 4.3,
            MetricType.NET_PROMOTER_SCORE: 68,
            MetricType.REPEAT_GUEST_RATE: 42.5,
            
            # Operational Metrics
            MetricType.HOUSEKEEPING_EFFICIENCY: 92.5,
            MetricType.MAINTENANCE_RESPONSE_TIME: 2.5,  # hours
            MetricType.CHECK_IN_TIME: 3.2,  # minutes
            
            # Payment Metrics
            MetricType.PAYMENT_SUCCESS_RATE: 98.2,
            MetricType.REFUND_RATE: 2.1,
            MetricType.AVERAGE_PAYMENT_TIME: 1.8,  # seconds
        }
        
        base = mock_values.get(metric_type, 100.0)
        # Add some random variation (±10%)
        return base * random.uniform(0.9, 1.1)
