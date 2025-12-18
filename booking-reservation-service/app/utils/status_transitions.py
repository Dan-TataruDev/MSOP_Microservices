"""
Status transition validation and management.
Ensures correct state machine transitions for bookings.
"""
from app.models.booking import BookingStatus
from typing import Set, Dict


# Valid status transitions
STATUS_TRANSITIONS: Dict[BookingStatus, Set[BookingStatus]] = {
    BookingStatus.PENDING: {
        BookingStatus.CONFIRMED,
        BookingStatus.CANCELLED,
        BookingStatus.EXPIRED,
    },
    BookingStatus.CONFIRMED: {
        BookingStatus.CHECKED_IN,
        BookingStatus.CANCELLED,
        BookingStatus.COMPLETED,
    },
    BookingStatus.CHECKED_IN: {
        BookingStatus.COMPLETED,
        BookingStatus.CANCELLED,
    },
    BookingStatus.COMPLETED: set(),  # Terminal state
    BookingStatus.CANCELLED: set(),  # Terminal state
    BookingStatus.NO_SHOW: set(),  # Terminal state
    BookingStatus.EXPIRED: set(),  # Terminal state
}


def validate_status_transition(
    from_status: BookingStatus,
    to_status: BookingStatus
) -> bool:
    """
    Validate if a status transition is allowed.
    
    Args:
        from_status: Current booking status
        to_status: Desired booking status
        
    Returns:
        True if transition is allowed, False otherwise
    """
    if from_status == to_status:
        return True  # No change is always valid
    
    allowed = STATUS_TRANSITIONS.get(from_status, set())
    return to_status in allowed


def get_allowed_transitions(current_status: BookingStatus) -> Set[BookingStatus]:
    """
    Get all allowed transitions from current status.
    
    Args:
        current_status: Current booking status
        
    Returns:
        Set of allowed status transitions
    """
    return STATUS_TRANSITIONS.get(current_status, set())


