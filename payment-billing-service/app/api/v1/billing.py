"""
Billing API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.billing import BillingRecordResponse
from app.services.billing_service import BillingService

router = APIRouter()


@router.get("/billing/booking/{booking_id}", response_model=List[BillingRecordResponse])
def get_billing_records_by_booking(
    booking_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all billing records for a booking."""
    billing_service = BillingService(db)
    records = billing_service.get_billing_records_by_booking(booking_id)
    return [BillingRecordResponse.model_validate(r) for r in records]


@router.get("/billing/guest/{guest_id}", response_model=List[BillingRecordResponse])
def get_billing_records_by_guest(
    guest_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all billing records for a guest."""
    billing_service = BillingService(db)
    records = billing_service.get_billing_records_by_guest(guest_id)
    return [BillingRecordResponse.model_validate(r) for r in records]


