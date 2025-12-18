"""
Invoice service for managing invoices.
"""
import logging
from typing import Optional
from datetime import date, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.utils.invoice_number import generate_invoice_number
from app.config import settings

logger = logging.getLogger(__name__)


class InvoiceService:
    """
    Service for managing invoices.
    
    Creates and manages invoices for bookings and payments.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_invoice(self, invoice_data: InvoiceCreate) -> Invoice:
        """Create an invoice."""
        invoice_number = generate_invoice_number()
        due_date = date.today() + timedelta(days=invoice_data.due_days)
        
        invoice = Invoice(
            invoice_number=invoice_number,
            booking_id=invoice_data.booking_id,
            booking_reference=invoice_data.booking_reference,
            payment_id=invoice_data.payment_id,
            guest_id=invoice_data.booking_id,  # TODO: Get from booking service
            amount=invoice_data.amount,
            currency=invoice_data.currency,
            status=InvoiceStatus.DRAFT,
            base_amount=invoice_data.base_amount,
            tax_amount=invoice_data.tax_amount,
            fee_amount=invoice_data.fee_amount,
            discount_amount=invoice_data.discount_amount,
            billing_name=invoice_data.billing_name,
            billing_email=invoice_data.billing_email,
            billing_address=invoice_data.billing_address,
            description=invoice_data.description,
            line_items=[item.dict() for item in invoice_data.line_items] if invoice_data.line_items else None,
            notes=invoice_data.notes,
            terms=invoice_data.terms,
            due_date=due_date,
        )
        
        try:
            self.db.add(invoice)
            self.db.commit()
            logger.info(f"Invoice created: {invoice.id} ({invoice_number})")
            return invoice
        except Exception as e:
            self.db.rollback()
            logger.error(f"Invoice creation failed: {str(e)}", exc_info=True)
            raise
    
    def get_invoice(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get invoice by ID."""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number."""
        return self.db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    
    def get_invoices_by_booking(self, booking_id: UUID) -> list[Invoice]:
        """Get all invoices for a booking."""
        return self.db.query(Invoice).filter(
            Invoice.booking_id == booking_id
        ).order_by(Invoice.created_at.desc()).all()
    
    def update_invoice(self, invoice_id: UUID, invoice_update: InvoiceUpdate) -> Invoice:
        """Update invoice."""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        if invoice_update.status:
            invoice.status = invoice_update.status
            if invoice_update.status == InvoiceStatus.SENT:
                from datetime import datetime
                invoice.sent_at = datetime.utcnow()
        
        if invoice_update.paid_date:
            invoice.paid_date = invoice_update.paid_date
            invoice.status = InvoiceStatus.PAID
        
        try:
            self.db.commit()
            logger.info(f"Invoice updated: {invoice.id}")
            return invoice
        except Exception as e:
            self.db.rollback()
            logger.error(f"Invoice update failed: {str(e)}", exc_info=True)
            raise


