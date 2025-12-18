"""
Event handlers for processing incoming events from other services.

This module defines how the housekeeping service reacts to external events.
Each handler transforms an external event into internal operational tasks.

Key Design Principles:
1. Handlers are stateless - all state is in the database
2. Handlers are idempotent - safe to process same event multiple times
3. No direct calls to external services - only event consumption
4. Store minimal external references - just IDs needed for correlation
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.events.consumer import event_consumer
from app.events.publisher import event_publisher
from app.models.task import Task, TaskType, TaskStatus, TaskPriority
from app.models.maintenance import MaintenanceRequest, MaintenanceCategory, MaintenancePriority
from app.utils.task_reference import generate_task_reference
from app.utils.priority_calculator import calculate_priority, calculate_due_date

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Get database session for event handlers."""
    return SessionLocal()


# ==================== Booking Event Handlers ====================

async def handle_booking_completed(payload: Dict[str, Any]) -> None:
    """
    Handle booking completion (checkout) event.
    
    When a guest checks out, automatically create a checkout cleaning task.
    
    Event payload expected:
    {
        "booking_id": "uuid",
        "booking_reference": "BK-123456",
        "venue_id": "uuid",
        "venue_type": "room"
    }
    """
    logger.info(f"Processing booking.completed event: {payload}")
    
    db = get_db()
    try:
        # Extract data from event (no external API calls)
        venue_id = UUID(payload.get("venue_id")) if payload.get("venue_id") else None
        booking_reference = payload.get("booking_reference")
        venue_type = payload.get("venue_type", "room")
        
        # Check for existing task (idempotency)
        existing = db.query(Task).filter(
            Task.source_booking_reference == booking_reference,
            Task.task_type == TaskType.CHECKOUT_CLEANING
        ).first()
        
        if existing:
            logger.info(f"Task already exists for booking {booking_reference}")
            return
        
        # Create checkout cleaning task
        now = datetime.utcnow()
        due_date = calculate_due_date(
            base_time=now,
            sla_minutes=settings.checkout_cleaning_sla
        )
        
        task = Task(
            task_reference=generate_task_reference("CLN"),
            task_type=TaskType.CHECKOUT_CLEANING,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,  # Checkout cleaning is always high priority
            venue_id=venue_id,
            venue_type=venue_type,
            source_event_type="booking.completed",
            source_booking_reference=booking_reference,
            title=f"Checkout Cleaning - {booking_reference}",
            description="Full room cleaning after guest checkout",
            scheduled_date=now,
            due_date=due_date,
            estimated_duration_minutes=settings.default_cleaning_duration_minutes,
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Publish task created event
        event_publisher.publish_task_created({
            "id": task.id,
            "task_reference": task.task_reference,
            "task_type": task.task_type.value,
            "priority": task.priority.value,
            "venue_id": task.venue_id,
            "venue_type": task.venue_type,
            "scheduled_date": task.scheduled_date,
            "due_date": task.due_date,
            "source_event_type": task.source_event_type,
        })
        
        logger.info(f"Created checkout cleaning task: {task.task_reference}")
        
    except Exception as e:
        logger.error(f"Error handling booking.completed: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


async def handle_booking_confirmed(payload: Dict[str, Any]) -> None:
    """
    Handle booking confirmation event.
    
    When a booking is confirmed, we may want to:
    - Schedule pre-arrival inspection
    - Note VIP status for priority handling
    
    Event payload expected:
    {
        "booking_id": "uuid",
        "booking_reference": "BK-123456",
        "guest_id": "uuid",
        "venue_id": "uuid",
        "booking_time": "ISO8601"
    }
    """
    logger.info(f"Processing booking.confirmed event: {payload}")
    
    # For now, we just log the event
    # VIP status could trigger inspection task scheduling
    # Future: Check guest profile for VIP status via event data
    pass


async def handle_booking_cancelled(payload: Dict[str, Any]) -> None:
    """
    Handle booking cancellation event.
    
    When a booking is cancelled, we may need to:
    - Cancel any pre-scheduled cleaning tasks
    - Adjust room scheduling
    
    Event payload expected:
    {
        "booking_id": "uuid",
        "booking_reference": "BK-123456",
        "venue_id": "uuid",
        "reason": "optional reason"
    }
    """
    logger.info(f"Processing booking.cancelled event: {payload}")
    
    db = get_db()
    try:
        booking_reference = payload.get("booking_reference")
        
        # Find and cancel any pending tasks for this booking
        pending_tasks = db.query(Task).filter(
            Task.source_booking_reference == booking_reference,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED])
        ).all()
        
        for task in pending_tasks:
            task.status = TaskStatus.CANCELLED
            logger.info(f"Cancelled task {task.task_reference} due to booking cancellation")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error handling booking.cancelled: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


