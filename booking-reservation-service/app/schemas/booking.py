"""
Pydantic schemas for booking API.
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.booking import VenueType, BookingStatus


class BookingCreate(BaseModel):
    """Schema for creating a new booking."""
    guest_id: UUID = Field(..., description="Guest ID")
    guest_name: str = Field(..., min_length=1, max_length=255)
    guest_email: EmailStr
    guest_phone: Optional[str] = Field(None, max_length=50)
    
    venue_id: UUID = Field(..., description="Venue ID")
    venue_type: VenueType
    venue_name: str = Field(..., min_length=1, max_length=255)
    
    booking_date: datetime = Field(..., description="Date of booking")
    booking_time: datetime = Field(..., description="Start time of booking")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duration in minutes")
    party_size: int = Field(..., ge=1, le=100, description="Number of guests")
    
    special_requests: Optional[str] = None
    source: Optional[str] = Field(None, max_length=50)
    
    # Idempotency
    idempotency_key: Optional[str] = Field(None, max_length=255, description="Idempotency key for duplicate prevention")
    
    # Metadata
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "guest_id": "123e4567-e89b-12d3-a456-426614174000",
                "guest_name": "John Doe",
                "guest_email": "john@example.com",
                "guest_phone": "+1234567890",
                "venue_id": "223e4567-e89b-12d3-a456-426614174000",
                "venue_type": "restaurant",
                "venue_name": "Fine Dining Restaurant",
                "booking_date": "2024-12-25T00:00:00Z",
                "booking_time": "2024-12-25T19:00:00Z",
                "duration_minutes": 120,
                "party_size": 4,
                "special_requests": "Window seat preferred",
                "source": "web"
            }
        }


class BookingUpdate(BaseModel):
    """Schema for updating a booking."""
    booking_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1)
    party_size: Optional[int] = Field(None, ge=1, le=100)
    special_requests: Optional[str] = None
    
    # Idempotency
    idempotency_key: Optional[str] = Field(None, max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "booking_time": "2024-12-25T20:00:00Z",
                "party_size": 5,
                "special_requests": "Updated request"
            }
        }


class BookingStatusUpdate(BaseModel):
    """Schema for updating booking status."""
    status: BookingStatus
    reason: Optional[str] = Field(None, max_length=255)
    changed_by: Optional[str] = Field(None, max_length=50)


class BookingCancelRequest(BaseModel):
    """Schema for cancelling a booking."""
    reason: Optional[str] = Field(None, max_length=255)
    cancelled_by: str = Field(..., max_length=50)  # guest, business, system
    idempotency_key: Optional[str] = Field(None, max_length=255)


class BookingResponse(BaseModel):
    """Schema for booking response."""
    id: UUID
    booking_reference: str
    guest_id: UUID
    guest_name: str
    guest_email: str
    guest_phone: Optional[str]
    
    venue_id: UUID
    venue_type: VenueType
    venue_name: str
    
    booking_date: datetime
    booking_time: datetime
    duration_minutes: Optional[int]
    end_time: Optional[datetime]
    party_size: int
    
    status: BookingStatus
    version: int
    
    base_price: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_price: Decimal
    currency: str
    
    payment_status: Optional[str]
    payment_intent_id: Optional[str]
    
    inventory_reservation_id: Optional[str]
    
    special_requests: Optional[str]
    internal_notes: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    checked_in_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    cancellation_reason: Optional[str]
    cancelled_by: Optional[str]
    
    source: Optional[str]
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for paginated booking list response."""
    bookings: List[BookingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AvailabilityCheckRequest(BaseModel):
    """Schema for checking availability."""
    venue_id: UUID
    venue_type: VenueType
    booking_date: datetime
    booking_time: datetime
    duration_minutes: Optional[int] = None
    party_size: int = Field(..., ge=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "venue_id": "223e4567-e89b-12d3-a456-426614174000",
                "venue_type": "restaurant",
                "booking_date": "2024-12-25T00:00:00Z",
                "booking_time": "2024-12-25T19:00:00Z",
                "duration_minutes": 120,
                "party_size": 4
            }
        }


class AvailabilityCheckResponse(BaseModel):
    """Schema for availability check response."""
    available: bool
    venue_id: UUID
    booking_date: datetime
    booking_time: datetime
    party_size: int
    
    # Available time slots (if checking multiple slots)
    available_slots: Optional[List[datetime]] = None
    
    # Reason if not available
    reason: Optional[str] = None
    
    # Estimated pricing (from pricing service)
    estimated_price: Optional[Decimal] = None
    currency: str = "USD"
    
    # Inventory availability (from inventory service)
    inventory_available: Optional[bool] = None


