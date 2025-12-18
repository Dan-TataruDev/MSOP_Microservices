"""
Schemas for reports API.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.reports import ReportType, ReportStatus


class ReportRequest(BaseModel):
    """Request to generate a new report."""
    report_type: ReportType
    name: Optional[str] = None
    period_start: datetime
    period_end: datetime
    parameters: Dict[str, Any] = {}
    is_public: bool = False


class ReportSummary(BaseModel):
    """Summary of a report (without full data)."""
    id: UUID
    report_type: ReportType
    name: str
    status: ReportStatus
    period_start: datetime
    period_end: datetime
    created_at: datetime
    generation_completed_at: Optional[datetime] = None
    generation_time_ms: Optional[int] = None
    
    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    """Full report response with data."""
    id: UUID
    report_type: ReportType
    name: str
    description: Optional[str] = None
    status: ReportStatus
    
    # Report content
    data: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    
    # Time range
    period_start: datetime
    period_end: datetime
    
    # Metadata
    parameters: Dict[str, Any] = {}
    created_at: datetime
    generation_completed_at: Optional[datetime] = None
    generation_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """List of reports with pagination."""
    reports: List[ReportSummary]
    total: int
    page: int
    page_size: int
    has_more: bool


class ScheduledReportCreate(BaseModel):
    """Create a scheduled report."""
    name: str
    report_type: ReportType
    schedule_cron: str = Field(..., description="Cron expression (e.g., '0 8 * * *' for daily at 8 AM)")
    parameters: Dict[str, Any] = {}
    recipients: List[str] = []
    is_active: bool = True


class ScheduledReportResponse(BaseModel):
    """Scheduled report response."""
    id: UUID
    name: str
    report_type: ReportType
    schedule_cron: str
    parameters: Dict[str, Any] = {}
    recipients: List[str] = []
    is_active: bool
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
