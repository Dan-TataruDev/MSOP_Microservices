"""Room availability service."""
import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.room import Room, RoomStatus, RoomType
from app.schemas.room import RoomCreate, RoomUpdate, RoomAvailabilityResponse
from app.events.publisher import event_publisher

logger = logging.getLogger(__name__)


class RoomService:
    """Manages room availability and status transitions."""
    
    def create_room(self, db: Session, room_data: RoomCreate) -> Room:
        """Create a new room."""
        room = Room(**room_data.model_dump())
        db.add(room)
        db.commit()
        db.refresh(room)
        return room
    
    def get_room(self, db: Session, room_id: UUID) -> Optional[Room]:
        """Get room by ID."""
        return db.query(Room).filter(Room.id == room_id).first()
    
    def update_status(self, db: Session, room_id: UUID, new_status: RoomStatus) -> Optional[Room]:
        """Update room status and emit event."""
        room = self.get_room(db, room_id)
        if not room:
            return None
        
        old_status = room.status
        room.status = new_status
        room.status_updated_at = datetime.utcnow()
        db.commit()
        
        event_publisher.publish_room_status_changed(room_id, old_status.value, new_status.value)
        logger.info(f"Room {room.room_number} status: {old_status.value} -> {new_status.value}")
        return room
    
    def assign_booking(self, db: Session, room_id: UUID, booking_id: UUID) -> Optional[Room]:
        """Assign a booking to a room."""
        room = self.get_room(db, room_id)
        if not room:
            return None
        
        room.current_booking_id = booking_id
        room.status = RoomStatus.RESERVED
        room.status_updated_at = datetime.utcnow()
        db.commit()
        
        event_publisher.publish_room_status_changed(room_id, "available", RoomStatus.RESERVED.value)
        return room
    
    def release_booking(self, db: Session, room_id: UUID) -> Optional[Room]:
        """Release room from booking."""
        room = self.get_room(db, room_id)
        if not room:
            return None
        
        old_status = room.status
        room.current_booking_id = None
        room.status = RoomStatus.CLEANING
        room.status_updated_at = datetime.utcnow()
        db.commit()
        
        event_publisher.publish_room_status_changed(room_id, old_status.value, RoomStatus.CLEANING.value)
        return room
    
    def get_availability(
        self, db: Session, venue_id: UUID, room_type: Optional[RoomType] = None, min_capacity: Optional[int] = None
    ) -> RoomAvailabilityResponse:
        """Get room availability summary for a venue."""
        query = db.query(Room).filter(Room.venue_id == venue_id, Room.is_active == True)
        
        if room_type:
            query = query.filter(Room.room_type == room_type)
        if min_capacity:
            query = query.filter(Room.capacity >= min_capacity)
        
        rooms = query.all()
        
        return RoomAvailabilityResponse(
            total_rooms=len(rooms),
            available=sum(1 for r in rooms if r.status == RoomStatus.AVAILABLE),
            occupied=sum(1 for r in rooms if r.status == RoomStatus.OCCUPIED),
            reserved=sum(1 for r in rooms if r.status == RoomStatus.RESERVED),
            maintenance=sum(1 for r in rooms if r.status in [RoomStatus.MAINTENANCE, RoomStatus.OUT_OF_SERVICE]),
            rooms=rooms,
        )
    
    def list_available_rooms(
        self, db: Session, venue_id: UUID, room_type: Optional[RoomType] = None, min_capacity: Optional[int] = None
    ) -> List[Room]:
        """List available rooms for booking."""
        query = db.query(Room).filter(
            Room.venue_id == venue_id,
            Room.is_active == True,
            Room.status == RoomStatus.AVAILABLE,
        )
        if room_type:
            query = query.filter(Room.room_type == room_type)
        if min_capacity:
            query = query.filter(Room.capacity >= min_capacity)
        return query.all()


room_service = RoomService()


