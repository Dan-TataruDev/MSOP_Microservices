"""API endpoints for operational dashboards and reporting."""
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.dashboard import (
    DashboardSummary, OperationalReport, RealTimeStatus, TrendReport
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    target_date: Optional[date] = Query(None, description="Date for summary (defaults to today)"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard summary for operations managers.
    
    Includes:
    - Task metrics (total, completed, pending, overdue, delayed)
    - Maintenance metrics (open requests, critical issues, SLA compliance)
    - Staff workload summary
    - Floor-by-floor breakdown
    - Room status (ready, pending cleaning)
    - Critical alerts
    
    This endpoint is designed to power the main operations dashboard
    providing a single-call overview of all operational metrics.
    """
    service = DashboardService(db)
    return service.get_dashboard_summary(target_date)


@router.get("/real-time", response_model=RealTimeStatus)
def get_real_time_status(db: Session = Depends(get_db)):
    """
    Get real-time operational status for live dashboards.
    
    Optimized for frequent polling (recommended: 30-second intervals).
    
    Returns:
    - Active task count
    - Staff on duty
    - Tasks currently in progress
    - Recent completions (last hour)
    - Active alerts
    - Estimated backlog time
    """
    service = DashboardService(db)
    return service.get_real_time_status()


@router.get("/report", response_model=OperationalReport)
def get_operational_report(
    start_date: datetime = Query(..., description="Report period start"),
    end_date: datetime = Query(..., description="Report period end"),
    db: Session = Depends(get_db)
):
    """
    Generate detailed operational report for a specified period.
    
    Comprehensive report including:
    - Task statistics (created, completed, cancelled, avg duration)
    - On-time completion rate
    - Tasks breakdown by type, priority, and floor
    - Maintenance statistics
    - SLA compliance rates
    - Maintenance breakdown by category and priority
    
    Useful for:
    - Daily/weekly/monthly operational reviews
    - Performance analysis
    - Resource planning
    """
    service = DashboardService(db)
    return service.get_operational_report(start_date, end_date)


@router.get("/report/daily")
def get_daily_report(
    target_date: Optional[date] = Query(None, description="Date for report (defaults to today)"),
    db: Session = Depends(get_db)
):
    """Get operational report for a single day."""
    target = target_date or date.today()
    start = datetime.combine(target, datetime.min.time())
    end = datetime.combine(target, datetime.max.time())
    
    service = DashboardService(db)
    return service.get_operational_report(start, end)


@router.get("/report/weekly")
def get_weekly_report(
    weeks_ago: int = Query(0, ge=0, le=52, description="Number of weeks ago (0 = current week)"),
    db: Session = Depends(get_db)
):
    """Get operational report for a week."""
    today = date.today()
    # Start of week (Monday)
    start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=weeks_ago)
    end_of_week = start_of_week + timedelta(days=6)
    
    start = datetime.combine(start_of_week, datetime.min.time())
    end = datetime.combine(end_of_week, datetime.max.time())
    
    service = DashboardService(db)
    return service.get_operational_report(start, end)


@router.get("/report/monthly")
def get_monthly_report(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Get operational report for a month."""
    start = datetime(year, month, 1)
    # Get last day of month
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    service = DashboardService(db)
    return service.get_operational_report(start, end)


@router.get("/metrics/tasks")
def get_task_metrics(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get task metrics only (lighter than full summary)."""
    target = target_date or date.today()
    day_start = datetime.combine(target, datetime.min.time())
    day_end = datetime.combine(target, datetime.max.time())
    
    service = DashboardService(db)
    return service._get_task_metrics(day_start, day_end)


@router.get("/metrics/maintenance")
def get_maintenance_metrics(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get maintenance metrics only (lighter than full summary)."""
    target = target_date or date.today()
    day_start = datetime.combine(target, datetime.min.time())
    day_end = datetime.combine(target, datetime.max.time())
    
    service = DashboardService(db)
    return service._get_maintenance_metrics(day_start, day_end)


@router.get("/metrics/staff")
def get_staff_workload(db: Session = Depends(get_db)):
    """Get staff workload summary."""
    service = DashboardService(db)
    return service._get_staff_workload_summary()


@router.get("/alerts")
def get_critical_alerts(db: Session = Depends(get_db)):
    """Get current critical alerts."""
    service = DashboardService(db)
    return {"alerts": service._get_critical_alerts()}
