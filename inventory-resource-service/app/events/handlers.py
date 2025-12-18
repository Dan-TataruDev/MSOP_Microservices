"""Event handlers for incoming events from other services."""
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.events.consumer import event_consumer

logger = logging.getLogger(__name__)


def handle_booking_confirmed(payload: Dict[str, Any]) -> None:
    """Handle booking confirmation - reserve room/table."""
    logger.info(f"Processing booking.confirmed: {payload}")
    db = SessionLocal()
    try:
        from app.services.room_service import room_service
        from app.services.table_service import table_service
        
        booking_id = UUID(payload.get("booking_id"))
        resource_type = payload.get("resource_type")
        resource_id = UUID(payload.get("resource_id"))
        
        if resource_type == "room":
            room_service.assign_booking(db, resource_id, booking_id)
        elif resource_type == "table":
            table_service.assign_booking(db, resource_id, booking_id)
    finally:
        db.close()


def handle_booking_cancelled(payload: Dict[str, Any]) -> None:
    """Handle booking cancellation - release room/table."""
    logger.info(f"Processing booking.cancelled: {payload}")
    db = SessionLocal()
    try:
        from app.services.room_service import room_service
        from app.services.table_service import table_service
        
        resource_type = payload.get("resource_type")
        resource_id = UUID(payload.get("resource_id"))
        
        if resource_type == "room":
            room_service.release_booking(db, resource_id)
        elif resource_type == "table":
            table_service.release_booking(db, resource_id)
    finally:
        db.close()


def handle_housekeeping_completed(payload: Dict[str, Any]) -> None:
    """Handle housekeeping completion - update room status and consume supplies."""
    logger.info(f"Processing housekeeping.completed: {payload}")
    db = SessionLocal()
    try:
        from app.services.room_service import room_service
        from app.services.inventory_service import inventory_service
        from app.models.room import RoomStatus
        from app.models.inventory import TransactionType
        
        room_id = UUID(payload.get("room_id"))
        room_service.update_status(db, room_id, RoomStatus.AVAILABLE)
        
        # Consume supplies used during cleaning
        supplies_used = payload.get("supplies_used", [])
        for supply in supplies_used:
            inventory_service.adjust_stock(
                db=db,
                item_id=UUID(supply["item_id"]),
                quantity_change=-supply["quantity"],
                transaction_type=TransactionType.USAGE,
                reference_type="housekeeping",
                reference_id=UUID(payload.get("task_id")),
            )
    finally:
        db.close()


def handle_supplier_delivery(payload: Dict[str, Any]) -> None:
    """Handle supplier delivery - restock inventory."""
    logger.info(f"Processing supplier.delivery: {payload}")
    db = SessionLocal()
    try:
        from app.services.inventory_service import inventory_service
        from app.models.inventory import TransactionType
        
        delivery_id = UUID(payload.get("delivery_id"))
        items = payload.get("items", [])
        
        for item in items:
            inventory_service.adjust_stock(
                db=db,
                item_id=UUID(item["item_id"]),
                quantity_change=item["quantity"],
                transaction_type=TransactionType.RESTOCK,
                reference_type="supplier",
                reference_id=delivery_id,
            )
    finally:
        db.close()


def register_handlers() -> None:
    """Register all event handlers."""
    event_consumer.register_handler("booking.confirmed", handle_booking_confirmed)
    event_consumer.register_handler("booking.cancelled", handle_booking_cancelled)
    event_consumer.register_handler("housekeeping.completed", handle_housekeeping_completed)
    event_consumer.register_handler("supplier.delivery", handle_supplier_delivery)
    logger.info("All event handlers registered")


