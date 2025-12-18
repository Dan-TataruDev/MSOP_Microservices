"""Maintenance request model for tracking repair and maintenance operations."""
import enum
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class MaintenanceCategory(str, enum.Enum):
    """Categories of maintenance work."""
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    APPLIANCE = "appliance"
    FURNITURE = "furniture"
    STRUCTURAL = "structural"
    SAFETY = "safety"
    COSMETIC = "cosmetic"
    IT_EQUIPMENT = "it_equipment"
    OTHER = "other"


class MaintenanceStatus(str, enum.Enum):
    """Maintenance request lifecycle states."""
    REPORTED = "reported"
    TRIAGED = "triaged"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PARTS_ORDERED = "parts_ordered"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class MaintenancePriority(str, enum.Enum):
    """Maintenance priority levels based on impact."""
    LOW = "low"           # Cosmetic issues, no guest impact
    NORMAL = "normal"     # Standard repairs
    HIGH = "high"         # Affects guest comfort
    URGENT = "urgent"     # Room unusable
    EMERGENCY = "emergency"  # Safety hazard


class MaintenanceRequest(Base):
    """
    Tracks maintenance requests from initial report to completion.
    
    Maintenance requests can be:
    - Reported by staff (housekeeping finding issues)
    - Reported by guests (via guest interaction service events)
    - Generated from inspections
    - Triggered by inventory alerts (equipment issues)
    
    Each request generates one or more tasks for execution.
    """
    __tablename__ = "maintenance_requests"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_reference = Column(String(20), unique=True, nullable=False, index=True)
    
    # Classification
    category = Column(Enum(MaintenanceCategory), nullable=False, index=True)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.REPORTED, nullable=False, index=True)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.NORMAL, nullable=False, index=True)
    
    # Location (local references - no direct DB coupling)
    venue_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    venue_type = Column(String(50), nullable=True)
    location_name = Column(String(100), nullable=True)
    floor_number = Column(Integer, nullable=True)
    specific_location = Column(String(200), nullable=True)  # "Bathroom sink", "Window AC unit"
    
    # Request details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    reported_issue = Column(Text, nullable=True)
    
    # Impact assessment
    affects_room_availability = Column(Boolean, default=False)
    guest_impact_level = Column(String(20), nullable=True)  # "none", "minor", "major", "critical"
    safety_concern = Column(Boolean, default=False)
    
    # Source tracking
    reported_by_staff_id = Column(UUID(as_uuid=True), nullable=True)
    reported_by_guest_id = Column(UUID(as_uuid=True), nullable=True)
    source_event_type = Column(String(100), nullable=True)
    source_task_id = Column(UUID(as_uuid=True), nullable=True)  # If found during inspection
    
    # Assignment
    assigned_to_staff_id = Column(UUID(as_uuid=True), nullable=True)
    assigned_to_vendor = Column(String(200), nullable=True)
    
    # Scheduling
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    triaged_at = Column(DateTime, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)
    sla_due_date = Column(DateTime, nullable=True)
    
    # Execution
    work_started_at = Column(DateTime, nullable=True)
    work_completed_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Parts and costs
    parts_required = Column(ARRAY(String), nullable=True)
    parts_ordered_at = Column(DateTime, nullable=True)
    parts_received_at = Column(DateTime, nullable=True)
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    
    # Resolution
    resolution_notes = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    preventive_action = Column(Text, nullable=True)
    
    # Follow-up
    requires_followup = Column(Boolean, default=False)
    followup_date = Column(DateTime, nullable=True)
    recurring_issue = Column(Boolean, default=False)
    related_request_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tasks = relationship("Task", back_populates="maintenance_request")
    
    def __repr__(self):
        return f"<MaintenanceRequest {self.request_reference} - {self.category.value} - {self.status.value}>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if request is past its SLA due date."""
        if self.status in [MaintenanceStatus.COMPLETED, MaintenanceStatus.VERIFIED, 
                          MaintenanceStatus.CLOSED, MaintenanceStatus.CANCELLED]:
            return False
        if not self.sla_due_date:
            return False
        return datetime.utcnow() > self.sla_due_date
    
    @property
    def resolution_time_minutes(self) -> int | None:
        """Calculate total resolution time if completed."""
        if self.reported_at and self.work_completed_at:
            return int((self.work_completed_at - self.reported_at).total_seconds() / 60)
        return None
