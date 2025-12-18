"""Pydantic schemas for dashboard and reporting operations."""
from datetime import datetime, date
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel
from app.models.task import TaskStatus, TaskType, TaskPriority
from app.models.maintenance import MaintenanceCategory, MaintenanceStatus


class TaskCountByStatus(BaseModel):
    """Task counts grouped by status."""
    pending: int = 0
    assigned: int = 0
    in_progress: int = 0
    on_hold: int = 0
    completed: int = 0
    verified: int = 0
    delayed: int = 0
    cancelled: int = 0


class TaskCountByType(BaseModel):
    """Task counts grouped by type."""
    checkout_cleaning: int = 0
    stay_over_cleaning: int = 0
    deep_cleaning: int = 0
    turndown_service: int = 0
    inspection: int = 0
    maintenance_repair: int = 0
    preventive_maintenance: int = 0
    restocking: int = 0
    public_area_cleaning: int = 0


class MaintenanceCountByCategory(BaseModel):
    """Maintenance request counts grouped by category."""
    plumbing: int = 0
    electrical: int = 0
    hvac: int = 0
    appliance: int = 0
    furniture: int = 0
    structural: int = 0
    safety: int = 0
    cosmetic: int = 0
    it_equipment: int = 0
    other: int = 0


class TaskMetrics(BaseModel):
    """Key task performance metrics."""
    total_tasks_today: int
    completed_tasks_today: int
    pending_tasks: int
    overdue_tasks: int
    delayed_tasks: int
    average_completion_time_minutes: Optional[float]
    on_time_completion_rate: float  # Percentage
    tasks_by_status: TaskCountByStatus
    tasks_by_type: TaskCountByType
    vip_tasks_pending: int


class MaintenanceMetrics(BaseModel):
    """Key maintenance performance metrics."""
    total_requests_today: int
    open_requests: int
    critical_requests: int
    overdue_requests: int
    average_resolution_time_minutes: Optional[float]
    sla_compliance_rate: float  # Percentage
    requests_by_category: MaintenanceCountByCategory
    safety_concerns_open: int


class StaffWorkload(BaseModel):
    """Staff workload summary."""
    staff_id: UUID
    staff_name: str
    role: str
    is_on_duty: bool
    assigned_tasks_count: int
    completed_tasks_today: int
    in_progress_task_id: Optional[UUID]
    current_location: Optional[str]
    efficiency_score: Optional[float]  # Based on estimated vs actual time


class StaffWorkloadSummary(BaseModel):
    """Summary of all staff workloads."""
    total_staff_on_duty: int
    total_staff_available: int
    staff_workloads: List[StaffWorkload]
    average_tasks_per_staff: float
    overloaded_staff_count: int


class FloorSummary(BaseModel):
    """Task summary by floor."""
    floor_number: int
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
    rooms_needing_cleaning: int
    maintenance_issues: int


class DashboardSummary(BaseModel):
    """Comprehensive dashboard summary for operations managers."""
    generated_at: datetime
    date: date
    task_metrics: TaskMetrics
    maintenance_metrics: MaintenanceMetrics
    staff_summary: StaffWorkloadSummary
    floors_summary: List[FloorSummary]
    upcoming_checkouts: int
    rooms_ready: int
    rooms_pending_cleaning: int
    critical_alerts: List[str]


class OperationalReport(BaseModel):
    """Detailed operational report for specified period."""
    report_period_start: datetime
    report_period_end: datetime
    generated_at: datetime
    
    # Task statistics
    total_tasks_created: int
    total_tasks_completed: int
    total_tasks_cancelled: int
    average_task_duration_minutes: float
    on_time_completion_rate: float
    
    # Task breakdowns
    tasks_by_type: Dict[str, int]
    tasks_by_priority: Dict[str, int]
    tasks_by_floor: Dict[int, int]
    
    # Maintenance statistics
    total_maintenance_requests: int
    maintenance_completed: int
    maintenance_pending: int
    average_resolution_time_hours: float
    sla_compliance_rate: float
    
    # Maintenance breakdowns
    maintenance_by_category: Dict[str, int]
    maintenance_by_priority: Dict[str, int]
    
    # Staff performance
    top_performers: List[Dict]
    staff_efficiency_average: float
    
    # Issues and insights
    recurring_maintenance_issues: List[Dict]
    frequently_delayed_task_types: List[str]
    recommendations: List[str]


class RealTimeStatus(BaseModel):
    """Real-time operational status for live dashboards."""
    timestamp: datetime
    active_tasks_count: int
    staff_on_duty_count: int
    tasks_in_progress: List[Dict]
    recent_completions: List[Dict]
    alerts: List[Dict]
    estimated_completion_backlog_minutes: int


class TaskTrendData(BaseModel):
    """Task trend data for charts."""
    date: date
    created: int
    completed: int
    delayed: int
    average_duration: Optional[float]


class TrendReport(BaseModel):
    """Trend report for analytics dashboards."""
    period_start: date
    period_end: date
    daily_trends: List[TaskTrendData]
    week_over_week_change: float
    busiest_day: str
    peak_hours: List[int]
