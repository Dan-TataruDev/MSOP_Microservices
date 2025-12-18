"""Pydantic schemas for cleaning schedule operations."""
from datetime import datetime, time
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.schedule import ScheduleStatus, RecurrencePattern


class ScheduleBase(BaseModel):
    """Base schema for schedule data."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    venue_type: str
    venue_ids: Optional[List[UUID]] = None
    floor_numbers: Optional[List[int]] = None
    cleaning_type: str
    estimated_duration_minutes: int = Field(default=30, ge=5, le=480)
    priority_level: str = "normal"
    recurrence_pattern: RecurrencePattern
    days_of_week: Optional[List[int]] = Field(None, description="0=Monday, 6=Sunday")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    preferred_time: Optional[time] = None
    trigger_on_checkout: bool = False
    trigger_on_checkin: bool = False
    trigger_time_based: bool = True
    must_complete_by_time: Optional[time] = None
    sla_minutes: Optional[int] = None
    special_instructions: Optional[str] = None


class ScheduleCreate(ScheduleBase):
    """Schema for creating a new schedule."""
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ScheduleStatus] = None
    venue_ids: Optional[List[UUID]] = None
    floor_numbers: Optional[List[int]] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    priority_level: Optional[str] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    preferred_time: Optional[time] = None
    trigger_on_checkout: Optional[bool] = None
    trigger_on_checkin: Optional[bool] = None
    trigger_time_based: Optional[bool] = None
    must_complete_by_time: Optional[time] = None
    sla_minutes: Optional[int] = None
    special_instructions: Optional[str] = None
    effective_until: Optional[datetime] = None


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    id: UUID
    schedule_reference: str
    name: str
    description: Optional[str]
    status: ScheduleStatus
    venue_type: str
    venue_ids: Optional[List[UUID]]
    floor_numbers: Optional[List[int]]
    cleaning_type: str
    estimated_duration_minutes: int
    priority_level: str
    recurrence_pattern: RecurrencePattern
    days_of_week: Optional[List[int]]
    day_of_month: Optional[int]
    preferred_time: Optional[time]
    trigger_on_checkout: bool
    trigger_on_checkin: bool
    trigger_time_based: bool
    must_complete_by_time: Optional[time]
    sla_minutes: Optional[int]
    special_instructions: Optional[str]
    effective_from: datetime
    effective_until: Optional[datetime]
    tasks_generated_count: int
    last_task_generated_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ScheduleListResponse(BaseModel):
    """Schema for paginated schedule list response."""
    schedules: List[ScheduleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
