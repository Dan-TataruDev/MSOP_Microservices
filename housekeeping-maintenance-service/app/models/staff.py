"""Staff member model for housekeeping and maintenance personnel."""
import enum
from datetime import datetime, time
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer, Enum, Boolean, Time
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class StaffRole(str, enum.Enum):
    """Staff roles in housekeeping and maintenance."""
    HOUSEKEEPER = "housekeeper"
    SENIOR_HOUSEKEEPER = "senior_housekeeper"
    HOUSEKEEPING_SUPERVISOR = "housekeeping_supervisor"
    MAINTENANCE_TECHNICIAN = "maintenance_technician"
    SENIOR_TECHNICIAN = "senior_technician"
    MAINTENANCE_SUPERVISOR = "maintenance_supervisor"
    INSPECTOR = "inspector"
    MANAGER = "manager"


class StaffShift(str, enum.Enum):
    """Standard work shifts."""
    MORNING = "morning"      # 6:00 - 14:00
    AFTERNOON = "afternoon"  # 14:00 - 22:00
    NIGHT = "night"          # 22:00 - 6:00
    FLEXIBLE = "flexible"


class StaffMember(Base):
    """
    Represents housekeeping and maintenance staff members.
    
    This is a local representation - actual employee data may live
    in an HR system. This service maintains operational data like
    skills, availability, and workload.
    """
    __tablename__ = "staff_members"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic info (cached from HR system)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Role and department
    role = Column(Enum(StaffRole), nullable=False, index=True)
    department = Column(String(50), nullable=False)  # "housekeeping", "maintenance"
    
    # Work configuration
    shift = Column(Enum(StaffShift), default=StaffShift.MORNING, nullable=False)
    shift_start = Column(Time, nullable=True)
    shift_end = Column(Time, nullable=True)
    working_days = Column(ARRAY(Integer), default=[0, 1, 2, 3, 4])  # Mon-Fri
    
    # Skills and certifications
    skills = Column(ARRAY(String), nullable=True)  # ["plumbing", "electrical", "hvac"]
    certifications = Column(ARRAY(String), nullable=True)
    can_handle_vip = Column(Boolean, default=False)
    
    # Assignment preferences
    preferred_floors = Column(ARRAY(Integer), nullable=True)
    max_tasks_per_shift = Column(Integer, default=15)
    
    # Current status
    is_active = Column(Boolean, default=True, index=True)
    is_on_duty = Column(Boolean, default=False, index=True)
    current_location = Column(String(100), nullable=True)
    
    # Performance tracking
    tasks_completed_total = Column(Integer, default=0)
    average_task_duration_minutes = Column(Integer, nullable=True)
    quality_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Availability
    available_from = Column(DateTime, nullable=True)
    unavailable_until = Column(DateTime, nullable=True)
    unavailability_reason = Column(String(200), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_task_assigned_at = Column(DateTime, nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="assigned_staff")
    
    def __repr__(self):
        return f"<StaffMember {self.employee_id} - {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self) -> str:
        """Get staff member's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_available(self) -> bool:
        """Check if staff member is currently available for tasks."""
        if not self.is_active or not self.is_on_duty:
            return False
        now = datetime.utcnow()
        if self.unavailable_until and now < self.unavailable_until:
            return False
        return True
    
    def can_handle_category(self, category: str) -> bool:
        """Check if staff member has skills for a category."""
        if not self.skills:
            return False
        return category.lower() in [s.lower() for s in self.skills]
