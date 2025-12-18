"""Table capacity service."""
import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.table import Table, TableStatus
from app.schemas.table import TableCreate, TableUpdate, TableAvailabilityResponse
from app.events.publisher import event_publisher

logger = logging.getLogger(__name__)


class TableService:
    """Manages table availability and status transitions."""
    
    def create_table(self, db: Session, table_data: TableCreate) -> Table:
        """Create a new table."""
        table = Table(**table_data.model_dump())
        db.add(table)
        db.commit()
        db.refresh(table)
        return table
    
    def get_table(self, db: Session, table_id: UUID) -> Optional[Table]:
        """Get table by ID."""
        return db.query(Table).filter(Table.id == table_id).first()
    
    def update_status(self, db: Session, table_id: UUID, new_status: TableStatus) -> Optional[Table]:
        """Update table status and emit event."""
        table = self.get_table(db, table_id)
        if not table:
            return None
        
        old_status = table.status
        table.status = new_status
        table.status_updated_at = datetime.utcnow()
        db.commit()
        
        event_publisher.publish_table_status_changed(table_id, old_status.value, new_status.value)
        logger.info(f"Table {table.table_number} status: {old_status.value} -> {new_status.value}")
        return table
    
    def assign_booking(self, db: Session, table_id: UUID, booking_id: UUID) -> Optional[Table]:
        """Assign a booking to a table."""
        table = self.get_table(db, table_id)
        if not table:
            return None
        
        table.current_booking_id = booking_id
        table.status = TableStatus.RESERVED
        table.status_updated_at = datetime.utcnow()
        db.commit()
        
        event_publisher.publish_table_status_changed(table_id, "available", TableStatus.RESERVED.value)
        return table
    
    def release_booking(self, db: Session, table_id: UUID) -> Optional[Table]:
        """Release table from booking."""
        table = self.get_table(db, table_id)
        if not table:
            return None
        
        old_status = table.status
        table.current_booking_id = None
        table.status = TableStatus.CLEANING
        table.status_updated_at = datetime.utcnow()
        db.commit()
        
        event_publisher.publish_table_status_changed(table_id, old_status.value, TableStatus.CLEANING.value)
        return table
    
    def get_availability(
        self, db: Session, venue_id: UUID, min_capacity: Optional[int] = None, section: Optional[str] = None
    ) -> TableAvailabilityResponse:
        """Get table availability summary for a venue."""
        query = db.query(Table).filter(Table.venue_id == venue_id, Table.is_active == True)
        
        if min_capacity:
            query = query.filter(Table.capacity >= min_capacity)
        if section:
            query = query.filter(Table.section == section)
        
        tables = query.all()
        
        return TableAvailabilityResponse(
            total_tables=len(tables),
            available=sum(1 for t in tables if t.status == TableStatus.AVAILABLE),
            occupied=sum(1 for t in tables if t.status == TableStatus.OCCUPIED),
            reserved=sum(1 for t in tables if t.status == TableStatus.RESERVED),
            tables=tables,
        )
    
    def list_available_tables(
        self, db: Session, venue_id: UUID, min_capacity: Optional[int] = None, section: Optional[str] = None
    ) -> List[Table]:
        """List available tables for booking."""
        query = db.query(Table).filter(
            Table.venue_id == venue_id,
            Table.is_active == True,
            Table.status == TableStatus.AVAILABLE,
        )
        if min_capacity:
            query = query.filter(Table.capacity >= min_capacity)
        if section:
            query = query.filter(Table.section == section)
        return query.all()


table_service = TableService()


