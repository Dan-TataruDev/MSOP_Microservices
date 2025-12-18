"""Cleaning schedule model for recurring and planned cleaning operations."""
import enum
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, Boolean, Time
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.database import Base


class ScheduleStatus(str, enum.Enum):
    """Schedule lifecycle states."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecurrencePattern(str, enum.Enum):
    """Recurrence patterns for scheduled tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class CleaningSchedule(Base):
    """
    Represents recurring cleaning schedules for rooms, public areas, etc.
    
    Schedules generate tasks automatically based on:
    - Time-based triggers (daily room cleaning)
    - Event-based triggers (checkout cleaning)
    - Custom patterns
    """
    __tablename__ = "cleaning_schedules"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    schedule_reference = Column(String(20), unique=True, nullable=False, index=True)
    
    # Schedule metadata
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.ACTIVE, nullable=False, index=True)
    
    # Target configuration (local references only)
    venue_type = Column(String(50), nullable=False)  # "room", "public_area", "restaurant"
    venue_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # Specific venues or null for all
    floor_numbers = Column(ARRAY(Integer), nullable=True)  # Filter by floors
    
    # Cleaning type
    cleaning_type = Column(String(50), nullable=False)  # maps to TaskType
    estimated_duration_minutes = Column(Integer, default=30)
    priority_level = Column(String(20), default="normal")
    
    # Recurrence configuration
    recurrence_pattern = Column(Enum(RecurrencePattern), nullable=False)
    days_of_week = Column(ARRAY(Integer), nullable=True)  # 0=Monday, 6=Sunday
    day_of_month = Column(Integer, nullable=True)
    preferred_time = Column(Time, nullable=True)
    
    # Trigger configuration
    trigger_on_checkout = Column(Boolean, default=False)
    trigger_on_checkin = Column(Boolean, default=False)
    trigger_time_based = Column(Boolean, default=True)
    
    # SLA configuration
    must_complete_by_time = Column(Time, nullable=True)
    sla_minutes = Column(Integer, nullable=True)
    
    # Special instructions
    special_instructions = Column(Text, nullable=True)
    checklist_template_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Validity period
    effective_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_until = Column(DateTime, nullable=True)
    
    # Statistics
    tasks_generated_count = Column(Integer, default=0)
    last_task_generated_at = Column(DateTime, nullable=True)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CleaningSchedule {self.schedule_reference} - {self.name}>"
    
    @property
    def is_active(self) -> bool:
        """Check if schedule is currently active."""
        if self.status != ScheduleStatus.ACTIVE:
            return False
        now = datetime.utcnow()
        if self.effective_until and now > self.effective_until:
            return False
        return now >= self.effective_from
