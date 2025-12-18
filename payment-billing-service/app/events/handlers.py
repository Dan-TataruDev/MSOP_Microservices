"""
Event handlers for consuming events from other services.
"""
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.events.consumer import event_consumer
from app.services.payment_service import PaymentService
from app.services.billing_service import BillingService
from app.services.invoice_service import InvoiceService
from app.config import settings
from app.models.payment import PaymentMethod

logger = logging.getLogger(__name__)


def handle_booking_created(payload: Dict[str, Any]) -> None:
    """
    Handle booking.created event from booking service.
    
    This handler can initiate payment if required, or wait for
    explicit payment initiation from the frontend.
    """
    db = SessionLocal()
    try:
        booking_id = UUID(payload.get("booking_id"))
        booking_reference = payload.get("booking_reference")
        total_price = payload.get("total_price")
        currency = payload.get("currency", "USD")
        
        logger.info(f"Received booking.created event for booking {booking_id}")
        
        # In this implementation, we don't auto-initiate payment
        # Payment is initiated explicitly via API when guest is ready to pay
        # This allows for payment method selection and 3D Secure flows
        
        # However, we could create a pending payment record here if needed
        # For now, we just log the event
        
    except Exception as e:
        logger.error(f"Error handling booking.created event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def handle_booking_cancelled(payload: Dict[str, Any]) -> None:
    """
    Handle booking.cancelled event from booking service.
    
    If auto_refund_on_cancellation is enabled, initiate refund.
    """
    db = SessionLocal()
    try:
        booking_id = UUID(payload.get("booking_id"))
        booking_reference = payload.get("booking_reference")
        
        logger.info(f"Received booking.cancelled event for booking {booking_id}")
        
        if settings.auto_refund_on_cancellation:
            # Find payment for this booking
            from app.models.payment import Payment, PaymentStatus
            payment = db.query(Payment).filter(
                Payment.booking_id == booking_id,
                Payment.status == PaymentStatus.COMPLETED
            ).first()
            
            if payment:
                from app.services.refund_service import RefundService
                from app.schemas.refund import RefundCreate
                
                refund_service = RefundService(db)
                refund_data = RefundCreate(
                    payment_id=payment.id,
                    booking_id=booking_id,
                    booking_reference=booking_reference,
                    reason="Booking cancelled",
                    refund_type="cancellation",
                )
                
                refund_service.create_refund(refund_data)
                logger.info(f"Auto-refund initiated for cancelled booking {booking_id}")
        
    except Exception as e:
        logger.error(f"Error handling booking.cancelled event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def register_handlers() -> None:
    """Register all event handlers."""
    event_consumer.register_handler("booking.created", handle_booking_created)
    event_consumer.register_handler("booking.cancelled", handle_booking_cancelled)
    logger.info("Event handlers registered")


