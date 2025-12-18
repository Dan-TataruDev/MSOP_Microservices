"""
Client for coordinating with Pricing Service.
This client makes HTTP calls to get pricing information,
but does not embed pricing logic.
"""
import httpx
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.config import settings

logger = logging.getLogger(__name__)


class PricingClient:
    """
    HTTP client for Pricing Service coordination.
    
    This service coordinates with pricing but does not own pricing logic.
    All pricing calculations are made by the pricing service.
    """
    
    def __init__(self):
        self.base_url = settings.pricing_service_url
        self.timeout = settings.external_service_timeout
        self.retry_attempts = settings.external_service_retry_attempts
    
    async def get_booking_price(
        self,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        duration_minutes: Optional[int],
        party_size: int,
        guest_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get pricing for a booking.
        
        Returns:
            {
                "base_price": Decimal,
                "tax_amount": Decimal,
                "discount_amount": Decimal,
                "total_price": Decimal,
                "currency": str,
                "breakdown": Optional[Dict]
            }
        """
        url = f"{self.base_url}/api/v1/pricing/calculate"
        
        payload = {
            "venue_id": str(venue_id),
            "venue_type": venue_type,
            "booking_time": booking_time.isoformat(),
            "party_size": party_size,
        }
        
        if duration_minutes:
            payload["duration_minutes"] = duration_minutes
        
        if guest_id:
            payload["guest_id"] = str(guest_id)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Convert string decimals to Decimal
                return {
                    "base_price": Decimal(str(data["base_price"])),
                    "tax_amount": Decimal(str(data.get("tax_amount", 0))),
                    "discount_amount": Decimal(str(data.get("discount_amount", 0))),
                    "total_price": Decimal(str(data["total_price"])),
                    "currency": data.get("currency", "USD"),
                    "breakdown": data.get("breakdown"),
                }
        except httpx.HTTPError as e:
            logger.error(f"Pricing service error: {e}")
            # Return default pricing on service error (fail-safe)
            # In production, this might be a fallback pricing strategy
            return {
                "base_price": Decimal("0.00"),
                "tax_amount": Decimal("0.00"),
                "discount_amount": Decimal("0.00"),
                "total_price": Decimal("0.00"),
                "currency": "USD",
                "breakdown": None,
            }
    
    async def estimate_price(
        self,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        party_size: int,
        duration_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get price estimate (for availability checks, no commitment).
        
        Returns:
            {
                "estimated_price": Decimal,
                "currency": str,
                "price_range": Optional[Dict]
            }
        """
        url = f"{self.base_url}/api/v1/pricing/estimate"
        
        payload = {
            "venue_id": str(venue_id),
            "venue_type": venue_type,
            "booking_time": booking_time.isoformat(),
            "party_size": party_size,
        }
        
        if duration_minutes:
            payload["duration_minutes"] = duration_minutes
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "estimated_price": Decimal(str(data.get("estimated_price", 0))),
                    "currency": data.get("currency", "USD"),
                    "price_range": data.get("price_range"),
                }
        except httpx.HTTPError as e:
            logger.error(f"Pricing estimate error: {e}")
            return {
                "estimated_price": Decimal("0.00"),
                "currency": "USD",
                "price_range": None,
            }


# Global client instance
pricing_client = PricingClient()


