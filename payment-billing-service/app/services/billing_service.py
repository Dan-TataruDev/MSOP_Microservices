"""
Billing service for managing billing records.
"""
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.billing import BillingRecord
from app.schemas.billing import BillingRecordCreate
from app.models.payment import Payment

logger = logging.getLogger(__name__)


class BillingService:
    """
    Service for managing billing records.
    
    Creates billing records linked to payments and bookings for audit trail.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_billing_record(self, billing_data: BillingRecordCreate) -> BillingRecord:
        """Create a billing record."""
        billing_record = BillingRecord(
            payment_id=billing_data.payment_id,
            booking_id=billing_data.booking_id,
            booking_reference=billing_data.booking_reference,
            guest_id=billing_data.booking_id,  # TODO: Get from booking service
            amount=billing_data.amount,
            currency=billing_data.currency,
            billing_type=billing_data.billing_type,
            base_amount=billing_data.base_amount,
            tax_amount=billing_data.tax_amount,
            fee_amount=billing_data.fee_amount,
            discount_amount=billing_data.discount_amount,
            description=billing_data.description,
            metadata=billing_data.metadata or {},
        )
        
        try:
            self.db.add(billing_record)
            self.db.commit()
            logger.info(f"Billing record created: {billing_record.id}")
            return billing_record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Billing record creation failed: {str(e)}", exc_info=True)
            raise
    
    def create_billing_record_from_payment(self, payment: Payment) -> BillingRecord:
        """
        Create a billing record from a completed payment.
        
        This is typically called automatically when a payment is completed.
        """
        billing_data = BillingRecordCreate(
            payment_id=payment.id,
            booking_id=payment.booking_id,
            booking_reference=payment.booking_reference,
            amount=float(payment.amount),
            currency=payment.currency,
            billing_type="payment",
            base_amount=float(payment.amount),  # TODO: Get breakdown from booking
            tax_amount=0,  # TODO: Get from booking
            fee_amount=0,
            discount_amount=0,
            description=payment.description or f"Payment for booking {payment.booking_reference}",
        )
        
        return self.create_billing_record(billing_data)
    
    def get_billing_records_by_booking(self, booking_id: UUID) -> list[BillingRecord]:
        """Get all billing records for a booking."""
        return self.db.query(BillingRecord).filter(
            BillingRecord.booking_id == booking_id
        ).order_by(BillingRecord.billed_at.desc()).all()
    
    def get_billing_records_by_guest(self, guest_id: UUID) -> list[BillingRecord]:
        """Get all billing records for a guest."""
        return self.db.query(BillingRecord).filter(
            BillingRecord.guest_id == guest_id
        ).order_by(BillingRecord.billed_at.desc()).all()


