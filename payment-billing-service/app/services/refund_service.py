"""
Refund service for managing refunds.
"""
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.refund import Refund, RefundStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.refund import RefundCreate, RefundUpdate
from app.clients.payment_provider import PaymentProviderClient
from app.config import settings
from app.events.publisher import event_publisher
from app.utils.refund_reference import generate_refund_reference
from app.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class RefundService:
    """
    Service for managing refund operations.
    
    Handles refund creation, processing, and status tracking.
    """
    
    def __init__(self, db: Session):
        self.db = db
        from app.clients.payment_provider import get_payment_provider_client
        self.provider_client: PaymentProviderClient = get_payment_provider_client(
            provider=settings.payment_provider,
            api_key=settings.payment_provider_api_key,
            secret_key=settings.payment_provider_secret_key,
        )
    
    def create_refund(self, refund_data: RefundCreate) -> Refund:
        """
        Create a refund.
        
        This initiates a refund with the payment provider.
        """
        # Check for idempotency
        if refund_data.idempotency_key:
            existing = self.db.query(Refund).filter(
                Refund.idempotency_key == refund_data.idempotency_key
            ).first()
            if existing:
                logger.info(f"Idempotent refund creation: {existing.id}")
                return existing
        
        # Get payment
        payment = self.db.query(Payment).filter(Payment.id == refund_data.payment_id).first()
        if not payment:
            raise ValueError(f"Payment {refund_data.payment_id} not found")
        
        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError(f"Cannot refund payment in status {payment.status}")
        
        # Determine refund amount
        refund_amount = Decimal(str(refund_data.amount)) if refund_data.amount else payment.amount
        
        # Check if refund amount is valid
        if refund_amount > payment.amount:
            raise ValueError("Refund amount cannot exceed payment amount")
        
        # Generate refund reference
        refund_reference = generate_refund_reference()
        
        # Create refund record
        refund = Refund(
            refund_reference=refund_reference,
            idempotency_key=refund_data.idempotency_key,
            payment_id=refund_data.payment_id,
            booking_id=refund_data.booking_id,
            booking_reference=refund_data.booking_reference,
            guest_id=payment.guest_id,
            amount=refund_amount,
            currency=payment.currency,
            status=RefundStatus.PENDING,
            reason=refund_data.reason,
            refund_type=refund_data.refund_type,
            provider=payment.provider,
        )
        
        try:
            self.db.add(refund)
            self.db.flush()
            
            # Process refund with provider
            self._process_refund_with_provider(refund, payment)
            
            self.db.commit()
            logger.info(f"Refund created: {refund.id} ({refund_reference})")
            
            # Publish event
            event_publisher.publish_refund_initiated(
                refund_id=refund.id,
                refund_data={
                    "refund_reference": refund_reference,
                    "payment_id": str(refund_data.payment_id),
                    "booking_id": str(refund_data.booking_id),
                    "amount": str(refund.amount),
                }
            )
            
            return refund
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Refund creation failed: {str(e)}", exc_info=True)
            raise
    
    def _process_refund_with_provider(self, refund: Refund, payment: Payment) -> None:
        """Process refund with payment provider."""
        try:
            provider_response = self.provider_client.create_refund(
                payment_intent_id=payment.provider_payment_id,
                amount=refund.amount,
                reason=refund.reason,
                idempotency_key=refund.idempotency_key,
            )
            
            refund.provider_refund_id = provider_response.get("refund_id")
            refund.provider_response = provider_response
            refund.status = RefundStatus.PROCESSING
            
            logger.info(f"Refund initiated with provider: {refund.provider_refund_id}")
            
        except Exception as e:
            logger.error(f"Provider refund initiation failed: {str(e)}", exc_info=True)
            refund.status = RefundStatus.FAILED
            refund.failure_reason = str(e)
            refund.failed_at = datetime.utcnow()
            raise
    
    @retry_with_backoff(max_retries=settings.refund_retry_attempts)
    def process_refund(self, refund_id: uuid.UUID) -> Refund:
        """Process a pending refund."""
        refund = self.db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise ValueError(f"Refund {refund_id} not found")
        
        if refund.status != RefundStatus.PENDING:
            raise ValueError(f"Refund {refund_id} cannot be processed in status {refund.status}")
        
        payment = refund.payment
        
        try:
            # Check status with provider
            provider_status = self.provider_client.get_refund_status(
                refund_id=refund.provider_refund_id
            )
            
            if provider_status.get("status") == "succeeded":
                refund.status = RefundStatus.COMPLETED
                refund.completed_at = datetime.utcnow()
                refund.processed_at = datetime.utcnow()
                
                # Update payment status
                if refund.amount == payment.amount:
                    payment.status = PaymentStatus.REFUNDED
                else:
                    payment.status = PaymentStatus.PARTIALLY_REFUNDED
                
                self.db.commit()
                
                # Publish event
                event_publisher.publish_refund_completed(
                    refund_id=refund.id,
                    refund_data={
                        "refund_reference": refund.refund_reference,
                        "payment_id": str(refund.payment_id),
                        "booking_id": str(refund.booking_id),
                    }
                )
                
                logger.info(f"Refund processed: {refund.id}")
            else:
                refund.status = RefundStatus.FAILED
                refund.failure_reason = "Refund processing failed"
                refund.failed_at = datetime.utcnow()
                self.db.commit()
            
            return refund
            
        except Exception as e:
            self.db.rollback()
            refund.retry_count += 1
            refund.last_retry_at = datetime.utcnow()
            refund.failure_reason = str(e)
            self.db.commit()
            logger.error(f"Refund processing failed: {str(e)}", exc_info=True)
            raise
    
    def get_refund(self, refund_id: uuid.UUID) -> Optional[Refund]:
        """Get refund by ID."""
        return self.db.query(Refund).filter(Refund.id == refund_id).first()
    
    def get_refund_by_reference(self, refund_reference: str) -> Optional[Refund]:
        """Get refund by reference."""
        return self.db.query(Refund).filter(Refund.refund_reference == refund_reference).first()
    
    def get_refunds_by_payment(self, payment_id: uuid.UUID) -> list[Refund]:
        """Get all refunds for a payment."""
        return self.db.query(Refund).filter(
            Refund.payment_id == payment_id
        ).order_by(Refund.created_at.desc()).all()


