"""Task model for housekeeping and maintenance tasks."""
import enum
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class TaskType(str, enum.Enum):
    """Types of operational tasks."""
    CHECKOUT_CLEANING = "checkout_cleaning"
    STAY_OVER_CLEANING = "stay_over_cleaning"
    DEEP_CLEANING = "deep_cleaning"
    TURNDOWN_SERVICE = "turndown_service"
    INSPECTION = "inspection"
    MAINTENANCE_REPAIR = "maintenance_repair"
    PREVENTIVE_MAINTENANCE = "preventive_maintenance"
    RESTOCKING = "restocking"
    LAUNDRY = "laundry"
    PUBLIC_AREA_CLEANING = "public_area_cleaning"


class TaskStatus(str, enum.Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Task(Base):
    """
    Core task model for all housekeeping and maintenance operations.
    
    Tasks are generated from:
    - Booking events (checkout -> cleaning task)
    - Inventory events (low stock -> restocking task)
    - Maintenance requests
    - Scheduled operations
    
    This model stores only local references to external entities (venue_id, booking_reference)
    to maintain loose coupling with other services.
    """
    __tablename__ = "tasks"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_reference = Column(String(20), unique=True, nullable=False, index=True)
    
    # Task classification
    task_type = Column(Enum(TaskType), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL, nullable=False, index=True)
    
    # Location reference (stored locally - no direct DB coupling)
    venue_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    venue_type = Column(String(50), nullable=True)  # "room", "table", "public_area"
    location_name = Column(String(100), nullable=True)  # Cached for display
    floor_number = Column(Integer, nullable=True)
    
    # Source tracking (event-driven creation)
    source_event_type = Column(String(100), nullable=True)
    source_booking_reference = Column(String(50), nullable=True, index=True)
    source_maintenance_id = Column(UUID(as_uuid=True), ForeignKey("maintenance_requests.id"), nullable=True)
    
    # Task details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    is_vip = Column(Boolean, default=False)
    
    # Assignment
    assigned_staff_id = Column(UUID(as_uuid=True), ForeignKey("staff_members.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    due_date = Column(DateTime, nullable=False, index=True)
    estimated_duration_minutes = Column(Integer, default=30)
    
    # Execution tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Delay tracking
    is_delayed = Column(Boolean, default=False)
    delay_reason = Column(Text, nullable=True)
    delay_notified_at = Column(DateTime, nullable=True)
    
    # Completion details
    completion_notes = Column(Text, nullable=True)
    issues_found = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assigned_staff = relationship("StaffMember", back_populates="tasks")
    maintenance_request = relationship("MaintenanceRequest", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task {self.task_reference} - {self.task_type.value} - {self.status.value}>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is past its due date."""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.CANCELLED]:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def actual_duration_minutes(self) -> int | None:
        """Calculate actual task duration if completed."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() / 60)
        return None
