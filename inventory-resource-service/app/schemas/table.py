"""Table schemas."""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.table import TableStatus


class TableBase(BaseModel):
    table_number: str
    venue_id: UUID
    capacity: int = 4
    min_capacity: int = 1
    section: Optional[str] = None


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    status: Optional[TableStatus] = None
    capacity: Optional[int] = None
    min_capacity: Optional[int] = None
    section: Optional[str] = None
    is_active: Optional[bool] = None
    current_booking_id: Optional[UUID] = None


class TableResponse(TableBase):
    id: UUID
    status: TableStatus
    is_active: bool
    current_booking_id: Optional[UUID]
    status_updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TableAvailabilityQuery(BaseModel):
    venue_id: UUID
    min_capacity: Optional[int] = None
    section: Optional[str] = None


class TableAvailabilityResponse(BaseModel):
    total_tables: int
    available: int
    occupied: int
    reserved: int
    tables: List[TableResponse]


