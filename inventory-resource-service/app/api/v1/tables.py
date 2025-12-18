"""Table capacity API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.services.table_service import table_service
from app.models.table import TableStatus
from app.schemas.table import TableCreate, TableResponse, TableAvailabilityResponse

router = APIRouter(prefix="/tables", tags=["tables"])


@router.post("/", response_model=TableResponse, status_code=201)
def create_table(table_data: TableCreate, db: Session = Depends(get_db)):
    """Create a new table."""
    return table_service.create_table(db, table_data)


@router.get("/{table_id}", response_model=TableResponse)
def get_table(table_id: UUID, db: Session = Depends(get_db)):
    """Get table by ID."""
    table = table_service.get_table(db, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.patch("/{table_id}/status")
def update_table_status(table_id: UUID, status: TableStatus, db: Session = Depends(get_db)):
    """Update table status."""
    table = table_service.update_status(db, table_id, status)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"message": f"Table status updated to {status.value}"}


@router.get("/venue/{venue_id}/availability", response_model=TableAvailabilityResponse)
def get_table_availability(
    venue_id: UUID,
    min_capacity: Optional[int] = None,
    section: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get table availability summary for a venue."""
    return table_service.get_availability(db, venue_id, min_capacity, section)


@router.get("/venue/{venue_id}/available", response_model=List[TableResponse])
def list_available_tables(
    venue_id: UUID,
    min_capacity: Optional[int] = None,
    section: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List available tables for booking."""
    return table_service.list_available_tables(db, venue_id, min_capacity, section)


