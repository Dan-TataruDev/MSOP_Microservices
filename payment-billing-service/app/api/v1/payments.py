"""
Payment API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentStatusResponse
from app.services.payment_service import PaymentService
from app.models.payment import PaymentStatus

router = APIRouter()


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new payment.
    
    This initiates a payment with the payment provider. The payment
    status will be PENDING or PROCESSING initially, and the frontend
    should poll for status or use webhooks.
    """
    try:
        payment_service = PaymentService(db)
        payment = payment_service.create_payment(payment_data)
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment creation failed"
        )


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get payment by ID."""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse.from_orm(payment)


@router.get("/payments/reference/{payment_reference}", response_model=PaymentStatusResponse)
def get_payment_status(
    payment_reference: str,
    db: Session = Depends(get_db)
):
    """
    Get payment status by reference.
    
    This endpoint is safe for frontend polling. It returns only
    sanitized payment information without sensitive data.
    """
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_status(payment_reference)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentStatusResponse.model_validate(payment)


@router.post("/payments/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(
    payment_id: UUID,
    confirmation_data: dict = None,
    db: Session = Depends(get_db)
):
    """
    Confirm a payment.
    
    This is called after the frontend completes payment confirmation
    (e.g., 3D Secure authentication). The confirmation_data can include
    provider-specific confirmation details.
    """
    try:
        payment_service = PaymentService(db)
        payment = payment_service.confirm_payment(payment_id, confirmation_data)
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment confirmation failed"
        )


@router.get("/payments/booking/{booking_id}", response_model=List[PaymentResponse])
def get_payments_by_booking(
    booking_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all payments for a booking."""
    from app.models.payment import Payment
    
    payments = db.query(Payment).filter(
        Payment.booking_id == booking_id
    ).order_by(Payment.created_at.desc()).all()
    
    return [PaymentResponse.model_validate(p) for p in payments]


