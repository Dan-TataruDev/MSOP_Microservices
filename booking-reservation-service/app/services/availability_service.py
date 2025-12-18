"""
Availability checking service.
Coordinates with inventory service to check availability.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from app.models.booking import Booking, BookingStatus, VenueType
from app.clients.inventory_client import inventory_client
from app.clients.pricing_client import pricing_client

logger = logging.getLogger(__name__)


class AvailabilityService:
    """
    Service for checking booking availability.
    Coordinates with inventory service but owns booking conflict logic.
    """
    
    @staticmethod
    async def check_availability(
        db: Session,
        venue_id: UUID,
        venue_type: VenueType,
        booking_date: datetime,
        booking_time: datetime,
        duration_minutes: Optional[int],
        party_size: int
    ) -> dict:
        """
        Check if a booking slot is available.
        
        Returns:
            {
                "available": bool,
                "reason": Optional[str],
                "conflicting_bookings": List[Booking],
                "inventory_available": bool,
                "estimated_price": Optional[Decimal]
            }
        """
        # Calculate end time
        if duration_minutes:
            end_time = booking_time + timedelta(minutes=duration_minutes)
        else:
            # Default duration based on venue type
            if venue_type == VenueType.RESTAURANT:
                end_time = booking_time + timedelta(hours=2)
            elif venue_type == VenueType.CAFE:
                end_time = booking_time + timedelta(hours=1)
            else:
                end_time = booking_time + timedelta(hours=24)  # Hotels, retail
        
        # Check for conflicting bookings in our database
        conflicting_bookings = db.query(Booking).filter(
            and_(
                Booking.venue_id == venue_id,
                Booking.status.in_([
                    BookingStatus.PENDING,
                    BookingStatus.CONFIRMED,
                    BookingStatus.CHECKED_IN
                ]),
                or_(
                    # Booking starts during existing booking
                    and_(
                        Booking.booking_time <= booking_time,
                        Booking.end_time > booking_time
                    ),
                    # Booking ends during existing booking
                    and_(
                        Booking.booking_time < end_time,
                        Booking.end_time >= end_time
                    ),
                    # Booking completely contains existing booking
                    and_(
                        Booking.booking_time >= booking_time,
                        Booking.end_time <= end_time
                    )
                )
            )
        ).all()
        
        # Check inventory availability (coordinate with inventory service)
        inventory_result = await inventory_client.check_availability(
            venue_id=venue_id,
            venue_type=venue_type.value,
            booking_time=booking_time,
            duration_minutes=duration_minutes,
            party_size=party_size,
            booking_date=booking_date
        )
        
        # Get price estimate (coordinate with pricing service)
        price_estimate = await pricing_client.estimate_price(
            venue_id=venue_id,
            venue_type=venue_type.value,
            booking_time=booking_time,
            party_size=party_size,
            duration_minutes=duration_minutes
        )
        
        # Determine availability
        booking_conflict = len(conflicting_bookings) > 0
        inventory_available = inventory_result.get("available", False)
        
        available = not booking_conflict and inventory_available
        
        reason = None
        if booking_conflict:
            reason = f"Time slot conflicts with {len(conflicting_bookings)} existing booking(s)"
        elif not inventory_available:
            reason = inventory_result.get("reason", "Inventory not available")
        
        return {
            "available": available,
            "reason": reason,
            "conflicting_bookings": conflicting_bookings,
            "inventory_available": inventory_available,
            "estimated_price": price_estimate.get("estimated_price"),
            "currency": price_estimate.get("currency", "USD"),
        }
    
    @staticmethod
    def get_available_slots(
        db: Session,
        venue_id: UUID,
        venue_type: VenueType,
        booking_date: datetime,
        party_size: int,
        duration_minutes: Optional[int] = None
    ) -> List[datetime]:
        """
        Get list of available time slots for a date.
        This is a simplified version - in production, this would be more sophisticated.
        """
        # This is a placeholder - in production, this would query available slots
        # from inventory service and filter by existing bookings
        return []


