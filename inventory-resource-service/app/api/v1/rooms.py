"""Room availability API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.services.room_service import room_service
from app.models.room import RoomStatus, RoomType
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomAvailabilityResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomResponse, status_code=201)
def create_room(room_data: RoomCreate, db: Session = Depends(get_db)):
    """Create a new room."""
    return room_service.create_room(db, room_data)


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: UUID, db: Session = Depends(get_db)):
    """Get room by ID."""
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.patch("/{room_id}/status")
def update_room_status(room_id: UUID, status: RoomStatus, db: Session = Depends(get_db)):
    """Update room status."""
    room = room_service.update_status(db, room_id, status)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": f"Room status updated to {status.value}"}


@router.get("/venue/{venue_id}/availability", response_model=RoomAvailabilityResponse)
def get_room_availability(
    venue_id: UUID,
    room_type: Optional[RoomType] = None,
    min_capacity: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get room availability summary for a venue."""
    return room_service.get_availability(db, venue_id, room_type, min_capacity)


@router.get("/venue/{venue_id}/available", response_model=List[RoomResponse])
def list_available_rooms(
    venue_id: UUID,
    room_type: Optional[RoomType] = None,
    min_capacity: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List available rooms for booking."""
    return room_service.list_available_rooms(db, venue_id, room_type, min_capacity)


