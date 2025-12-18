"""
Invoice API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db)
):
    """Create an invoice."""
    try:
        invoice_service = InvoiceService(db)
        invoice = invoice_service.create_invoice(invoice_data)
        return InvoiceResponse.model_validate(invoice)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invoice creation failed"
        )


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db)
):
    """Get invoice by ID."""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return InvoiceResponse.from_orm(invoice)


@router.get("/invoices/number/{invoice_number}", response_model=InvoiceResponse)
def get_invoice_by_number(
    invoice_number: str,
    db: Session = Depends(get_db)
):
    """Get invoice by invoice number."""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_number(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return InvoiceResponse.from_orm(invoice)


@router.get("/invoices/booking/{booking_id}", response_model=List[InvoiceResponse])
def get_invoices_by_booking(
    booking_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all invoices for a booking."""
    invoice_service = InvoiceService(db)
    invoices = invoice_service.get_invoices_by_booking(booking_id)
    return [InvoiceResponse.model_validate(i) for i in invoices]


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: UUID,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """Update invoice."""
    try:
        invoice_service = InvoiceService(db)
        invoice = invoice_service.update_invoice(invoice_id, invoice_update)
        return InvoiceResponse.model_validate(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invoice update failed"
        )


