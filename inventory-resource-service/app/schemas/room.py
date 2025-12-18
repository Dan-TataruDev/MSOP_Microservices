"""Room schemas."""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.room import RoomStatus, RoomType


class RoomBase(BaseModel):
    room_number: str
    venue_id: UUID
    room_type: RoomType
    floor: int = 1
    capacity: int = 2


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    status: Optional[RoomStatus] = None
    room_type: Optional[RoomType] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None
    current_booking_id: Optional[UUID] = None


class RoomResponse(RoomBase):
    id: UUID
    status: RoomStatus
    is_active: bool
    current_booking_id: Optional[UUID]
    status_updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class RoomAvailabilityQuery(BaseModel):
    venue_id: UUID
    room_type: Optional[RoomType] = None
    min_capacity: Optional[int] = None


class RoomAvailabilityResponse(BaseModel):
    total_rooms: int
    available: int
    occupied: int
    reserved: int
    maintenance: int
    rooms: List[RoomResponse]


