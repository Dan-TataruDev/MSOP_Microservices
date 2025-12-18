"""Service layer for cleaning schedule operations."""
import logging
from datetime import datetime, timedelta, time
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.schedule import CleaningSchedule, ScheduleStatus, RecurrencePattern
from app.models.task import Task, TaskType, TaskStatus, TaskPriority
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.utils.task_reference import generate_schedule_reference, generate_task_reference
from app.config import settings

logger = logging.getLogger(__name__)


class ScheduleService:
    """
    Business logic for cleaning schedule management.
    
    Responsibilities:
    - Create and manage recurring schedules
    - Generate tasks from schedules
    - Handle schedule activation/deactivation
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_schedule(self, schedule_data: ScheduleCreate) -> CleaningSchedule:
        """
        Create a new cleaning schedule.
        
        Args:
            schedule_data: Schedule creation data
            
        Returns:
            Created CleaningSchedule instance
        """
        schedule = CleaningSchedule(
            schedule_reference=generate_schedule_reference(),
            name=schedule_data.name,
            description=schedule_data.description,
            status=ScheduleStatus.ACTIVE,
            venue_type=schedule_data.venue_type,
            venue_ids=schedule_data.venue_ids,
            floor_numbers=schedule_data.floor_numbers,
            cleaning_type=schedule_data.cleaning_type,
            estimated_duration_minutes=schedule_data.estimated_duration_minutes,
            priority_level=schedule_data.priority_level,
            recurrence_pattern=schedule_data.recurrence_pattern,
            days_of_week=schedule_data.days_of_week,
            day_of_month=schedule_data.day_of_month,
            preferred_time=schedule_data.preferred_time,
            trigger_on_checkout=schedule_data.trigger_on_checkout,
            trigger_on_checkin=schedule_data.trigger_on_checkin,
            trigger_time_based=schedule_data.trigger_time_based,
            must_complete_by_time=schedule_data.must_complete_by_time,
            sla_minutes=schedule_data.sla_minutes,
            special_instructions=schedule_data.special_instructions,
            effective_from=schedule_data.effective_from or datetime.utcnow(),
            effective_until=schedule_data.effective_until,
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(f"Created schedule: {schedule.schedule_reference}")
        return schedule
    
    def get_schedule(self, schedule_id: UUID) -> Optional[CleaningSchedule]:
        """Get schedule by ID."""
        return self.db.query(CleaningSchedule).filter(
            CleaningSchedule.id == schedule_id
        ).first()
    
    def get_schedule_by_reference(self, reference: str) -> Optional[CleaningSchedule]:
        """Get schedule by reference number."""
        return self.db.query(CleaningSchedule).filter(
            CleaningSchedule.schedule_reference == reference
        ).first()
    
    def update_schedule(self, schedule_id: UUID, 
                       update_data: ScheduleUpdate) -> Optional[CleaningSchedule]:
        """
        Update schedule details.
        
        Args:
            schedule_id: Schedule ID
            update_data: Fields to update
            
        Returns:
            Updated CleaningSchedule or None
        """
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(schedule, key, value)
        
        schedule.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(schedule)
        
        return schedule
    
    def activate_schedule(self, schedule_id: UUID) -> Optional[CleaningSchedule]:
        """Activate a paused schedule."""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        schedule.status = ScheduleStatus.ACTIVE
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(f"Activated schedule: {schedule.schedule_reference}")
        return schedule
    
    def pause_schedule(self, schedule_id: UUID) -> Optional[CleaningSchedule]:
        """Pause an active schedule."""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        schedule.status = ScheduleStatus.PAUSED
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(f"Paused schedule: {schedule.schedule_reference}")
        return schedule
    
    def list_schedules(
        self,
        status: Optional[ScheduleStatus] = None,
        venue_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CleaningSchedule], int]:
        """
        List schedules with filtering and pagination.
        
        Args:
            status: Filter by status
            venue_type: Filter by venue type
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (schedules list, total count)
        """
        query = self.db.query(CleaningSchedule)
        
        if status:
            query = query.filter(CleaningSchedule.status == status)
        if venue_type:
            query = query.filter(CleaningSchedule.venue_type == venue_type)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        schedules = query.order_by(CleaningSchedule.created_at.desc())\
            .offset(offset).limit(page_size).all()
        
        return schedules, total
    
    def get_active_schedules(self) -> List[CleaningSchedule]:
        """Get all currently active schedules."""
        now = datetime.utcnow()
        return self.db.query(CleaningSchedule).filter(
            CleaningSchedule.status == ScheduleStatus.ACTIVE,
            CleaningSchedule.effective_from <= now,
            (CleaningSchedule.effective_until.is_(None)) | 
            (CleaningSchedule.effective_until >= now)
        ).all()
    
    def should_generate_task_today(self, schedule: CleaningSchedule) -> bool:
        """
        Check if schedule should generate a task today.
        
        Args:
            schedule: The schedule to check
            
        Returns:
            True if task should be generated
        """
        if not schedule.trigger_time_based:
            return False
        
        now = datetime.utcnow()
        today_weekday = now.weekday()  # 0=Monday
        today_day = now.day
        
        if schedule.recurrence_pattern == RecurrencePattern.DAILY:
            return True
        
        elif schedule.recurrence_pattern == RecurrencePattern.WEEKLY:
            if schedule.days_of_week:
                return today_weekday in schedule.days_of_week
            return today_weekday == 0  # Default to Monday
        
        elif schedule.recurrence_pattern == RecurrencePattern.BIWEEKLY:
            # Check if this is a scheduled week
            week_number = now.isocalendar()[1]
            if week_number % 2 == 0 and schedule.days_of_week:
                return today_weekday in schedule.days_of_week
            return False
        
        elif schedule.recurrence_pattern == RecurrencePattern.MONTHLY:
            if schedule.day_of_month:
                return today_day == schedule.day_of_month
            return today_day == 1  # Default to first of month
        
        return False
    
    def generate_tasks_from_schedule(self, schedule: CleaningSchedule) -> List[Task]:
        """
        Generate tasks from a schedule.
        
        Args:
            schedule: The schedule to generate tasks from
            
        Returns:
            List of created tasks
        """
        if not schedule.is_active:
            return []
        
        # Map cleaning type to task type
        type_map = {
            "checkout_cleaning": TaskType.CHECKOUT_CLEANING,
            "stay_over_cleaning": TaskType.STAY_OVER_CLEANING,
            "deep_cleaning": TaskType.DEEP_CLEANING,
            "turndown_service": TaskType.TURNDOWN_SERVICE,
            "inspection": TaskType.INSPECTION,
            "public_area_cleaning": TaskType.PUBLIC_AREA_CLEANING,
        }
        task_type = type_map.get(schedule.cleaning_type, TaskType.STAY_OVER_CLEANING)
        
        # Map priority level
        priority_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT,
        }
        priority = priority_map.get(schedule.priority_level, TaskPriority.NORMAL)
        
        now = datetime.utcnow()
        tasks = []
        
        # Determine scheduled time
        if schedule.preferred_time:
            scheduled_date = now.replace(
                hour=schedule.preferred_time.hour,
                minute=schedule.preferred_time.minute,
                second=0,
                microsecond=0
            )
        else:
            scheduled_date = now
        
        # Calculate due date
        if schedule.must_complete_by_time:
            due_date = now.replace(
                hour=schedule.must_complete_by_time.hour,
                minute=schedule.must_complete_by_time.minute,
                second=0,
                microsecond=0
            )
        elif schedule.sla_minutes:
            due_date = scheduled_date + timedelta(minutes=schedule.sla_minutes)
        else:
            due_date = scheduled_date + timedelta(hours=4)  # Default 4 hour SLA
        
        # Generate tasks for each venue or floor
        if schedule.venue_ids:
            for venue_id in schedule.venue_ids:
                task = self._create_scheduled_task(
                    schedule=schedule,
                    task_type=task_type,
                    priority=priority,
                    venue_id=venue_id,
                    scheduled_date=scheduled_date,
                    due_date=due_date
                )
                tasks.append(task)
        elif schedule.floor_numbers:
            for floor in schedule.floor_numbers:
                task = self._create_scheduled_task(
                    schedule=schedule,
                    task_type=task_type,
                    priority=priority,
                    floor_number=floor,
                    scheduled_date=scheduled_date,
                    due_date=due_date
                )
                tasks.append(task)
        else:
            # Create single task for schedule
            task = self._create_scheduled_task(
                schedule=schedule,
                task_type=task_type,
                priority=priority,
                scheduled_date=scheduled_date,
                due_date=due_date
            )
            tasks.append(task)
        
        # Update schedule statistics
        schedule.tasks_generated_count += len(tasks)
        schedule.last_task_generated_at = now
        
        self.db.commit()
        
        logger.info(f"Generated {len(tasks)} tasks from schedule {schedule.schedule_reference}")
        return tasks
    
    def _create_scheduled_task(
        self,
        schedule: CleaningSchedule,
        task_type: TaskType,
        priority: TaskPriority,
        scheduled_date: datetime,
        due_date: datetime,
        venue_id: Optional[UUID] = None,
        floor_number: Optional[int] = None
    ) -> Task:
        """Create a task from schedule parameters."""
        prefix_map = {
            TaskType.CHECKOUT_CLEANING: "CLN",
            TaskType.STAY_OVER_CLEANING: "CLN",
            TaskType.DEEP_CLEANING: "DPC",
            TaskType.TURNDOWN_SERVICE: "TDS",
            TaskType.INSPECTION: "INS",
            TaskType.PUBLIC_AREA_CLEANING: "PAC",
        }
        prefix = prefix_map.get(task_type, "TSK")
        
        location_desc = ""
        if floor_number is not None:
            location_desc = f"Floor {floor_number}"
        
        task = Task(
            task_reference=generate_task_reference(prefix),
            task_type=task_type,
            status=TaskStatus.PENDING,
            priority=priority,
            venue_id=venue_id,
            venue_type=schedule.venue_type,
            floor_number=floor_number,
            location_name=location_desc,
            title=f"{schedule.name} - {location_desc or 'Scheduled'}",
            description=schedule.description,
            special_instructions=schedule.special_instructions,
            scheduled_date=scheduled_date,
            due_date=due_date,
            estimated_duration_minutes=schedule.estimated_duration_minutes,
        )
        
        self.db.add(task)
        return task
    
    def run_scheduled_task_generation(self) -> int:
        """
        Run scheduled task generation for all active schedules.
        Called by background job scheduler.
        
        Returns:
            Number of tasks generated
        """
        active_schedules = self.get_active_schedules()
        total_tasks = 0
        
        for schedule in active_schedules:
            if self.should_generate_task_today(schedule):
                tasks = self.generate_tasks_from_schedule(schedule)
                total_tasks += len(tasks)
        
        logger.info(f"Scheduled task generation complete: {total_tasks} tasks created")
        return total_tasks
