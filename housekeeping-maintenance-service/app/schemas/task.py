"""Pydantic schemas for task operations."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.task import TaskType, TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base schema for task data."""
    task_type: TaskType
    priority: TaskPriority = TaskPriority.NORMAL
    venue_id: Optional[UUID] = None
    venue_type: Optional[str] = None
    location_name: Optional[str] = None
    floor_number: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    is_vip: bool = False
    scheduled_date: datetime
    due_date: datetime
    estimated_duration_minutes: int = Field(default=30, ge=5, le=480)


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    source_event_type: Optional[str] = None
    source_booking_reference: Optional[str] = None
    source_maintenance_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_staff_id: Optional[UUID] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    completion_notes: Optional[str] = None
    issues_found: Optional[str] = None
    delay_reason: Optional[str] = None


class TaskAssignment(BaseModel):
    """Schema for task assignment."""
    staff_id: UUID
    notes: Optional[str] = None


class TaskCompletion(BaseModel):
    """Schema for completing a task."""
    completion_notes: Optional[str] = None
    issues_found: Optional[str] = None
    actual_duration_minutes: Optional[int] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    task_reference: str
    task_type: TaskType
    status: TaskStatus
    priority: TaskPriority
    venue_id: Optional[UUID]
    venue_type: Optional[str]
    location_name: Optional[str]
    floor_number: Optional[int]
    source_event_type: Optional[str]
    source_booking_reference: Optional[str]
    source_maintenance_id: Optional[UUID]
    title: str
    description: Optional[str]
    special_instructions: Optional[str]
    is_vip: bool
    assigned_staff_id: Optional[UUID]
    assigned_at: Optional[datetime]
    scheduled_date: datetime
    due_date: datetime
    estimated_duration_minutes: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    verified_at: Optional[datetime]
    is_delayed: bool
    delay_reason: Optional[str]
    completion_notes: Optional[str]
    issues_found: Optional[str]
    is_overdue: bool
    actual_duration_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TaskFilter(BaseModel):
    """Schema for filtering tasks."""
    task_types: Optional[List[TaskType]] = None
    statuses: Optional[List[TaskStatus]] = None
    priorities: Optional[List[TaskPriority]] = None
    venue_id: Optional[UUID] = None
    floor_number: Optional[int] = None
    assigned_staff_id: Optional[UUID] = None
    is_vip: Optional[bool] = None
    is_overdue: Optional[bool] = None
    scheduled_date_from: Optional[datetime] = None
    scheduled_date_to: Optional[datetime] = None
