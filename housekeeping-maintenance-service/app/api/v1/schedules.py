"""API endpoints for cleaning schedule management."""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schedule import ScheduleStatus
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleListResponse
)
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new cleaning schedule.
    
    Schedules define recurring cleaning patterns that automatically
    generate tasks based on time or event triggers.
    
    Trigger types:
    - Time-based: Daily, weekly, biweekly, monthly patterns
    - Event-based: On checkout, on checkin
    """
    service = ScheduleService(db)
    schedule = service.create_schedule(schedule_data)
    return schedule


@router.get("", response_model=ScheduleListResponse)
def list_schedules(
    status: Optional[ScheduleStatus] = Query(None),
    venue_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List cleaning schedules with filtering and pagination.
    
    Filter by:
    - Status (active, paused, completed, cancelled)
    - Venue type (room, public_area, restaurant, etc.)
    """
    service = ScheduleService(db)
    schedules, total = service.list_schedules(status, venue_type, page, page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    return ScheduleListResponse(
        schedules=schedules,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/active", response_model=List[ScheduleResponse])
def get_active_schedules(db: Session = Depends(get_db)):
    """Get all currently active schedules."""
    service = ScheduleService(db)
    return service.get_active_schedules()


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    """Get schedule by ID."""
    service = ScheduleService(db)
    schedule = service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    return schedule


@router.get("/reference/{reference}", response_model=ScheduleResponse)
def get_schedule_by_reference(reference: str, db: Session = Depends(get_db)):
    """Get schedule by reference number."""
    service = ScheduleService(db)
    schedule = service.get_schedule_by_reference(reference)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {reference} not found"
        )
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: UUID,
    update_data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update schedule configuration."""
    service = ScheduleService(db)
    schedule = service.update_schedule(schedule_id, update_data)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    return schedule


@router.post("/{schedule_id}/activate", response_model=ScheduleResponse)
def activate_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    """Activate a paused schedule."""
    service = ScheduleService(db)
    schedule = service.activate_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    return schedule


@router.post("/{schedule_id}/pause", response_model=ScheduleResponse)
def pause_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    """Pause an active schedule."""
    service = ScheduleService(db)
    schedule = service.pause_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    return schedule


@router.post("/{schedule_id}/generate-tasks")
def generate_tasks_from_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    """
    Manually trigger task generation from a schedule.
    
    Useful for testing or handling missed scheduled runs.
    """
    service = ScheduleService(db)
    schedule = service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    
    tasks = service.generate_tasks_from_schedule(schedule)
    return {
        "schedule_reference": schedule.schedule_reference,
        "tasks_generated": len(tasks),
        "task_references": [t.task_reference for t in tasks]
    }


@router.post("/run-scheduled-generation")
def run_scheduled_task_generation(db: Session = Depends(get_db)):
    """
    Run scheduled task generation for all active schedules.
    
    This endpoint is typically called by a background scheduler (cron job).
    It checks all active schedules and generates tasks for those
    that should run today.
    """
    service = ScheduleService(db)
    count = service.run_scheduled_task_generation()
    return {"tasks_generated": count}