# ==================== Inventory Event Handlers ====================

async def handle_low_stock_alert(payload: Dict[str, Any]) -> None:
    """
    Handle low stock alert from inventory service.
    
    Create a restocking task when inventory falls below threshold.
    
    Event payload expected:
    {
        "item_id": "uuid",
        "item_name": "Towels",
        "current_quantity": 10,
        "low_threshold": 15,
        "location": "Floor 3 Storage"
    }
    """
    logger.info(f"Processing inventory.low_stock event: {payload}")
    
    db = get_db()
    try:
        item_id = payload.get("item_id")
        item_name = payload.get("item_name", "Unknown Item")
        location = payload.get("location")
        
        # Check for existing pending restocking task (idempotency)
        existing = db.query(Task).filter(
            Task.task_type == TaskType.RESTOCKING,
            Task.description.contains(item_id) if item_id else False,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ).first()
        
        if existing:
            logger.info(f"Restocking task already exists for item {item_name}")
            return
        
        now = datetime.utcnow()
        
        task = Task(
            task_reference=generate_task_reference("RST"),
            task_type=TaskType.RESTOCKING,
            status=TaskStatus.PENDING,
            priority=TaskPriority.NORMAL,
            location_name=location,
            source_event_type="inventory.low_stock",
            title=f"Restock: {item_name}",
            description=f"Low stock alert - Item ID: {item_id}. Current quantity below threshold.",
            scheduled_date=now,
            due_date=now + timedelta(hours=4),
            estimated_duration_minutes=30,
        )
        
        db.add(task)
        db.commit()
        
        logger.info(f"Created restocking task: {task.task_reference}")
        
    except Exception as e:
        logger.error(f"Error handling inventory.low_stock: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


async def handle_critical_stock_alert(payload: Dict[str, Any]) -> None:
    """
    Handle critical stock alert from inventory service.
    
    Create an URGENT restocking task when inventory is critically low.
    """
    logger.info(f"Processing inventory.critical_stock event: {payload}")
    
    db = get_db()
    try:
        item_id = payload.get("item_id")
        item_name = payload.get("item_name", "Unknown Item")
        location = payload.get("location")
        
        now = datetime.utcnow()
        
        task = Task(
            task_reference=generate_task_reference("RST"),
            task_type=TaskType.RESTOCKING,
            status=TaskStatus.PENDING,
            priority=TaskPriority.URGENT,  # Critical = Urgent priority
            location_name=location,
            source_event_type="inventory.critical_stock",
            title=f"URGENT Restock: {item_name}",
            description=f"Critical stock alert - Item ID: {item_id}. Immediate restocking required.",
            scheduled_date=now,
            due_date=now + timedelta(hours=1),  # 1 hour SLA for critical
            estimated_duration_minutes=30,
        )
        
        db.add(task)
        db.commit()
        
        # Publish critical alert
        event_publisher.publish_critical_alert(
            alert_type="critical_stock",
            message=f"Critical stock level for {item_name}",
            requires_immediate_action=True
        )
        
        logger.info(f"Created urgent restocking task: {task.task_reference}")
        
    except Exception as e:
        logger.error(f"Error handling inventory.critical_stock: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


async def handle_room_status_changed(payload: Dict[str, Any]) -> None:
    """
    Handle room status change from inventory service.
    
    React to room status changes that may require housekeeping action.
    
    Event payload expected:
    {
        "room_id": "uuid",
        "old_status": "occupied",
        "new_status": "vacant"
    }
    """
    logger.info(f"Processing resource.room_status_changed event: {payload}")
    
    # This is informational - actual task creation happens via booking events
    # Could be used to sync local state or trigger inspections
    pass


# ==================== Guest Interaction Event Handlers ====================

async def handle_guest_complaint(payload: Dict[str, Any]) -> None:
    """
    Handle guest complaint that may require maintenance.
    
    Event payload expected:
    {
        "complaint_id": "uuid",
        "guest_id": "uuid",
        "venue_id": "uuid",
        "category": "maintenance",
        "description": "AC not working"
    }
    """
    logger.info(f"Processing guest.complaint_filed event: {payload}")
    
    # Only process maintenance-related complaints
    if payload.get("category") != "maintenance":
        return
    
    db = get_db()
    try:
        venue_id = UUID(payload.get("venue_id")) if payload.get("venue_id") else None
        guest_id = UUID(payload.get("guest_id")) if payload.get("guest_id") else None
        description = payload.get("description", "")
        
        # Create maintenance request
        from app.utils.task_reference import generate_maintenance_reference
        
        request = MaintenanceRequest(
            request_reference=generate_maintenance_reference(),
            category=MaintenanceCategory.OTHER,  # Will be triaged
            priority=MaintenancePriority.HIGH,  # Guest-reported = high priority
            venue_id=venue_id,
            reported_by_guest_id=guest_id,
            source_event_type="guest.complaint_filed",
            title=f"Guest Reported Issue",
            description=description,
            guest_impact_level="major",
        )
        
        db.add(request)
        db.commit()
        
        event_publisher.publish_maintenance_reported({
            "id": request.id,
            "request_reference": request.request_reference,
            "category": request.category.value,
            "priority": request.priority.value,
            "venue_id": request.venue_id,
            "title": request.title,
        })
        
        logger.info(f"Created maintenance request from guest complaint: {request.request_reference}")
        
    except Exception as e:
        logger.error(f"Error handling guest.complaint_filed: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


async def handle_maintenance_request_from_guest(payload: Dict[str, Any]) -> None:
    """
    Handle direct maintenance request from guest interaction service.
    
    Event payload expected:
    {
        "request_id": "uuid",
        "guest_id": "uuid",
        "venue_id": "uuid",
        "issue_type": "plumbing",
        "description": "Shower not draining",
        "urgency": "normal"
    }
    """
    logger.info(f"Processing guest.maintenance_requested event: {payload}")
    
    db = get_db()
    try:
        venue_id = UUID(payload.get("venue_id")) if payload.get("venue_id") else None
        guest_id = UUID(payload.get("guest_id")) if payload.get("guest_id") else None
        issue_type = payload.get("issue_type", "other")
        description = payload.get("description", "")
        urgency = payload.get("urgency", "normal")
        
        # Map issue type to category
        category_map = {
            "plumbing": MaintenanceCategory.PLUMBING,
            "electrical": MaintenanceCategory.ELECTRICAL,
            "hvac": MaintenanceCategory.HVAC,
            "ac": MaintenanceCategory.HVAC,
            "heating": MaintenanceCategory.HVAC,
            "appliance": MaintenanceCategory.APPLIANCE,
            "tv": MaintenanceCategory.APPLIANCE,
            "furniture": MaintenanceCategory.FURNITURE,
        }
        category = category_map.get(issue_type.lower(), MaintenanceCategory.OTHER)
        
        # Map urgency to priority
        priority_map = {
            "low": MaintenancePriority.NORMAL,
            "normal": MaintenancePriority.HIGH,  # Guest requests default to high
            "high": MaintenancePriority.URGENT,
            "emergency": MaintenancePriority.EMERGENCY,
        }
        priority = priority_map.get(urgency.lower(), MaintenancePriority.HIGH)
        
        from app.utils.task_reference import generate_maintenance_reference
        
        request = MaintenanceRequest(
            request_reference=generate_maintenance_reference(),
            category=category,
            priority=priority,
            venue_id=venue_id,
            reported_by_guest_id=guest_id,
            source_event_type="guest.maintenance_requested",
            title=f"Guest Request: {issue_type.title()}",
            description=description,
            guest_impact_level="major" if priority in [MaintenancePriority.URGENT, MaintenancePriority.EMERGENCY] else "minor",
        )
        
        db.add(request)
        db.commit()
        
        event_publisher.publish_maintenance_reported({
            "id": request.id,
            "request_reference": request.request_reference,
            "category": request.category.value,
            "priority": request.priority.value,
            "venue_id": request.venue_id,
            "title": request.title,
        })
        
        logger.info(f"Created maintenance request: {request.request_reference}")
        
    except Exception as e:
        logger.error(f"Error handling guest.maintenance_requested: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


# ==================== Handler Registration ====================

def register_handlers() -> None:
    """Register all event handlers with the event consumer."""
    logger.info("Registering event handlers...")
    
    # Booking events
    event_consumer.register_handler("booking.completed", handle_booking_completed)
    event_consumer.register_handler("booking.confirmed", handle_booking_confirmed)
    event_consumer.register_handler("booking.cancelled", handle_booking_cancelled)
    
    # Inventory events
    event_consumer.register_handler("inventory.low_stock", handle_low_stock_alert)
    event_consumer.register_handler("inventory.critical_stock", handle_critical_stock_alert)
    event_consumer.register_handler("resource.room_status_changed", handle_room_status_changed)
    
    # Guest interaction events
    event_consumer.register_handler("guest.complaint_filed", handle_guest_complaint)
    event_consumer.register_handler("guest.maintenance_requested", handle_maintenance_request_from_guest)
    
    logger.info("All event handlers registered successfully")
