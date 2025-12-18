"""Room availability database model."""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    CLEANING = "cleaning"
    OUT_OF_SERVICE = "out_of_service"


class RoomType(str, enum.Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    PENTHOUSE = "penthouse"
    ACCESSIBLE = "accessible"


class Room(Base):
    """Room entity with availability status."""
    __tablename__ = "rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_number = Column(String(20), nullable=False, index=True)
    venue_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    room_type = Column(Enum(RoomType), nullable=False, index=True)
    status = Column(Enum(RoomStatus), nullable=False, default=RoomStatus.AVAILABLE, index=True)
    
    floor = Column(Integer, nullable=False, default=1)
    capacity = Column(Integer, nullable=False, default=2)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Current assignment
    current_booking_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    status_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_room_venue_status", "venue_id", "status"),
        Index("idx_room_venue_number", "venue_id", "room_number", unique=True),
    )


