"""
Abstract payment provider client interface.

This module provides an abstraction layer over payment providers (Stripe, PayPal, Square, etc.).
The service never exposes raw provider responses to the frontend - only sanitized data.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PaymentProviderClient(ABC):
    """
    Abstract base class for payment provider clients.
    
    All payment providers must implement this interface to ensure
    consistent behavior and abstraction from provider-specific details.
    """
    
    @abstractmethod
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        payment_method: str,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment intent with the provider.
        
        Returns sanitized response with:
        - payment_intent_id: Provider's payment intent ID
        - client_secret: For frontend payment confirmation (if applicable)
        - status: Payment status
        - provider_response: Raw response (encrypted/stored securely, never exposed)
        """
        pass
    
    @abstractmethod
    async def confirm_payment(
        self,
        payment_intent_id: str,
        confirmation_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Confirm a payment intent.
        
        Returns sanitized response with payment status and details.
        """
        pass
    
    @abstractmethod
    async def get_payment_status(
        self,
        payment_intent_id: str,
    ) -> Dict[str, Any]:
        """
        Get current payment status from provider.
        
        Returns sanitized status information.
        """
        pass
    
    @abstractmethod
    async def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a refund.
        
        Returns sanitized response with refund status and details.
        """
        pass
    
    @abstractmethod
    async def get_refund_status(
        self,
        refund_id: str,
    ) -> Dict[str, Any]:
        """
        Get refund status from provider.
        
        Returns sanitized refund status information.
        """
        pass
    
    @abstractmethod
    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify webhook signature from provider.
        
        Returns True if signature is valid.
        """
        pass
    
    @abstractmethod
    def parse_webhook(
        self,
        payload: bytes,
    ) -> Dict[str, Any]:
        """
        Parse webhook payload from provider.
        
        Returns normalized webhook event data.
        """
        pass
    
    def sanitize_response(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize provider response to remove sensitive data.
        
        This method ensures no sensitive information (full card numbers,
        internal provider IDs, etc.) is exposed to the frontend.
        """
        sanitized = {
            "payment_intent_id": raw_response.get("id"),
            "status": raw_response.get("status"),
            "amount": raw_response.get("amount"),
            "currency": raw_response.get("currency"),
            "created_at": raw_response.get("created"),
        }
        
        # Only include safe card information
        if "payment_method" in raw_response:
            pm = raw_response["payment_method"]
            if isinstance(pm, dict):
                sanitized["card_last4"] = pm.get("card", {}).get("last4")
                sanitized["card_brand"] = pm.get("card", {}).get("brand")
        
        return sanitized


class MockPaymentProviderClient(PaymentProviderClient):
    """
    Mock payment provider for development and testing.
    
    Simulates payment provider behavior without actual API calls.
    """
    
    def __init__(self, api_key: str = "", secret_key: str = ""):
        self.api_key = api_key
        self.secret_key = secret_key
        self._payments: Dict[str, Dict[str, Any]] = {}
        self._refunds: Dict[str, Dict[str, Any]] = {}
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        payment_method: str,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mock payment intent creation."""
        import uuid
        payment_id = f"pi_mock_{uuid.uuid4().hex[:24]}"
        
        mock_response = {
            "id": payment_id,
            "status": "requires_payment_method",
            "amount": int(amount * 100),  # Convert to cents
            "currency": currency.lower(),
            "client_secret": f"{payment_id}_secret",
            "payment_method": {
                "card": {
                    "last4": "4242",
                    "brand": "visa",
                }
            },
            "created": 1234567890,
        }
        
        self._payments[payment_id] = {
            "raw": mock_response,
            "status": "pending",
        }
        
        return self.sanitize_response(mock_response)
    
    async def confirm_payment(
        self,
        payment_intent_id: str,
        confirmation_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Mock payment confirmation."""
        if payment_intent_id not in self._payments:
            raise ValueError(f"Payment intent {payment_intent_id} not found")
        
        payment = self._payments[payment_intent_id]
        payment["status"] = "succeeded"
        payment["raw"]["status"] = "succeeded"
        
        return self.sanitize_response(payment["raw"])
    
    async def get_payment_status(
        self,
        payment_intent_id: str,
    ) -> Dict[str, Any]:
        """Mock payment status check."""
        if payment_intent_id not in self._payments:
            raise ValueError(f"Payment intent {payment_intent_id} not found")
        
        return self.sanitize_response(self._payments[payment_intent_id]["raw"])
    
    async def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mock refund creation."""
        import uuid
        refund_id = f"re_mock_{uuid.uuid4().hex[:24]}"
        
        mock_response = {
            "id": refund_id,
            "status": "pending",
            "amount": int((amount or Decimal(0)) * 100),
            "currency": "usd",
            "payment_intent": payment_intent_id,
            "reason": reason,
            "created": 1234567890,
        }
        
        self._refunds[refund_id] = {
            "raw": mock_response,
            "status": "pending",
        }
        
        return {
            "refund_id": refund_id,
            "status": "pending",
            "amount": float(amount or 0),
        }
    
    async def get_refund_status(
        self,
        refund_id: str,
    ) -> Dict[str, Any]:
        """Mock refund status check."""
        if refund_id not in self._refunds:
            raise ValueError(f"Refund {refund_id} not found")
        
        refund = self._refunds[refund_id]
        refund["status"] = "succeeded"
        refund["raw"]["status"] = "succeeded"
        
        return {
            "refund_id": refund_id,
            "status": refund["status"],
        }
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Mock webhook verification (always returns True in mock)."""
        return True
    
    def parse_webhook(self, payload: bytes) -> Dict[str, Any]:
        """Mock webhook parsing."""
        import json
        return json.loads(payload.decode())


def get_payment_provider_client(provider: str, api_key: str, secret_key: str) -> PaymentProviderClient:
    """
    Factory function to get appropriate payment provider client.
    
    In production, this would instantiate real provider clients:
    - StripePaymentProviderClient
    - PayPalPaymentProviderClient
    - SquarePaymentProviderClient
    etc.
    """
    if provider.lower() == "mock" or not api_key:
        logger.info("Using mock payment provider client")
        return MockPaymentProviderClient(api_key, secret_key)
    
    # In production, return actual provider clients
    # For now, return mock
    logger.warning(f"Provider {provider} not fully implemented, using mock")
    return MockPaymentProviderClient(api_key, secret_key)


