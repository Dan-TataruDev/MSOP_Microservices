"""
Client for coordinating with Payment Service.
This client makes HTTP calls to create payment intents and process payments,
but does not embed payment logic.
"""
import httpx
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from app.config import settings

logger = logging.getLogger(__name__)


class PaymentClient:
    """
    HTTP client for Payment Service coordination.
    
    This service coordinates with payment but does not own payment logic.
    All payment processing is handled by the payment service.
    """
    
    def __init__(self):
        self.base_url = settings.payment_service_url
        self.timeout = settings.external_service_timeout
        self.retry_attempts = settings.external_service_retry_attempts
    
    async def create_payment_intent(
        self,
        booking_id: UUID,
        booking_reference: str,
        amount: Decimal,
        currency: str,
        guest_id: UUID,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent for a booking.
        
        Returns:
            {
                "payment_intent_id": str,
                "client_secret": Optional[str],
                "status": str
            }
        """
        url = f"{self.base_url}/api/v1/payments/intents"
        
        payload = {
            "booking_id": str(booking_id),
            "booking_reference": booking_reference,
            "amount": str(amount),
            "currency": currency,
            "guest_id": str(guest_id),
        }
        
        if payment_method_id:
            payload["payment_method_id"] = payment_method_id
        
        if metadata:
            payload["metadata"] = metadata
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Payment intent creation error: {e}")
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    async def confirm_payment(
        self,
        payment_intent_id: str,
        booking_id: UUID
    ) -> Dict[str, Any]:
        """
        Confirm a payment intent.
        
        Returns:
            {
                "payment_intent_id": str,
                "status": str,
                "transaction_id": Optional[str]
            }
        """
        url = f"{self.base_url}/api/v1/payments/intents/{payment_intent_id}/confirm"
        
        payload = {
            "booking_id": str(booking_id),
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Payment confirmation error: {e}")
            raise Exception(f"Failed to confirm payment: {str(e)}")
    
    async def get_payment_status(
        self,
        payment_intent_id: str
    ) -> Dict[str, Any]:
        """
        Get payment status.
        
        Returns:
            {
                "payment_intent_id": str,
                "status": str,
                "amount": Decimal,
                "currency": str
            }
        """
        url = f"{self.base_url}/api/v1/payments/intents/{payment_intent_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "payment_intent_id": data["payment_intent_id"],
                    "status": data["status"],
                    "amount": Decimal(str(data["amount"])),
                    "currency": data.get("currency", "USD"),
                }
        except httpx.HTTPError as e:
            logger.error(f"Payment status check error: {e}")
            raise Exception(f"Failed to get payment status: {str(e)}")
    
    async def refund_payment(
        self,
        payment_intent_id: str,
        booking_id: UUID,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refund a payment (full or partial).
        
        Returns:
            {
                "refund_id": str,
                "status": str,
                "amount": Decimal
            }
        """
        url = f"{self.base_url}/api/v1/payments/refunds"
        
        payload = {
            "payment_intent_id": payment_intent_id,
            "booking_id": str(booking_id),
        }
        
        if amount:
            payload["amount"] = str(amount)
        
        if reason:
            payload["reason"] = reason
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "refund_id": data["refund_id"],
                    "status": data["status"],
                    "amount": Decimal(str(data["amount"])),
                }
        except httpx.HTTPError as e:
            logger.error(f"Payment refund error: {e}")
            raise Exception(f"Failed to refund payment: {str(e)}")


# Global client instance
payment_client = PaymentClient()


