"""Pydantic schemas for Housekeeping & Maintenance Service."""
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskAssignment,
)
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleListResponse,
)
from app.schemas.maintenance import (
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
    MaintenanceRequestResponse,
    MaintenanceRequestListResponse,
)
from app.schemas.dashboard import (
    DashboardSummary,
    TaskMetrics,
    StaffWorkload,
    OperationalReport,
)

__all__ = [
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskAssignment",
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "ScheduleListResponse",
    "MaintenanceRequestCreate",
    "MaintenanceRequestUpdate",
    "MaintenanceRequestResponse",
    "MaintenanceRequestListResponse",
    "DashboardSummary",
    "TaskMetrics",
    "StaffWorkload",
    "OperationalReport",
]
