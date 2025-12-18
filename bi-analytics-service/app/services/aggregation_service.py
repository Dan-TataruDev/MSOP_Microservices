"""
Service for aggregating raw events into metrics.

Design:
- Background processing to avoid blocking reads
- Incremental aggregation for efficiency
- Multiple granularity levels (hourly, daily, monthly)
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from app.models.events import IngestedEvent, EventSource
from app.models.metrics import MetricSnapshot, RealtimeMetric, MetricType, Granularity
from app.config import settings

logger = logging.getLogger(__name__)


class AggregationService:
    """Service for aggregating events into metrics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def run_aggregation(self, granularity: Granularity = Granularity.HOURLY) -> int:
        """
        Run aggregation for unprocessed events.
        
        Returns:
            Number of metrics updated
        """
        logger.info(f"Starting {granularity.value} aggregation...")
        
        # Get unprocessed events
        unprocessed = self.db.query(IngestedEvent).filter(
            IngestedEvent.processed == False
        ).limit(settings.batch_size).all()
        
        if not unprocessed:
            logger.info("No unprocessed events found")
            return 0
        
        metrics_updated = 0
        
        # Group events by source for specialized aggregation
        events_by_source: Dict[EventSource, List[IngestedEvent]] = {}
        for event in unprocessed:
            if event.source not in events_by_source:
                events_by_source[event.source] = []
            events_by_source[event.source].append(event)
        
        # Aggregate each source
        for source, events in events_by_source.items():
            try:
                count = self._aggregate_source(source, events, granularity)
                metrics_updated += count
            except Exception as e:
                logger.error(f"Error aggregating {source.value}: {str(e)}", exc_info=True)
        
        # Mark events as processed
        for event in unprocessed:
            event.processed = True
            event.processed_at = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Aggregation complete: {metrics_updated} metrics updated")
        
        return metrics_updated
    
    def _aggregate_source(
        self, 
        source: EventSource, 
        events: List[IngestedEvent],
        granularity: Granularity
    ) -> int:
        """Aggregate events from a specific source."""
        if source == EventSource.BOOKING:
            return self._aggregate_booking_events(events, granularity)
        elif source == EventSource.PAYMENT:
            return self._aggregate_payment_events(events, granularity)
        elif source == EventSource.FEEDBACK:
            return self._aggregate_feedback_events(events, granularity)
        elif source == EventSource.INVENTORY:
            return self._aggregate_inventory_events(events, granularity)
        else:
            logger.debug(f"No specific aggregation for source: {source.value}")
            return 0
    
    def _aggregate_booking_events(
        self, 
        events: List[IngestedEvent],
        granularity: Granularity
    ) -> int:
        """Aggregate booking-related metrics."""
        metrics_count = 0
        
        # Count bookings by type
        created_count = sum(1 for e in events if e.event_type == "booking.created")
        cancelled_count = sum(1 for e in events if e.event_type == "booking.cancelled")
        completed_count = sum(1 for e in events if e.event_type == "booking.completed")
        
        # Calculate time bucket
        now = datetime.utcnow()
        period_start, period_end = self._get_period_bounds(now, granularity)
        
        # Update total bookings metric
        if created_count > 0:
            self._upsert_metric(
                MetricType.TOTAL_BOOKINGS,
                granularity,
                period_start,
                period_end,
                created_count,
                increment=True
            )
            metrics_count += 1
        
        # Update cancellation rate
        if cancelled_count > 0 or created_count > 0:
            total = created_count + cancelled_count
            if total > 0:
                rate = (cancelled_count / total) * 100
                self._upsert_metric(
                    MetricType.CANCELLATION_RATE,
                    granularity,
                    period_start,
                    period_end,
                    rate
                )
                metrics_count += 1
        
        return metrics_count
    
    def _aggregate_payment_events(
        self, 
        events: List[IngestedEvent],
        granularity: Granularity
    ) -> int:
        """Aggregate payment-related metrics."""
        metrics_count = 0
        
        # Calculate revenue from completed payments
        completed_payments = [e for e in events if e.event_type == "payment.completed"]
        total_revenue = sum(
            e.payload.get("amount", 0) for e in completed_payments
        )
        
        # Count success/failure
        success_count = len(completed_payments)
        failed_count = sum(1 for e in events if e.event_type == "payment.failed")
        
        now = datetime.utcnow()
        period_start, period_end = self._get_period_bounds(now, granularity)
        
        # Update revenue metric
        if total_revenue > 0:
            self._upsert_metric(
                MetricType.TOTAL_REVENUE,
                granularity,
                period_start,
                period_end,
                total_revenue,
                increment=True
            )
            metrics_count += 1
            
            # Calculate average order value
            if success_count > 0:
                avg_value = total_revenue / success_count
                self._upsert_metric(
                    MetricType.AVERAGE_ORDER_VALUE,
                    granularity,
                    period_start,
                    period_end,
                    avg_value
                )
                metrics_count += 1
        
        # Update payment success rate
        total_attempts = success_count + failed_count
        if total_attempts > 0:
            success_rate = (success_count / total_attempts) * 100
            self._upsert_metric(
                MetricType.PAYMENT_SUCCESS_RATE,
                granularity,
                period_start,
                period_end,
                success_rate
            )
            metrics_count += 1
        
        return metrics_count
    
    def _aggregate_feedback_events(
        self, 
        events: List[IngestedEvent],
        granularity: Granularity
    ) -> int:
        """Aggregate feedback and satisfaction metrics."""
        metrics_count = 0
        
        feedback_events = [e for e in events if e.event_type == "feedback.submitted"]
        
        if not feedback_events:
            return 0
        
        # Calculate average satisfaction rating
        ratings = [
            e.payload.get("rating", 0) 
            for e in feedback_events 
            if e.payload.get("rating")
        ]
        
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            now = datetime.utcnow()
            period_start, period_end = self._get_period_bounds(now, granularity)
            
            self._upsert_metric(
                MetricType.GUEST_SATISFACTION,
                granularity,
                period_start,
                period_end,
                avg_rating,
                count=len(ratings)
            )
            metrics_count += 1
        
        return metrics_count
    
    def _aggregate_inventory_events(
        self, 
        events: List[IngestedEvent],
        granularity: Granularity
    ) -> int:
        """Aggregate inventory and occupancy metrics."""
        # Placeholder for occupancy calculations
        # Would need room availability data
        return 0
    
    def _get_period_bounds(
        self, 
        timestamp: datetime, 
        granularity: Granularity
    ) -> tuple[datetime, datetime]:
        """Get start and end of period for given granularity."""
        if granularity == Granularity.HOURLY:
            start = timestamp.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)
        elif granularity == Granularity.DAILY:
            start = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif granularity == Granularity.WEEKLY:
            start = timestamp - timedelta(days=timestamp.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(weeks=1)
        else:  # MONTHLY
            start = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        
        return start, end
    
    def _upsert_metric(
        self,
        metric_type: MetricType,
        granularity: Granularity,
        period_start: datetime,
        period_end: datetime,
        value: float,
        count: int = 1,
        increment: bool = False,
        dimensions: Dict[str, Any] = None
    ) -> MetricSnapshot:
        """Insert or update a metric snapshot."""
        existing = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.metric_type == metric_type,
            MetricSnapshot.granularity == granularity,
            MetricSnapshot.period_start == period_start,
        ).first()
        
        if existing:
            if increment:
                existing.value += value
                existing.count += count
            else:
                # For averages, compute weighted average
                total_count = existing.count + count
                existing.value = (
                    (existing.value * existing.count + value * count) / total_count
                )
                existing.count = total_count
            
            existing.computed_at = datetime.utcnow()
            existing.data_freshness = datetime.utcnow()
            
            if existing.min_value is None or value < existing.min_value:
                existing.min_value = value
            if existing.max_value is None or value > existing.max_value:
                existing.max_value = value
            
            return existing
        else:
            snapshot = MetricSnapshot(
                metric_type=metric_type,
                granularity=granularity,
                period_start=period_start,
                period_end=period_end,
                value=value,
                count=count,
                min_value=value,
                max_value=value,
                dimensions=dimensions or {},
                data_freshness=datetime.utcnow(),
            )
            self.db.add(snapshot)
            return snapshot
    
    def update_realtime_metric(
        self, 
        metric_type: MetricType, 
        value: float
    ) -> RealtimeMetric:
        """Update a real-time metric for live dashboards."""
        existing = self.db.query(RealtimeMetric).filter(
            RealtimeMetric.metric_type == metric_type
        ).first()
        
        if existing:
            existing.previous_value = existing.value
            existing.value = value
            
            if existing.previous_value and existing.previous_value != 0:
                change = ((value - existing.previous_value) / existing.previous_value) * 100
                existing.change_percent = round(change, 2)
                existing.trend = "up" if change > 0 else ("down" if change < 0 else "stable")
            
            return existing
        else:
            metric = RealtimeMetric(
                metric_type=metric_type,
                value=value,
            )
            self.db.add(metric)
            return metric
