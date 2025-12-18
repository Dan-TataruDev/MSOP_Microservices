"""
API endpoints for booking management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    AvailabilityCheckRequest,
    AvailabilityCheckResponse,
    BookingStatusUpdate,
    BookingCancelRequest,
)
from app.services.booking_service import BookingService
from app.services.availability_service import AvailabilityService
from app.events.publisher import event_publisher
from app.models.booking import BookingStatus

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new booking.
    
    This endpoint:
    - Checks availability
    - Coordinates with inventory, pricing, and payment services
    - Creates booking record
    - Emits booking.created event
    """
    try:
        booking = await BookingService.create_booking(
            db=db,
            booking_data=booking_data,
            changed_by=str(booking_data.guest_id)
        )
        
        # Emit event
        event_publisher.publish_booking_created(
            booking_id=booking.id,
            booking_data={
                "booking_reference": booking.booking_reference,
                "guest_id": booking.guest_id,
                "venue_id": booking.venue_id,
                "venue_type": booking.venue_type.value,
                "booking_time": booking.booking_time,
                "party_size": booking.party_size,
                "total_price": booking.total_price,
                "currency": booking.currency,
                "status": booking.status.value,
            }
        )
        
        return booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db)
):
    """Get booking by ID."""
    booking = BookingService.get_booking_by_id(db=db, booking_id=booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking


@router.get("/reference/{booking_reference}", response_model=BookingResponse)
def get_booking_by_reference(
    booking_reference: str,
    db: Session = Depends(get_db)
):
    """Get booking by reference."""
    booking = BookingService.get_booking_by_reference(
        db=db,
        booking_reference=booking_reference
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: UUID,
    booking_data: BookingUpdate,
    expected_version: int = Query(..., description="Current booking version for optimistic locking"),
    db: Session = Depends(get_db)
):
    """
    Update an existing booking.
    
    Requires expected_version for optimistic locking to prevent conflicts.
    """
    try:
        booking = await BookingService.update_booking(
            db=db,
            booking_id=booking_id,
            booking_data=booking_data,
            expected_version=expected_version,
            changed_by="guest"  # In production, get from auth token
        )
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Emit event
        event_publisher.publish_booking_updated(
            booking_id=booking.id,
            changes=booking_data.model_dump(exclude_unset=True)
        )
        
        return booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update booking: {str(e)}"
        )


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    cancel_data: BookingCancelRequest,
    expected_version: Optional[int] = Query(None, description="Current booking version for optimistic locking"),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking.
    
    This will:
    - Release inventory
    - Process refund if payment was made
    - Update booking status
    - Emit booking.cancelled event
    """
    try:
        booking = await BookingService.cancel_booking(
            db=db,
            booking_id=booking_id,
            cancel_data=cancel_data,
            expected_version=expected_version
        )
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Emit event
        event_publisher.publish_booking_cancelled(
            booking_id=booking.id,
            booking_reference=booking.booking_reference,
            guest_id=booking.guest_id,
            venue_id=booking.venue_id,
            reason=cancel_data.reason,
            cancelled_by=cancel_data.cancelled_by
        )
        
        return booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel booking: {str(e)}"
        )


@router.post("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: UUID,
    status_data: BookingStatusUpdate,
    expected_version: Optional[int] = Query(None, description="Current booking version for optimistic locking"),
    db: Session = Depends(get_db)
):
    """
    Update booking status.
    
    Validates status transitions according to state machine.
    """
    try:
        booking = BookingService.update_booking_status(
            db=db,
            booking_id=booking_id,
            new_status=status_data.status,
            changed_by=status_data.changed_by or "system",
            reason=status_data.reason,
            expected_version=expected_version
        )
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Emit event
        event_publisher.publish_booking_status_changed(
            booking_id=booking.id,
            booking_reference=booking.booking_reference,
            from_status=status_data.status.value,
            to_status=status_data.status.value,
            changed_by=status_data.changed_by or "system"
        )
        
        # Emit specific events for important status changes
        if status_data.status == BookingStatus.CONFIRMED:
            event_publisher.publish_booking_confirmed(
                booking_id=booking.id,
                booking_data={
                    "booking_reference": booking.booking_reference,
                    "guest_id": booking.guest_id,
                    "venue_id": booking.venue_id,
                    "booking_time": booking.booking_time,
                }
            )
        elif status_data.status == BookingStatus.CHECKED_IN:
            event_publisher.publish_booking_checked_in(
                booking_id=booking.id,
                booking_reference=booking.booking_reference,
                venue_id=booking.venue_id
            )
        elif status_data.status == BookingStatus.COMPLETED:
            event_publisher.publish_booking_completed(
                booking_id=booking.id,
                booking_reference=booking.booking_reference,
                venue_id=booking.venue_id
            )
        
        return booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status: {str(e)}"
        )


@router.get("/guest/{guest_id}", response_model=BookingListResponse)
def get_guest_bookings(
    guest_id: UUID,
    status: Optional[BookingStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all bookings for a guest."""
    bookings = BookingService.get_bookings_by_guest(
        db=db,
        guest_id=guest_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    total = len(bookings)  # In production, use count query
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    return BookingListResponse(
        bookings=bookings,
        total=total,
        page=(offset // limit) + 1,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/venue/{venue_id}", response_model=BookingListResponse)
def get_venue_bookings(
    venue_id: UUID,
    status: Optional[BookingStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all bookings for a venue."""
    bookings = BookingService.get_bookings_by_venue(
        db=db,
        venue_id=venue_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    total = len(bookings)  # In production, use count query
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    return BookingListResponse(
        bookings=bookings,
        total=total,
        page=(offset // limit) + 1,
        page_size=limit,
        total_pages=total_pages
    )


@router.post("/availability/check", response_model=AvailabilityCheckResponse)
async def check_availability(
    request: AvailabilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check availability for a booking slot.
    
    This endpoint:
    - Checks for conflicting bookings in our database
    - Coordinates with inventory service
    - Gets price estimate from pricing service
    """
    availability = await AvailabilityService.check_availability(
        db=db,
        venue_id=request.venue_id,
        venue_type=request.venue_type,
        booking_date=request.booking_date,
        booking_time=request.booking_time,
        duration_minutes=request.duration_minutes,
        party_size=request.party_size
    )
    
    return AvailabilityCheckResponse(
        available=availability["available"],
        venue_id=request.venue_id,
        booking_date=request.booking_date,
        booking_time=request.booking_time,
        party_size=request.party_size,
        reason=availability.get("reason"),
        estimated_price=availability.get("estimated_price"),
        currency=availability.get("currency", "USD"),
        inventory_available=availability.get("inventory_available"),
    )


