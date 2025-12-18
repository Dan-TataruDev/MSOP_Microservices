"""
Models for reports and scheduled analytics.

Design:
- Pre-generated reports for fast access
- Scheduled report generation to offload computation
- Report templates for consistency
"""
import enum
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Text, Enum, Index, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class ReportType(str, enum.Enum):
    """Types of reports available."""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"
    REVENUE_REPORT = "revenue_report"
    OCCUPANCY_REPORT = "occupancy_report"
    GUEST_SATISFACTION = "guest_satisfaction"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    CUSTOM = "custom"


class ReportStatus(str, enum.Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """
    Pre-generated reports for business users.
    
    Reports are generated asynchronously and cached.
    Users can request reports and retrieve them when ready.
    """
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Report identification
    report_type = Column(Enum(ReportType), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Report parameters
    parameters = Column(JSON, default={})  # Date range, filters, etc.
    
    # Report data
    data = Column(JSON, nullable=True)  # Report content
    summary = Column(JSON, nullable=True)  # Key highlights
    
    # Time range covered
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Generation status
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, index=True)
    generation_started_at = Column(DateTime, nullable=True)
    generation_completed_at = Column(DateTime, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Access control
    created_by = Column(UUID(as_uuid=True), nullable=True)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Auto-cleanup old reports
    
    __table_args__ = (
        Index('ix_report_type_period', 'report_type', 'period_start', 'period_end'),
        Index('ix_report_status', 'status', 'created_at'),
    )


class ScheduledReport(Base):
    """
    Scheduled report configurations.
    
    Defines reports that should be generated automatically.
    """
    __tablename__ = "scheduled_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Schedule configuration
    name = Column(String(200), nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    schedule_cron = Column(String(50), nullable=False)  # Cron expression
    
    # Report parameters
    parameters = Column(JSON, default={})
    
    # Recipients
    recipients = Column(JSON, default=[])  # List of user IDs or emails
    
    # Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_report_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
