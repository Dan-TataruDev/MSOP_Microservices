"""
Refund API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.refund import RefundCreate, RefundResponse
from app.services.refund_service import RefundService

router = APIRouter()


@router.post("/refunds", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
def create_refund(
    refund_data: RefundCreate,
    db: Session = Depends(get_db)
):
    """
    Create a refund.
    
    This initiates a refund with the payment provider. The refund
    status will be PENDING initially and will be processed asynchronously.
    """
    try:
        refund_service = RefundService(db)
        refund = refund_service.create_refund(refund_data)
        return RefundResponse.model_validate(refund)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refund creation failed"
        )


@router.get("/refunds/{refund_id}", response_model=RefundResponse)
def get_refund(
    refund_id: UUID,
    db: Session = Depends(get_db)
):
    """Get refund by ID."""
    refund_service = RefundService(db)
    refund = refund_service.get_refund(refund_id)
    
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found"
        )
    
    return RefundResponse.from_orm(refund)


@router.get("/refunds/reference/{refund_reference}", response_model=RefundResponse)
def get_refund_by_reference(
    refund_reference: str,
    db: Session = Depends(get_db)
):
    """Get refund by reference."""
    refund_service = RefundService(db)
    refund = refund_service.get_refund_by_reference(refund_reference)
    
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found"
        )
    
    return RefundResponse.from_orm(refund)


@router.get("/refunds/payment/{payment_id}", response_model=List[RefundResponse])
def get_refunds_by_payment(
    payment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all refunds for a payment."""
    refund_service = RefundService(db)
    refunds = refund_service.get_refunds_by_payment(payment_id)
    return [RefundResponse.model_validate(r) for r in refunds]


@router.post("/refunds/{refund_id}/process", response_model=RefundResponse)
def process_refund(
    refund_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Process a pending refund.
    
    This manually triggers processing of a pending refund.
    In production, refunds are typically processed automatically.
    """
    try:
        refund_service = RefundService(db)
        refund = refund_service.process_refund(refund_id)
        return RefundResponse.model_validate(refund)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refund processing failed"
        )


