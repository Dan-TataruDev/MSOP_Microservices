"""
Payment service for handling payment operations.
"""
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.clients.payment_provider import get_payment_provider_client, PaymentProviderClient
from app.config import settings
from app.events.publisher import event_publisher
from app.utils.payment_reference import generate_payment_reference
from app.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Service for managing payment operations.
    
    Handles payment initiation, status tracking, retries, and failure handling.
    Abstracts payment provider details and ensures sensitive data is protected.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.provider_client: PaymentProviderClient = get_payment_provider_client(
            provider=settings.payment_provider,
            api_key=settings.payment_provider_api_key,
            secret_key=settings.payment_provider_secret_key,
        )
    
    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """
        Create a new payment.
        
        This initiates a payment with the payment provider and creates
        a payment record in the database.
        """
        # Check for idempotency
        if payment_data.idempotency_key:
            existing = self.db.query(Payment).filter(
                Payment.idempotency_key == payment_data.idempotency_key
            ).first()
            if existing:
                logger.info(f"Idempotent payment creation: {existing.id}")
                return existing
        
        # Generate payment reference
        payment_reference = generate_payment_reference()
        
        # Create payment record
        payment = Payment(
            payment_reference=payment_reference,
            idempotency_key=payment_data.idempotency_key,
            booking_id=payment_data.booking_id,
            booking_reference=payment_data.booking_reference,
            guest_id=payment_data.booking_id,  # TODO: Get guest_id from booking service via event/API
            amount=Decimal(str(payment_data.amount)),
            currency=payment_data.currency,
            payment_method=payment_data.payment_method,
            status=PaymentStatus.PENDING,
            provider=settings.payment_provider,
            description=payment_data.description,
            metadata=payment_data.metadata or {},
        )
        
        try:
            self.db.add(payment)
            self.db.flush()  # Get payment ID
            
            # Initiate payment with provider (async in production)
            self._initiate_payment_with_provider(payment)
            
            self.db.commit()
            logger.info(f"Payment created: {payment.id} ({payment_reference})")
            
            # Publish event
            event_publisher.publish_payment_initiated(
                payment_id=payment.id,
                payment_data={
                    "payment_reference": payment_reference,
                    "booking_id": str(payment_data.booking_id),
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                }
            )
            
            return payment
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Payment creation failed: {str(e)}")
            raise ValueError("Payment with this reference already exists")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Payment creation failed: {str(e)}", exc_info=True)
            raise
    
    def _initiate_payment_with_provider(self, payment: Payment) -> None:
        """
        Initiate payment with payment provider.
        
        This method handles the actual payment provider API call.
        In production, this would be async.
        """
        try:
            # Convert payment method enum to provider format
            provider_payment_method = payment.payment_method.value
            
            # Create payment intent with provider
            provider_response = self.provider_client.create_payment_intent(
                amount=payment.amount,
                currency=payment.currency,
                payment_method=provider_payment_method,
                metadata={
                    "payment_id": str(payment.id),
                    "booking_id": str(payment.booking_id),
                    **payment.metadata,
                },
                idempotency_key=payment.idempotency_key,
            )
            
            # Store provider response (encrypted in production)
            payment.provider_payment_id = provider_response.get("payment_intent_id")
            payment.provider_response = provider_response  # Store raw response securely
            payment.status = PaymentStatus.PROCESSING
            payment.payment_intent_id = provider_response.get("payment_intent_id")
            
            # Extract safe card information
            if "card_last4" in provider_response:
                payment.card_last4 = provider_response["card_last4"]
            if "card_brand" in provider_response:
                payment.card_brand = provider_response["card_brand"]
            
            logger.info(f"Payment initiated with provider: {payment.provider_payment_id}")
            
        except Exception as e:
            logger.error(f"Provider payment initiation failed: {str(e)}", exc_info=True)
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = str(e)
            payment.failed_at = datetime.utcnow()
            raise
    
    @retry_with_backoff(max_retries=settings.payment_retry_attempts)
    def confirm_payment(self, payment_id: uuid.UUID, confirmation_data: Optional[Dict[str, Any]] = None) -> Payment:
        """
        Confirm a payment.
        
        This is called after the frontend completes payment confirmation
        (e.g., 3D Secure authentication).
        """
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError(f"Payment {payment_id} cannot be confirmed in status {payment.status}")
        
        try:
            # Confirm with provider
            provider_response = self.provider_client.confirm_payment(
                payment_intent_id=payment.provider_payment_id,
                confirmation_data=confirmation_data,
            )
            
            # Update payment status
            if provider_response.get("status") == "succeeded":
                payment.status = PaymentStatus.COMPLETED
                payment.completed_at = datetime.utcnow()
                payment.processed_at = datetime.utcnow()
            else:
                payment.status = PaymentStatus.FAILED
                payment.failure_reason = provider_response.get("failure_reason", "Payment confirmation failed")
                payment.failed_at = datetime.utcnow()
            
            payment.provider_response = provider_response
            self.db.commit()
            
            # Publish event
            if payment.status == PaymentStatus.COMPLETED:
                event_publisher.publish_payment_completed(
                    payment_id=payment.id,
                    payment_data={
                        "payment_reference": payment.payment_reference,
                        "booking_id": str(payment.booking_id),
                        "amount": str(payment.amount),
                    }
                )
            else:
                event_publisher.publish_payment_failed(
                    payment_id=payment.id,
                    payment_data={
                        "payment_reference": payment.payment_reference,
                        "booking_id": str(payment.booking_id),
                        "failure_reason": payment.failure_reason,
                    }
                )
            
            logger.info(f"Payment confirmed: {payment.id} - Status: {payment.status}")
            return payment
            
        except Exception as e:
            self.db.rollback()
            payment.retry_count += 1
            payment.last_retry_at = datetime.utcnow()
            payment.failure_reason = str(e)
            self.db.commit()
            logger.error(f"Payment confirmation failed: {str(e)}", exc_info=True)
            raise
    
    def get_payment(self, payment_id: uuid.UUID) -> Optional[Payment]:
        """Get payment by ID."""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def get_payment_by_reference(self, payment_reference: str) -> Optional[Payment]:
        """Get payment by reference."""
        return self.db.query(Payment).filter(Payment.payment_reference == payment_reference).first()
    
    def get_payment_status(self, payment_reference: str) -> Optional[Payment]:
        """
        Get payment status.
        
        This method can optionally reconcile with the payment provider
        to ensure status is up-to-date.
        """
        payment = self.get_payment_by_reference(payment_reference)
        if not payment:
            return None
        
        # Optionally reconcile with provider
        if payment.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            try:
                provider_status = self.provider_client.get_payment_status(
                    payment_intent_id=payment.provider_payment_id
                )
                
                # Update if status changed
                if provider_status.get("status") == "succeeded" and payment.status != PaymentStatus.COMPLETED:
                    payment.status = PaymentStatus.COMPLETED
                    payment.completed_at = datetime.utcnow()
                    self.db.commit()
                    
                    event_publisher.publish_payment_completed(
                        payment_id=payment.id,
                        payment_data={
                            "payment_reference": payment.payment_reference,
                            "booking_id": str(payment.booking_id),
                        }
                    )
            except Exception as e:
                logger.warning(f"Status reconciliation failed: {str(e)}")
        
        return payment
    
    def update_payment_status_from_webhook(self, payment_id: uuid.UUID, status: PaymentStatus, provider_data: Dict[str, Any]) -> Payment:
        """
        Update payment status from webhook.
        
        This is called when receiving webhook events from the payment provider.
        """
        payment = self.get_payment(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        old_status = payment.status
        payment.status = status
        payment.provider_response = provider_data
        payment.webhook_received_at = datetime.utcnow()
        payment.webhook_processed = True
        
        if status == PaymentStatus.COMPLETED:
            payment.completed_at = datetime.utcnow()
            payment.processed_at = datetime.utcnow()
        elif status == PaymentStatus.FAILED:
            payment.failed_at = datetime.utcnow()
            payment.failure_reason = provider_data.get("failure_reason")
        
        self.db.commit()
        
        # Publish event if status changed
        if old_status != status:
            if status == PaymentStatus.COMPLETED:
                event_publisher.publish_payment_completed(
                    payment_id=payment.id,
                    payment_data={
                        "payment_reference": payment.payment_reference,
                        "booking_id": str(payment.booking_id),
                    }
                )
        
        logger.info(f"Payment status updated from webhook: {payment.id} - {old_status} -> {status}")
        return payment


