"""Table capacity database model."""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class TableStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"
    OUT_OF_SERVICE = "out_of_service"


class Table(Base):
    """Restaurant/venue table with capacity tracking."""
    __tablename__ = "tables"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_number = Column(String(20), nullable=False)
    venue_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    status = Column(Enum(TableStatus), nullable=False, default=TableStatus.AVAILABLE, index=True)
    capacity = Column(Integer, nullable=False, default=4)
    min_capacity = Column(Integer, nullable=False, default=1)
    
    section = Column(String(50), nullable=True)  # e.g., "patio", "main", "private"
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Current assignment
    current_booking_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    status_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_table_venue_status", "venue_id", "status"),
        Index("idx_table_venue_number", "venue_id", "table_number", unique=True),
    )


