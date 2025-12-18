"""
Utility functions for Booking & Reservation Service.
"""
from app.utils.booking_reference import generate_booking_reference
from app.utils.status_transitions import validate_status_transition, get_allowed_transitions

__all__ = ["generate_booking_reference", "validate_status_transition", "get_allowed_transitions"]


