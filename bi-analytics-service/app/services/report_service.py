"""
Service for generating and managing reports.

Design:
- Asynchronous report generation
- Template-based report structures
- Caching of completed reports
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.models.reports import Report, ReportType, ReportStatus, ScheduledReport
from app.models.metrics import MetricSnapshot, MetricType, Granularity
from app.schemas.reports import (
    ReportRequest, ReportResponse, ReportSummary, 
    ReportListResponse, ScheduledReportCreate, ScheduledReportResponse
)

logger = logging.getLogger(__name__)


class ReportService:
    """Service for report generation and management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_report(
        self, 
        request: ReportRequest,
        user_id: Optional[UUID] = None
    ) -> ReportResponse:
        """Create a new report request."""
        # Generate report name if not provided
        name = request.name or f"{request.report_type.value} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        
        report = Report(
            report_type=request.report_type,
            name=name,
            period_start=request.period_start,
            period_end=request.period_end,
            parameters=request.parameters,
            is_public=request.is_public,
            created_by=user_id,
            status=ReportStatus.PENDING,
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        # In production, queue report generation as background task
        # For now, generate synchronously
        self._generate_report(report)
        
        return ReportResponse.model_validate(report)
    
    def get_report(self, report_id: UUID) -> Optional[ReportResponse]:
        """Get a report by ID."""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if report:
            return ReportResponse.model_validate(report)
        return None
    
    def list_reports(
        self,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> ReportListResponse:
        """List reports with filtering and pagination."""
        query = self.db.query(Report)
        
        if report_type:
            query = query.filter(Report.report_type == report_type)
        if status:
            query = query.filter(Report.status == status)
        
        total = query.count()
        reports = query.order_by(desc(Report.created_at))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return ReportListResponse(
            reports=[ReportSummary.model_validate(r) for r in reports],
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total
        )
    
    def _generate_report(self, report: Report) -> None:
        """Generate report data."""
        report.status = ReportStatus.GENERATING
        report.generation_started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            start_time = datetime.utcnow()
            
            # Generate report based on type
            if report.report_type == ReportType.DAILY_SUMMARY:
                data, summary = self._generate_daily_summary(
                    report.period_start, report.period_end
                )
            elif report.report_type == ReportType.REVENUE_REPORT:
                data, summary = self._generate_revenue_report(
                    report.period_start, report.period_end
                )
            elif report.report_type == ReportType.OCCUPANCY_REPORT:
                data, summary = self._generate_occupancy_report(
                    report.period_start, report.period_end
                )
            elif report.report_type == ReportType.GUEST_SATISFACTION:
                data, summary = self._generate_satisfaction_report(
                    report.period_start, report.period_end
                )
            else:
                data, summary = self._generate_generic_report(
                    report.report_type, report.period_start, report.period_end
                )
            
            report.data = data
            report.summary = summary
            report.status = ReportStatus.COMPLETED
            report.generation_completed_at = datetime.utcnow()
            report.generation_time_ms = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}", exc_info=True)
            report.status = ReportStatus.FAILED
            report.error_message = str(e)
        
        self.db.commit()
    
    def _generate_daily_summary(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate daily summary report."""
        # Fetch metrics for the period
        metrics = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.granularity == Granularity.DAILY,
            MetricSnapshot.period_start >= period_start,
            MetricSnapshot.period_end <= period_end
        ).all()
        
        # Group metrics by type
        metrics_by_type: Dict[str, List[Dict]] = {}
        for m in metrics:
            key = m.metric_type.value
            if key not in metrics_by_type:
                metrics_by_type[key] = []
            metrics_by_type[key].append({
                "date": m.period_start.isoformat(),
                "value": m.value,
                "count": m.count
            })
        
        data = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "metrics": metrics_by_type
        }
        
        # Calculate summary statistics
        summary = {
            "total_days": (period_end - period_start).days,
            "metrics_count": len(metrics),
            "highlights": []
        }
        
        # Add highlights based on available data
        for metric_type, values in metrics_by_type.items():
            if values:
                avg = sum(v["value"] for v in values) / len(values)
                summary["highlights"].append({
                    "metric": metric_type,
                    "average": round(avg, 2),
                    "data_points": len(values)
                })
        
        return data, summary
    
    def _generate_revenue_report(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate revenue-focused report."""
        revenue_metrics = [
            MetricType.TOTAL_REVENUE,
            MetricType.AVERAGE_ORDER_VALUE,
            MetricType.REVPAR,
            MetricType.REVENUE_PER_ROOM
        ]
        
        metrics = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.metric_type.in_(revenue_metrics),
            MetricSnapshot.granularity == Granularity.DAILY,
            MetricSnapshot.period_start >= period_start,
            MetricSnapshot.period_end <= period_end
        ).all()
        
        # Calculate totals and trends
        total_revenue = sum(
            m.value for m in metrics 
            if m.metric_type == MetricType.TOTAL_REVENUE
        )
        
        data = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "total_revenue": total_revenue,
            "daily_breakdown": [
                {
                    "date": m.period_start.isoformat(),
                    "metric": m.metric_type.value,
                    "value": m.value
                }
                for m in metrics
            ]
        }
        
        summary = {
            "total_revenue": round(total_revenue, 2),
            "period_days": (period_end - period_start).days,
            "average_daily_revenue": round(
                total_revenue / max(1, (period_end - period_start).days), 2
            )
        }
        
        return data, summary
    
    def _generate_occupancy_report(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate occupancy report."""
        occupancy_metrics = [
            MetricType.OCCUPANCY_RATE,
            MetricType.AVERAGE_DAILY_RATE,
            MetricType.REVPAR
        ]
        
        metrics = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.metric_type.in_(occupancy_metrics),
            MetricSnapshot.granularity == Granularity.DAILY,
            MetricSnapshot.period_start >= period_start,
            MetricSnapshot.period_end <= period_end
        ).all()
        
        data = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "metrics": [
                {
                    "date": m.period_start.isoformat(),
                    "metric": m.metric_type.value,
                    "value": m.value
                }
                for m in metrics
            ]
        }
        
        # Calculate averages
        occupancy_values = [
            m.value for m in metrics 
            if m.metric_type == MetricType.OCCUPANCY_RATE
        ]
        
        summary = {
            "average_occupancy": round(
                sum(occupancy_values) / max(1, len(occupancy_values)), 2
            ) if occupancy_values else 0,
            "period_days": (period_end - period_start).days
        }
        
        return data, summary
    
    def _generate_satisfaction_report(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate guest satisfaction report."""
        satisfaction_metrics = [
            MetricType.GUEST_SATISFACTION,
            MetricType.NET_PROMOTER_SCORE,
            MetricType.REPEAT_GUEST_RATE
        ]
        
        metrics = self.db.query(MetricSnapshot).filter(
            MetricSnapshot.metric_type.in_(satisfaction_metrics),
            MetricSnapshot.granularity == Granularity.DAILY,
            MetricSnapshot.period_start >= period_start,
            MetricSnapshot.period_end <= period_end
        ).all()
        
        data = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "metrics": [
                {
                    "date": m.period_start.isoformat(),
                    "metric": m.metric_type.value,
                    "value": m.value,
                    "responses": m.count
                }
                for m in metrics
            ]
        }
        
        satisfaction_values = [
            m.value for m in metrics 
            if m.metric_type == MetricType.GUEST_SATISFACTION
        ]
        
        summary = {
            "average_satisfaction": round(
                sum(satisfaction_values) / max(1, len(satisfaction_values)), 2
            ) if satisfaction_values else 0,
            "total_responses": sum(m.count for m in metrics)
        }
        
        return data, summary
    
    def _generate_generic_report(
        self,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a generic report for other types."""
        data = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "report_type": report_type.value,
            "message": "Report generation not yet implemented for this type"
        }
        
        summary = {
            "status": "placeholder",
            "period_days": (period_end - period_start).days
        }
        
        return data, summary
    
    # Scheduled Reports
    def create_scheduled_report(
        self, 
        request: ScheduledReportCreate
    ) -> ScheduledReportResponse:
        """Create a scheduled report configuration."""
        scheduled = ScheduledReport(
            name=request.name,
            report_type=request.report_type,
            schedule_cron=request.schedule_cron,
            parameters=request.parameters,
            recipients=request.recipients,
            is_active=request.is_active,
        )
        
        self.db.add(scheduled)
        self.db.commit()
        self.db.refresh(scheduled)
        
        return ScheduledReportResponse.model_validate(scheduled)
    
    def list_scheduled_reports(self) -> List[ScheduledReportResponse]:
        """List all scheduled reports."""
        scheduled = self.db.query(ScheduledReport).all()
        return [ScheduledReportResponse.model_validate(s) for s in scheduled]
