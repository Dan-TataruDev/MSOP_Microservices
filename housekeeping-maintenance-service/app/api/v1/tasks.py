"""API endpoints for task management."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import TaskStatus, TaskType, TaskPriority
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskAssignment, TaskCompletion, TaskFilter
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new task.
    
    Tasks can be created manually or are typically generated automatically
    from booking events (checkout -> cleaning) or inventory events (low stock -> restocking).
    """
    service = TaskService(db)
    task = service.create_task(task_data)
    return task


@router.get("", response_model=TaskListResponse)
def list_tasks(
    task_types: Optional[List[TaskType]] = Query(None),
    statuses: Optional[List[TaskStatus]] = Query(None),
    priorities: Optional[List[TaskPriority]] = Query(None),
    venue_id: Optional[UUID] = Query(None),
    floor_number: Optional[int] = Query(None),
    assigned_staff_id: Optional[UUID] = Query(None),
    is_vip: Optional[bool] = Query(None),
    scheduled_date_from: Optional[datetime] = Query(None),
    scheduled_date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List tasks with filtering and pagination.
    
    Supports filtering by:
    - Task type (cleaning, maintenance, restocking, etc.)
    - Status (pending, in_progress, completed, etc.)
    - Priority level
    - Location (venue, floor)
    - Staff assignment
    - VIP status
    - Date range
    """
    filters = TaskFilter(
        task_types=task_types,
        statuses=statuses,
        priorities=priorities,
        venue_id=venue_id,
        floor_number=floor_number,
        assigned_staff_id=assigned_staff_id,
        is_vip=is_vip,
        scheduled_date_from=scheduled_date_from,
        scheduled_date_to=scheduled_date_to
    )
    
    service = TaskService(db)
    tasks, total = service.list_tasks(filters, page, page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/pending", response_model=List[TaskResponse])
def get_pending_tasks(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get pending tasks ordered by priority and due date."""
    service = TaskService(db)
    filters = TaskFilter(statuses=[TaskStatus.PENDING, TaskStatus.ASSIGNED])
    tasks, _ = service.list_tasks(filters, page=1, page_size=limit)
    return tasks


@router.get("/overdue", response_model=List[TaskResponse])
def get_overdue_tasks(db: Session = Depends(get_db)):
    """Get all overdue tasks that need attention."""
    service = TaskService(db)
    return service.get_overdue_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    """Get task by ID."""
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task


@router.get("/reference/{reference}", response_model=TaskResponse)
def get_task_by_reference(reference: str, db: Session = Depends(get_db)):
    """Get task by reference number."""
    service = TaskService(db)
    task = service.get_task_by_reference(reference)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {reference} not found"
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    update_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update task details."""
    service = TaskService(db)
    task = service.update_task(task_id, update_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task


@router.post("/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    task_id: UUID,
    assignment: TaskAssignment,
    db: Session = Depends(get_db)
):
    """
    Assign task to a staff member.
    
    Publishes task.assigned event for downstream consumers.
    """
    service = TaskService(db)
    task = service.assign_task(task_id, assignment.staff_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or staff member invalid"
        )
    return task


@router.post("/{task_id}/start", response_model=TaskResponse)
def start_task(task_id: UUID, db: Session = Depends(get_db)):
    """
    Mark task as started.
    
    Publishes task.started event. For cleaning tasks, also publishes
    room.cleaning_started to notify booking service.
    """
    service = TaskService(db)
    task = service.start_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} not found or cannot be started"
        )
    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: UUID,
    completion: TaskCompletion,
    db: Session = Depends(get_db)
):
    """
    Mark task as completed.
    
    Publishes task.completed event. For checkout cleaning tasks,
    also publishes room.ready event to notify booking service that
    the room is ready for check-in.
    """
    service = TaskService(db)
    task = service.complete_task(task_id, completion)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} not found or cannot be completed"
        )
    return task


@router.post("/{task_id}/delay", response_model=TaskResponse)
def mark_task_delayed(
    task_id: UUID,
    reason: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    Mark task as delayed.
    
    Publishes task.delayed event to notify supervisors and
    update room availability ETAs in booking service.
    """
    service = TaskService(db)
    task = service.mark_delayed(task_id, reason)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task


@router.post("/{task_id}/verify", response_model=TaskResponse)
def verify_task(
    task_id: UUID,
    verified_by: UUID = Query(...),
    quality_score: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    Verify task completion by supervisor.
    
    Optional quality score (1-5) for performance tracking.
    """
    service = TaskService(db)
    task = service.verify_task(task_id, verified_by, quality_score)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} not found or cannot be verified"
        )
    return task


@router.post("/auto-assign", response_model=List[dict])
def auto_assign_tasks(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Automatically assign pending tasks to available staff.
    
    Uses workload balancing algorithm considering:
    - Staff availability and current workload
    - Skills match
    - Floor proximity
    - VIP handling capability
    """
    service = TaskService(db)
    assignments = service.auto_assign_tasks(limit)
    return assignments


@router.post("/check-overdue")
def check_and_mark_overdue(db: Session = Depends(get_db)):
    """
    Check for overdue tasks and mark them as delayed.
    
    This endpoint is typically called by a background scheduler.
    Publishes task.delayed events for each newly delayed task.
    """
    service = TaskService(db)
    count = service.check_and_mark_overdue()
    return {"marked_as_delayed": count}
