"""API endpoints for maintenance request management."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.maintenance import MaintenanceCategory, MaintenanceStatus, MaintenancePriority
from app.schemas.maintenance import (
    MaintenanceRequestCreate, MaintenanceRequestUpdate,
    MaintenanceRequestResponse, MaintenanceRequestListResponse,
    MaintenanceTriageRequest, MaintenanceCompletionRequest,
    MaintenanceFilter
)
from app.services.maintenance_service import MaintenanceService

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.post("", response_model=MaintenanceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new maintenance request.
    
    Maintenance requests can be created:
    - Manually by staff
    - Automatically from guest complaint events
    - From inspection task findings
    - From inventory equipment alerts
    
    SLA is automatically calculated based on priority.
    Publishes maintenance.reported event.
    """
    service = MaintenanceService(db)
    request = service.create_request(request_data)
    return request


@router.get("", response_model=MaintenanceRequestListResponse)
def list_maintenance_requests(
    categories: Optional[List[MaintenanceCategory]] = Query(None),
    statuses: Optional[List[MaintenanceStatus]] = Query(None),
    priorities: Optional[List[MaintenancePriority]] = Query(None),
    venue_id: Optional[UUID] = Query(None),
    floor_number: Optional[int] = Query(None),
    assigned_to_staff_id: Optional[UUID] = Query(None),
    safety_concern: Optional[bool] = Query(None),
    affects_room_availability: Optional[bool] = Query(None),
    reported_from: Optional[datetime] = Query(None),
    reported_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List maintenance requests with filtering and pagination.
    
    Filter by:
    - Category (plumbing, electrical, HVAC, etc.)
    - Status (reported, triaged, in_progress, completed, etc.)
    - Priority (low, normal, high, urgent, emergency)
    - Location (venue, floor)
    - Assignment
    - Safety concern flag
    - Room availability impact
    - Date range
    """
    filters = MaintenanceFilter(
        categories=categories,
        statuses=statuses,
        priorities=priorities,
        venue_id=venue_id,
        floor_number=floor_number,
        assigned_to_staff_id=assigned_to_staff_id,
        safety_concern=safety_concern,
        affects_room_availability=affects_room_availability,
        reported_from=reported_from,
        reported_to=reported_to
    )
    
    service = MaintenanceService(db)
    requests, total = service.list_requests(filters, page, page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    return MaintenanceRequestListResponse(
        requests=requests,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/open", response_model=List[MaintenanceRequestResponse])
def get_open_requests(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get open maintenance requests ordered by priority."""
    filters = MaintenanceFilter(
        statuses=[
            MaintenanceStatus.REPORTED,
            MaintenanceStatus.TRIAGED,
            MaintenanceStatus.SCHEDULED,
            MaintenanceStatus.IN_PROGRESS,
            MaintenanceStatus.PARTS_ORDERED,
            MaintenanceStatus.ON_HOLD
        ]
    )
    
    service = MaintenanceService(db)
    requests, _ = service.list_requests(filters, page=1, page_size=limit)
    return requests


@router.get("/overdue", response_model=List[MaintenanceRequestResponse])
def get_overdue_requests(db: Session = Depends(get_db)):
    """Get all overdue maintenance requests."""
    service = MaintenanceService(db)
    return service.get_overdue_requests()


@router.get("/critical", response_model=List[MaintenanceRequestResponse])
def get_critical_requests(db: Session = Depends(get_db)):
    """Get critical/emergency maintenance requests."""
    filters = MaintenanceFilter(
        priorities=[MaintenancePriority.URGENT, MaintenancePriority.EMERGENCY],
        statuses=[
            MaintenanceStatus.REPORTED,
            MaintenanceStatus.TRIAGED,
            MaintenanceStatus.SCHEDULED,
            MaintenanceStatus.IN_PROGRESS
        ]
    )
    
    service = MaintenanceService(db)
    requests, _ = service.list_requests(filters, page=1, page_size=100)
    return requests


@router.get("/{request_id}", response_model=MaintenanceRequestResponse)
def get_maintenance_request(request_id: UUID, db: Session = Depends(get_db)):
    """Get maintenance request by ID."""
    service = MaintenanceService(db)
    request = service.get_request(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance request {request_id} not found"
        )
    return request


@router.get("/reference/{reference}", response_model=MaintenanceRequestResponse)
def get_request_by_reference(reference: str, db: Session = Depends(get_db)):
    """Get maintenance request by reference number."""
    service = MaintenanceService(db)
    request = service.get_request_by_reference(reference)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance request {reference} not found"
        )
    return request


@router.patch("/{request_id}", response_model=MaintenanceRequestResponse)
def update_maintenance_request(
    request_id: UUID,
    update_data: MaintenanceRequestUpdate,
    db: Session = Depends(get_db)
):
    """Update maintenance request details."""
    service = MaintenanceService(db)
    request = service.update_request(request_id, update_data)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance request {request_id} not found"
        )
    return request


@router.post("/{request_id}/triage", response_model=MaintenanceRequestResponse)
def triage_maintenance_request(
    request_id: UUID,
    triage_data: MaintenanceTriageRequest,
    db: Session = Depends(get_db)
):
    """
    Triage a reported maintenance request.
    
    Sets priority, assignment, and schedule. Automatically creates
    a maintenance task if assigned.
    """
    service = MaintenanceService(db)
    request = service.triage_request(request_id, triage_data)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request {request_id} not found or cannot be triaged"
        )
    return request


@router.post("/{request_id}/start", response_model=MaintenanceRequestResponse)
def start_maintenance_work(request_id: UUID, db: Session = Depends(get_db)):
    """Mark maintenance work as started."""
    service = MaintenanceService(db)
    request = service.start_work(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request {request_id} not found or cannot be started"
        )
    return request


@router.post("/{request_id}/complete", response_model=MaintenanceRequestResponse)
def complete_maintenance_request(
    request_id: UUID,
    completion_data: MaintenanceCompletionRequest,
    db: Session = Depends(get_db)
):
    """
    Mark maintenance request as completed.
    
    Publishes maintenance.resolved event to notify booking service
    that the room is available again (if it affected availability).
    """
    service = MaintenanceService(db)
    request = service.complete_request(request_id, completion_data)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request {request_id} not found or cannot be completed"
        )
    return request


@router.post("/{request_id}/escalate", response_model=MaintenanceRequestResponse)
def escalate_maintenance_request(
    request_id: UUID,
    reason: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    Escalate maintenance request to higher priority.
    
    Publishes maintenance.escalated event to notify supervisors.
    """
    service = MaintenanceService(db)
    request = service.escalate_request(request_id, reason)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {request_id} not found"
        )
    return request
