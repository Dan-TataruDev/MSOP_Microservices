"""Pydantic schemas for maintenance request operations."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.maintenance import MaintenanceCategory, MaintenanceStatus, MaintenancePriority


class MaintenanceRequestBase(BaseModel):
    """Base schema for maintenance request data."""
    category: MaintenanceCategory
    priority: MaintenancePriority = MaintenancePriority.NORMAL
    venue_id: Optional[UUID] = None
    venue_type: Optional[str] = None
    location_name: Optional[str] = None
    floor_number: Optional[int] = None
    specific_location: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    affects_room_availability: bool = False
    guest_impact_level: Optional[str] = None
    safety_concern: bool = False


class MaintenanceRequestCreate(MaintenanceRequestBase):
    """Schema for creating a new maintenance request."""
    reported_by_staff_id: Optional[UUID] = None
    reported_by_guest_id: Optional[UUID] = None
    source_event_type: Optional[str] = None
    source_task_id: Optional[UUID] = None


class MaintenanceRequestUpdate(BaseModel):
    """Schema for updating a maintenance request."""
    status: Optional[MaintenanceStatus] = None
    priority: Optional[MaintenancePriority] = None
    category: Optional[MaintenanceCategory] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    specific_location: Optional[str] = None
    affects_room_availability: Optional[bool] = None
    guest_impact_level: Optional[str] = None
    safety_concern: Optional[bool] = None
    assigned_to_staff_id: Optional[UUID] = None
    assigned_to_vendor: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    parts_required: Optional[List[str]] = None
    estimated_cost: Optional[Decimal] = None
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None
    preventive_action: Optional[str] = None


class MaintenanceTriageRequest(BaseModel):
    """Schema for triaging a maintenance request."""
    priority: MaintenancePriority
    assigned_to_staff_id: Optional[UUID] = None
    assigned_to_vendor: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    estimated_cost: Optional[Decimal] = None
    notes: Optional[str] = None


class MaintenanceCompletionRequest(BaseModel):
    """Schema for completing a maintenance request."""
    resolution_notes: str
    root_cause: Optional[str] = None
    preventive_action: Optional[str] = None
    actual_cost: Optional[Decimal] = None
    parts_used: Optional[List[str]] = None
    requires_followup: bool = False
    followup_date: Optional[datetime] = None


class MaintenanceRequestResponse(BaseModel):
    """Schema for maintenance request response."""
    id: UUID
    request_reference: str
    category: MaintenanceCategory
    status: MaintenanceStatus
    priority: MaintenancePriority
    venue_id: Optional[UUID]
    venue_type: Optional[str]
    location_name: Optional[str]
    floor_number: Optional[int]
    specific_location: Optional[str]
    title: str
    description: str
    reported_issue: Optional[str]
    affects_room_availability: bool
    guest_impact_level: Optional[str]
    safety_concern: bool
    reported_by_staff_id: Optional[UUID]
    reported_by_guest_id: Optional[UUID]
    source_event_type: Optional[str]
    assigned_to_staff_id: Optional[UUID]
    assigned_to_vendor: Optional[str]
    reported_at: datetime
    triaged_at: Optional[datetime]
    scheduled_for: Optional[datetime]
    sla_due_date: Optional[datetime]
    work_started_at: Optional[datetime]
    work_completed_at: Optional[datetime]
    parts_required: Optional[List[str]]
    estimated_cost: Optional[Decimal]
    actual_cost: Optional[Decimal]
    resolution_notes: Optional[str]
    root_cause: Optional[str]
    preventive_action: Optional[str]
    requires_followup: bool
    followup_date: Optional[datetime]
    is_overdue: bool
    resolution_time_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MaintenanceRequestListResponse(BaseModel):
    """Schema for paginated maintenance request list response."""
    requests: List[MaintenanceRequestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MaintenanceFilter(BaseModel):
    """Schema for filtering maintenance requests."""
    categories: Optional[List[MaintenanceCategory]] = None
    statuses: Optional[List[MaintenanceStatus]] = None
    priorities: Optional[List[MaintenancePriority]] = None
    venue_id: Optional[UUID] = None
    floor_number: Optional[int] = None
    assigned_to_staff_id: Optional[UUID] = None
    safety_concern: Optional[bool] = None
    affects_room_availability: Optional[bool] = None
    is_overdue: Optional[bool] = None
    reported_from: Optional[datetime] = None
    reported_to: Optional[datetime] = None
