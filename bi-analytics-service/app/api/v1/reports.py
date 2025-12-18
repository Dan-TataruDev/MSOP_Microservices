"""
API endpoints for reports.

Reports are generated asynchronously and can be retrieved
once generation is complete.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, get_read_db
from app.services.report_service import ReportService
from app.schemas.reports import (
    ReportRequest, ReportResponse, ReportListResponse,
    ScheduledReportCreate, ScheduledReportResponse
)
from app.models.reports import ReportType, ReportStatus

router = APIRouter()


@router.post("/reports", response_model=ReportResponse, status_code=201)
def create_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new report request.
    
    The report will be generated asynchronously. Use the returned
    report ID to check status and retrieve results.
    
    Report types:
    - daily_summary: Overview of daily metrics
    - weekly_summary: Weekly aggregated metrics
    - monthly_summary: Monthly performance report
    - revenue_report: Detailed revenue analysis
    - occupancy_report: Room occupancy analysis
    - guest_satisfaction: Guest feedback analysis
    - operational_efficiency: Operations performance
    - custom: Custom report with specified parameters
    """
    service = ReportService(db)
    return service.create_report(request)


@router.get("/reports", response_model=ReportListResponse)
def list_reports(
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_read_db)
):
    """
    List all reports with optional filtering.
    
    Returns paginated list of reports ordered by creation date.
    """
    service = ReportService(db)
    return service.list_reports(
        report_type=report_type,
        status=status,
        page=page,
        page_size=page_size
    )


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_read_db)
):
    """
    Get a report by ID.
    
    Returns the full report including data if generation is complete.
    Check the 'status' field to see if report is ready.
    """
    service = ReportService(db)
    report = service.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.delete("/reports/{report_id}", status_code=204)
def delete_report(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a report.
    
    Removes the report and its data from the system.
    """
    from app.models.reports import Report
    
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()


# Scheduled Reports

@router.post("/reports/scheduled", response_model=ScheduledReportResponse, status_code=201)
def create_scheduled_report(
    request: ScheduledReportCreate,
    db: Session = Depends(get_db)
):
    """
    Create a scheduled report configuration.
    
    The report will be generated automatically according to
    the specified cron schedule.
    
    Cron format: minute hour day month weekday
    Examples:
    - "0 8 * * *" - Daily at 8 AM
    - "0 8 * * 1" - Weekly on Monday at 8 AM
    - "0 8 1 * *" - Monthly on the 1st at 8 AM
    """
    service = ReportService(db)
    return service.create_scheduled_report(request)


@router.get("/reports/scheduled", response_model=list[ScheduledReportResponse])
def list_scheduled_reports(db: Session = Depends(get_read_db)):
    """
    List all scheduled report configurations.
    """
    service = ReportService(db)
    return service.list_scheduled_reports()


@router.put("/reports/scheduled/{schedule_id}", response_model=ScheduledReportResponse)
def update_scheduled_report(
    schedule_id: UUID,
    request: ScheduledReportCreate,
    db: Session = Depends(get_db)
):
    """
    Update a scheduled report configuration.
    """
    from app.models.reports import ScheduledReport
    
    scheduled = db.query(ScheduledReport).filter(
        ScheduledReport.id == schedule_id
    ).first()
    
    if not scheduled:
        raise HTTPException(status_code=404, detail="Scheduled report not found")
    
    scheduled.name = request.name
    scheduled.report_type = request.report_type
    scheduled.schedule_cron = request.schedule_cron
    scheduled.parameters = request.parameters
    scheduled.recipients = request.recipients
    scheduled.is_active = request.is_active
    
    db.commit()
    db.refresh(scheduled)
    
    return ScheduledReportResponse.model_validate(scheduled)


@router.delete("/reports/scheduled/{schedule_id}", status_code=204)
def delete_scheduled_report(
    schedule_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a scheduled report configuration.
    """
    from app.models.reports import ScheduledReport
    
    scheduled = db.query(ScheduledReport).filter(
        ScheduledReport.id == schedule_id
    ).first()
    
    if not scheduled:
        raise HTTPException(status_code=404, detail="Scheduled report not found")
    
    db.delete(scheduled)
    db.commit()
