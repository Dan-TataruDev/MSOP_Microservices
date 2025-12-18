"""
Main booking service - orchestrates booking lifecycle.
Coordinates with external services but owns booking state.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.booking import Booking, BookingStatus, BookingStatusHistory, VenueType
from app.schemas.booking import BookingCreate, BookingUpdate, BookingCancelRequest
from app.services.availability_service import AvailabilityService
from app.services.conflict_resolution import ConflictResolutionService
from app.clients.inventory_client import inventory_client
from app.clients.pricing_client import pricing_client
from app.clients.payment_client import payment_client
from app.utils.booking_reference import generate_booking_reference
from app.utils.status_transitions import validate_status_transition
from app.config import settings

logger = logging.getLogger(__name__)


class BookingService:
    """
    Main service for managing booking lifecycle.
    
    This service:
    - Owns booking state and data model
    - Coordinates with inventory, pricing, and payment services
    - Ensures consistency and idempotency
    - Manages status transitions
    - Emits events for downstream consumers
    """
    
    @staticmethod
    async def create_booking(
        db: Session,
        booking_data: BookingCreate,
        changed_by: str = "system"
    ) -> Booking:
        """
        Create a new booking.
        
        Process:
        1. Check idempotency
        2. Validate availability
        3. Get pricing
        4. Reserve inventory
        5. Create booking record
        6. Create payment intent
        7. Record status history
        """
        # Check idempotency
        if booking_data.idempotency_key:
            existing_booking_id = ConflictResolutionService.check_idempotency(
                db=db,
                idempotency_key=booking_data.idempotency_key,
                operation_type="create"
            )
            if existing_booking_id:
                existing_booking = db.query(Booking).filter(
                    Booking.id == existing_booking_id
                ).first()
                if existing_booking:
                    logger.info(f"Idempotent booking creation: {existing_booking_id}")
                    return existing_booking
        
        # Check availability
        availability = await AvailabilityService.check_availability(
            db=db,
            venue_id=booking_data.venue_id,
            venue_type=booking_data.venue_type,
            booking_date=booking_data.booking_date,
            booking_time=booking_data.booking_time,
            duration_minutes=booking_data.duration_minutes,
            party_size=booking_data.party_size
        )
        
        if not availability["available"]:
            raise ValueError(f"Booking not available: {availability.get('reason', 'Unknown reason')}")
        
        # Get pricing (coordinate with pricing service)
        pricing = await pricing_client.get_booking_price(
            venue_id=booking_data.venue_id,
            venue_type=booking_data.venue_type.value,
            booking_time=booking_data.booking_time,
            duration_minutes=booking_data.duration_minutes,
            party_size=booking_data.party_size,
            guest_id=booking_data.guest_id
        )
        
        # Calculate end time
        if booking_data.duration_minutes:
            end_time = booking_data.booking_time + timedelta(minutes=booking_data.duration_minutes)
        else:
            if booking_data.venue_type == VenueType.RESTAURANT:
                end_time = booking_data.booking_time + timedelta(hours=2)
            elif booking_data.venue_type == VenueType.CAFE:
                end_time = booking_data.booking_time + timedelta(hours=1)
            else:
                end_time = booking_data.booking_time + timedelta(hours=24)
        
        # Generate booking reference
        booking_reference = generate_booking_reference()
        
        # Create booking record
        booking = Booking(
            booking_reference=booking_reference,
            idempotency_key=booking_data.idempotency_key,
            guest_id=booking_data.guest_id,
            guest_name=booking_data.guest_name,
            guest_email=booking_data.guest_email,
            guest_phone=booking_data.guest_phone,
            venue_id=booking_data.venue_id,
            venue_type=booking_data.venue_type,
            venue_name=booking_data.venue_name,
            booking_date=booking_data.booking_date,
            booking_time=booking_data.booking_time,
            duration_minutes=booking_data.duration_minutes,
            end_time=end_time,
            party_size=booking_data.party_size,
            status=BookingStatus.PENDING,
            base_price=pricing["base_price"],
            tax_amount=pricing["tax_amount"],
            discount_amount=pricing["discount_amount"],
            total_price=pricing["total_price"],
            currency=pricing["currency"],
            special_requests=booking_data.special_requests,
            source=booking_data.source,
            expires_at=datetime.utcnow() + timedelta(
                minutes=settings.booking_confirmation_timeout_minutes
            )
        )
        
        db.add(booking)
        db.flush()  # Get booking ID without committing
        
        # Reserve inventory (coordinate with inventory service)
        try:
            inventory_reservation = await inventory_client.reserve_inventory(
                venue_id=booking_data.venue_id,
                venue_type=booking_data.venue_type.value,
                booking_time=booking_data.booking_time,
                duration_minutes=booking_data.duration_minutes,
                party_size=booking_data.party_size,
                booking_reference=booking_reference,
                booking_id=booking.id
            )
            booking.inventory_reservation_id = inventory_reservation.get("reservation_id")
            booking.inventory_item_id = inventory_reservation.get("inventory_item_id")
        except Exception as e:
            logger.error(f"Failed to reserve inventory: {e}")
            db.rollback()
            raise Exception(f"Failed to reserve inventory: {str(e)}")
        
        # Create payment intent (coordinate with payment service)
        try:
            payment_intent = await payment_client.create_payment_intent(
                booking_id=booking.id,
                booking_reference=booking_reference,
                amount=booking.total_price,
                currency=booking.currency,
                guest_id=booking_data.guest_id,
                metadata={
                    "venue_id": str(booking_data.venue_id),
                    "venue_type": booking_data.venue_type.value,
                    "booking_date": booking_data.booking_date.isoformat(),
                }
            )
            booking.payment_intent_id = payment_intent.get("payment_intent_id")
            booking.payment_status = "pending"
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            # Release inventory on payment failure
            if booking.inventory_reservation_id:
                await inventory_client.release_inventory(
                    reservation_id=booking.inventory_reservation_id,
                    booking_reference=booking_reference
                )
            db.rollback()
            raise Exception(f"Failed to create payment intent: {str(e)}")
        
        # Record status history
        status_history = BookingStatusHistory(
            booking_id=booking.id,
            from_status=None,
            to_status=BookingStatus.PENDING,
            changed_by=changed_by,
            reason="Booking created"
        )
        db.add(status_history)
        
        # Create idempotency key record
        if booking_data.idempotency_key:
            ConflictResolutionService.create_idempotency_key(
                db=db,
                idempotency_key=booking_data.idempotency_key,
                operation_type="create",
                booking_id=booking.id
            )
        
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking created: {booking.id} ({booking_reference})")
        return booking
    
    @staticmethod
    async def update_booking(
        db: Session,
        booking_id: UUID,
        booking_data: BookingUpdate,
        expected_version: int,
        changed_by: str = "system"
    ) -> Optional[Booking]:
        """
        Update an existing booking.
        
        Process:
        1. Check optimistic lock
        2. Check idempotency
        3. Validate new availability if time changed
        4. Update inventory reservation if needed
        5. Get updated pricing
        6. Update booking record
        7. Record status history
        """
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None
        
        # Check optimistic lock
        if settings.optimistic_locking_enabled:
            if not ConflictResolutionService.check_optimistic_lock(
                db=db,
                booking_id=booking_id,
                expected_version=expected_version
            ):
                raise ValueError("Booking was modified by another operation. Please refresh and try again.")
        
        # Check idempotency
        if booking_data.idempotency_key:
            existing_booking_id = ConflictResolutionService.check_idempotency(
                db=db,
                idempotency_key=booking_data.idempotency_key,
                operation_type="update"
            )
            if existing_booking_id and existing_booking_id != booking_id:
                raise ValueError("Idempotency key already used for different booking")
        
        # Check if time changed - need to recheck availability
        time_changed = (
            booking_data.booking_time and booking_data.booking_time != booking.booking_time
        ) or (
            booking_data.party_size and booking_data.party_size != booking.party_size
        )
        
        if time_changed:
            new_time = booking_data.booking_time or booking.booking_time
            new_party_size = booking_data.party_size or booking.party_size
            
            availability = await AvailabilityService.check_availability(
                db=db,
                venue_id=booking.venue_id,
                venue_type=booking.venue_type,
                booking_date=booking.booking_date,
                booking_time=new_time,
                duration_minutes=booking_data.duration_minutes or booking.duration_minutes,
                party_size=new_party_size
            )
            
            if not availability["available"]:
                raise ValueError(f"New time slot not available: {availability.get('reason')}")
            
            # Update inventory reservation
            if booking.inventory_reservation_id:
                await inventory_client.update_inventory_reservation(
                    reservation_id=booking.inventory_reservation_id,
                    booking_time=new_time,
                    duration_minutes=booking_data.duration_minutes or booking.duration_minutes,
                    party_size=new_party_size
                )
        
        # Get updated pricing if time or party size changed
        if time_changed:
            pricing = await pricing_client.get_booking_price(
                venue_id=booking.venue_id,
                venue_type=booking.venue_type.value,
                booking_time=booking_data.booking_time or booking.booking_time,
                duration_minutes=booking_data.duration_minutes or booking.duration_minutes,
                party_size=booking_data.party_size or booking.party_size,
                guest_id=booking.guest_id
            )
            
            booking.base_price = pricing["base_price"]
            booking.tax_amount = pricing["tax_amount"]
            booking.discount_amount = pricing["discount_amount"]
            booking.total_price = pricing["total_price"]
        
        # Update booking fields
        if booking_data.booking_time:
            booking.booking_time = booking_data.booking_time
            if booking_data.duration_minutes:
                booking.end_time = booking_data.booking_time + timedelta(
                    minutes=booking_data.duration_minutes
                )
            booking.duration_minutes = booking_data.duration_minutes
        
        if booking_data.party_size:
            booking.party_size = booking_data.party_size
        
        if booking_data.special_requests is not None:
            booking.special_requests = booking_data.special_requests
        
        # Increment version for optimistic locking
        ConflictResolutionService.increment_version(db, booking)
        
        # Record status history if status changed
        # (Status changes are handled separately via update_status)
        
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking updated: {booking.id}")
        return booking
    
    @staticmethod
    async def cancel_booking(
        db: Session,
        booking_id: UUID,
        cancel_data: BookingCancelRequest,
        expected_version: Optional[int] = None
    ) -> Optional[Booking]:
        """
        Cancel a booking.
        
        Process:
        1. Check optimistic lock
        2. Check idempotency
        3. Validate status can be cancelled
        4. Release inventory
        5. Process refund if payment made
        6. Update booking status
        7. Record status history
        """
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None
        
        # Check if can be cancelled
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED, BookingStatus.EXPIRED]:
            raise ValueError(f"Cannot cancel booking in status: {booking.status}")
        
        # Check optimistic lock
        if settings.optimistic_locking_enabled and expected_version is not None:
            if not ConflictResolutionService.check_optimistic_lock(
                db=db,
                booking_id=booking_id,
                expected_version=expected_version
            ):
                raise ValueError("Booking was modified by another operation. Please refresh and try again.")
        
        # Check idempotency
        if cancel_data.idempotency_key:
            existing_booking_id = ConflictResolutionService.check_idempotency(
                db=db,
                idempotency_key=cancel_data.idempotency_key,
                operation_type="cancel"
            )
            if existing_booking_id and existing_booking_id != booking_id:
                raise ValueError("Idempotency key already used")
        
        # Release inventory
        if booking.inventory_reservation_id:
            await inventory_client.release_inventory(
                reservation_id=booking.inventory_reservation_id,
                booking_reference=booking.booking_reference
            )
        
        # Process refund if payment was made
        if booking.payment_intent_id and booking.payment_status == "completed":
            try:
                await payment_client.refund_payment(
                    payment_intent_id=booking.payment_intent_id,
                    booking_id=booking_id,
                    reason=cancel_data.reason
                )
                booking.payment_status = "refunded"
            except Exception as e:
                logger.error(f"Failed to refund payment: {e}")
                # Continue with cancellation even if refund fails
        
        # Update booking status
        old_status = booking.status
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = cancel_data.reason
        booking.cancelled_by = cancel_data.cancelled_by
        
        ConflictResolutionService.increment_version(db, booking)
        
        # Record status history
        status_history = BookingStatusHistory(
            booking_id=booking.id,
            from_status=old_status,
            to_status=BookingStatus.CANCELLED,
            changed_by=cancel_data.cancelled_by,
            reason=cancel_data.reason
        )
        db.add(status_history)
        
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking cancelled: {booking.id}")
        return booking
    
    @staticmethod
    def update_booking_status(
        db: Session,
        booking_id: UUID,
        new_status: BookingStatus,
        changed_by: str,
        reason: Optional[str] = None,
        expected_version: Optional[int] = None
    ) -> Optional[Booking]:
        """
        Update booking status with validation.
        """
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None
        
        # Validate transition
        if not validate_status_transition(booking.status, new_status):
            raise ValueError(
                f"Invalid status transition from {booking.status} to {new_status}"
            )
        
        # Check optimistic lock
        if settings.optimistic_locking_enabled and expected_version is not None:
            if not ConflictResolutionService.check_optimistic_lock(
                db=db,
                booking_id=booking_id,
                expected_version=expected_version
            ):
                raise ValueError("Booking was modified by another operation.")
        
        old_status = booking.status
        booking.status = new_status
        
        # Update timestamps
        now = datetime.utcnow()
        if new_status == BookingStatus.CONFIRMED:
            booking.confirmed_at = now
        elif new_status == BookingStatus.CHECKED_IN:
            booking.checked_in_at = now
        elif new_status == BookingStatus.COMPLETED:
            booking.completed_at = now
        
        ConflictResolutionService.increment_version(db, booking)
        
        # Record status history
        status_history = BookingStatusHistory(
            booking_id=booking.id,
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            reason=reason
        )
        db.add(status_history)
        
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking status updated: {booking.id} {old_status} -> {new_status}")
        return booking
    
    @staticmethod
    def get_booking_by_id(db: Session, booking_id: UUID) -> Optional[Booking]:
        """Get booking by ID."""
        return db.query(Booking).filter(Booking.id == booking_id).first()
    
    @staticmethod
    def get_booking_by_reference(
        db: Session,
        booking_reference: str
    ) -> Optional[Booking]:
        """Get booking by reference."""
        return db.query(Booking).filter(
            Booking.booking_reference == booking_reference
        ).first()
    
    @staticmethod
    def get_bookings_by_guest(
        db: Session,
        guest_id: UUID,
        status: Optional[BookingStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Booking]:
        """Get bookings for a guest."""
        query = db.query(Booking).filter(Booking.guest_id == guest_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.booking_time.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_bookings_by_venue(
        db: Session,
        venue_id: UUID,
        status: Optional[BookingStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Booking]:
        """Get bookings for a venue."""
        query = db.query(Booking).filter(Booking.venue_id == venue_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        if start_date:
            query = query.filter(Booking.booking_time >= start_date)
        
        if end_date:
            query = query.filter(Booking.booking_time <= end_date)
        
        return query.order_by(Booking.booking_time.asc()).limit(limit).offset(offset).all()


