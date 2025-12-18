"""Service layer for task operations."""
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.task import Task, TaskType, TaskStatus, TaskPriority
from app.models.staff import StaffMember
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter, TaskCompletion
from app.events.publisher import event_publisher
from app.utils.task_reference import generate_task_reference
from app.utils.priority_calculator import calculate_due_date
from app.utils.workload_balancer import WorkloadBalancer
from app.config import settings

logger = logging.getLogger(__name__)


class TaskService:
    """
    Business logic for task management.
    
    Responsibilities:
    - Create, update, and manage tasks
    - Handle task state transitions
    - Track delays and SLA compliance
    - Coordinate with event publisher
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.workload_balancer = WorkloadBalancer(db)
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """
        Create a new task.
        
        Args:
            task_data: Task creation data
            
        Returns:
            Created Task instance
        """
        # Generate reference based on task type
        prefix_map = {
            TaskType.CHECKOUT_CLEANING: "CLN",
            TaskType.STAY_OVER_CLEANING: "CLN",
            TaskType.DEEP_CLEANING: "DPC",
            TaskType.TURNDOWN_SERVICE: "TDS",
            TaskType.INSPECTION: "INS",
            TaskType.MAINTENANCE_REPAIR: "MNT",
            TaskType.PREVENTIVE_MAINTENANCE: "PMT",
            TaskType.RESTOCKING: "RST",
            TaskType.LAUNDRY: "LND",
            TaskType.PUBLIC_AREA_CLEANING: "PAC",
        }
        prefix = prefix_map.get(task_data.task_type, "TSK")
        
        task = Task(
            task_reference=generate_task_reference(prefix),
            task_type=task_data.task_type,
            status=TaskStatus.PENDING,
            priority=task_data.priority,
            venue_id=task_data.venue_id,
            venue_type=task_data.venue_type,
            location_name=task_data.location_name,
            floor_number=task_data.floor_number,
            source_event_type=task_data.source_event_type,
            source_booking_reference=task_data.source_booking_reference,
            source_maintenance_id=task_data.source_maintenance_id,
            title=task_data.title,
            description=task_data.description,
            special_instructions=task_data.special_instructions,
            is_vip=task_data.is_vip,
            scheduled_date=task_data.scheduled_date,
            due_date=task_data.due_date,
            estimated_duration_minutes=task_data.estimated_duration_minutes,
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        # Publish event
        event_publisher.publish_task_created({
            "id": task.id,
            "task_reference": task.task_reference,
            "task_type": task.task_type.value,
            "priority": task.priority.value,
            "venue_id": task.venue_id,
            "venue_type": task.venue_type,
            "scheduled_date": task.scheduled_date,
            "due_date": task.due_date,
            "source_event_type": task.source_event_type,
            "is_vip": task.is_vip,
        })
        
        logger.info(f"Created task: {task.task_reference}")
        return task
    
    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID."""
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def get_task_by_reference(self, reference: str) -> Optional[Task]:
        """Get task by reference number."""
        return self.db.query(Task).filter(Task.task_reference == reference).first()
    
    def update_task(self, task_id: UUID, update_data: TaskUpdate) -> Optional[Task]:
        """
        Update task details.
        
        Args:
            task_id: Task ID
            update_data: Fields to update
            
        Returns:
            Updated Task or None
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(task, key, value)
        
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def assign_task(self, task_id: UUID, staff_id: UUID) -> Optional[Task]:
        """
        Assign task to staff member.
        
        Args:
            task_id: Task ID
            staff_id: Staff member ID
            
        Returns:
            Updated Task or None
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        staff = self.db.query(StaffMember).filter(StaffMember.id == staff_id).first()
        if not staff:
            return None
        
        task.assigned_staff_id = staff_id
        task.assigned_at = datetime.utcnow()
        task.status = TaskStatus.ASSIGNED
        
        self.db.commit()
        self.db.refresh(task)
        
        # Publish event
        event_publisher.publish_task_assigned(
            task_id=task.id,
            task_reference=task.task_reference,
            staff_id=staff_id,
            staff_name=staff.full_name
        )
        
        logger.info(f"Assigned task {task.task_reference} to {staff.full_name}")
        return task
    
    def start_task(self, task_id: UUID) -> Optional[Task]:
        """
        Mark task as started.
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated Task or None
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        if task.status not in [TaskStatus.PENDING, TaskStatus.ASSIGNED]:
            logger.warning(f"Cannot start task {task.task_reference} in status {task.status}")
            return None
        
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        # Publish events
        event_publisher.publish_task_started(
            task_id=task.id,
            task_reference=task.task_reference,
            venue_id=task.venue_id
        )
        
        # If it's a cleaning task, notify room status
        if task.task_type in [TaskType.CHECKOUT_CLEANING, TaskType.STAY_OVER_CLEANING, 
                             TaskType.DEEP_CLEANING] and task.venue_id:
            event_publisher.publish_room_cleaning_started(
                venue_id=task.venue_id,
                room_number=task.location_name or "Unknown",
                estimated_completion_minutes=task.estimated_duration_minutes
            )
        
        logger.info(f"Started task: {task.task_reference}")
        return task
    
    def complete_task(self, task_id: UUID, completion_data: TaskCompletion) -> Optional[Task]:
        """
        Mark task as completed.
        
        Args:
            task_id: Task ID
            completion_data: Completion details
            
        Returns:
            Updated Task or None
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        if task.status != TaskStatus.IN_PROGRESS:
            logger.warning(f"Cannot complete task {task.task_reference} not in progress")
            return None
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.completion_notes = completion_data.completion_notes
        task.issues_found = completion_data.issues_found
        
        self.db.commit()
        self.db.refresh(task)
        
        # Calculate duration
        duration = task.actual_duration_minutes or task.estimated_duration_minutes
        
        # Publish completion event
        event_publisher.publish_task_completed(
            task_id=task.id,
            task_reference=task.task_reference,
            task_type=task.task_type.value,
            venue_id=task.venue_id,
            duration_minutes=duration,
            issues_found=task.issues_found
        )
        
        # If checkout cleaning, publish room ready
        if task.task_type == TaskType.CHECKOUT_CLEANING and task.venue_id:
            event_publisher.publish_room_ready(
                venue_id=task.venue_id,
                room_number=task.location_name or "Unknown",
                booking_reference=task.source_booking_reference
            )
        
        logger.info(f"Completed task: {task.task_reference}")
        return task
    
    def mark_delayed(self, task_id: UUID, reason: str) -> Optional[Task]:
        """
        Mark task as delayed.
        
        Args:
            task_id: Task ID
            reason: Delay reason
            
        Returns:
            Updated Task or None
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        task.is_delayed = True
        task.delay_reason = reason
        task.delay_notified_at = datetime.utcnow()
        task.status = TaskStatus.DELAYED
        
        self.db.commit()
        self.db.refresh(task)
        
        # Calculate new estimated completion
        new_estimated = datetime.utcnow() + \
            __import__('datetime').timedelta(minutes=task.estimated_duration_minutes)
        
        # Publish delay event
        event_publisher.publish_task_delayed(
            task_id=task.id,
            task_reference=task.task_reference,
            task_type=task.task_type.value,
            venue_id=task.venue_id,
            delay_reason=reason,
            new_estimated_completion=new_estimated
        )
        
        logger.warning(f"Task delayed: {task.task_reference} - {reason}")
        return task
    
    def verify_task(self, task_id: UUID, verified_by: UUID, 
                   quality_score: Optional[int] = None) -> Optional[Task]:
        """
        Verify task completion by supervisor.
        
        Args:
            task_id: Task ID
            verified_by: Verifier's staff ID
            quality_score: Optional quality score (1-5)
            
        Returns:
            Updated Task or None
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        if task.status != TaskStatus.COMPLETED:
            logger.warning(f"Cannot verify task {task.task_reference} not completed")
            return None
        
        task.status = TaskStatus.VERIFIED
        task.verified_at = datetime.utcnow()
        task.verified_by = verified_by
        
        self.db.commit()
        self.db.refresh(task)
        
        # Publish verification event
        event_publisher.publish_task_verified(
            task_id=task.id,
            task_reference=task.task_reference,
            verified_by=verified_by,
            quality_score=quality_score
        )
        
        logger.info(f"Verified task: {task.task_reference}")
        return task
    
    def list_tasks(
        self,
        filters: Optional[TaskFilter] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Task], int]:
        """
        List tasks with filtering and pagination.
        
        Args:
            filters: Filter criteria
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (tasks list, total count)
        """
        query = self.db.query(Task)
        
        if filters:
            if filters.task_types:
                query = query.filter(Task.task_type.in_(filters.task_types))
            if filters.statuses:
                query = query.filter(Task.status.in_(filters.statuses))
            if filters.priorities:
                query = query.filter(Task.priority.in_(filters.priorities))
            if filters.venue_id:
                query = query.filter(Task.venue_id == filters.venue_id)
            if filters.floor_number is not None:
                query = query.filter(Task.floor_number == filters.floor_number)
            if filters.assigned_staff_id:
                query = query.filter(Task.assigned_staff_id == filters.assigned_staff_id)
            if filters.is_vip is not None:
                query = query.filter(Task.is_vip == filters.is_vip)
            if filters.scheduled_date_from:
                query = query.filter(Task.scheduled_date >= filters.scheduled_date_from)
            if filters.scheduled_date_to:
                query = query.filter(Task.scheduled_date <= filters.scheduled_date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        tasks = query.order_by(Task.priority.desc(), Task.due_date.asc())\
            .offset(offset).limit(page_size).all()
        
        return tasks, total
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        now = datetime.utcnow()
        return self.db.query(Task).filter(
            Task.due_date < now,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED, 
                           TaskStatus.IN_PROGRESS, TaskStatus.ON_HOLD])
        ).all()
    
    def check_and_mark_overdue(self) -> int:
        """
        Check for overdue tasks and mark them as delayed.
        
        Returns:
            Number of tasks marked as delayed
        """
        overdue_tasks = self.get_overdue_tasks()
        count = 0
        
        for task in overdue_tasks:
            if not task.is_delayed:
                self.mark_delayed(task.id, "Task exceeded due date")
                count += 1
        
        return count
    
    def auto_assign_tasks(self, limit: int = 10) -> List[dict]:
        """
        Auto-assign pending tasks to available staff.
        
        Args:
            limit: Maximum tasks to assign
            
        Returns:
            List of assignment results
        """
        return self.workload_balancer.auto_assign_pending_tasks(limit)
