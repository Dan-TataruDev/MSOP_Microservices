"""
Client for coordinating with Inventory Service.
This client makes HTTP calls to check and reserve inventory,
but does not embed inventory logic.
"""
import httpx
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class InventoryClient:
    """
    HTTP client for Inventory Service coordination.
    
    This service coordinates with inventory but does not own inventory logic.
    All inventory decisions are made by the inventory service.
    """
    
    def __init__(self):
        self.base_url = settings.inventory_service_url
        self.timeout = settings.external_service_timeout
        self.retry_attempts = settings.external_service_retry_attempts
    
    async def check_availability(
        self,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        duration_minutes: Optional[int],
        party_size: int,
        booking_date: datetime
    ) -> Dict[str, Any]:
        """
        Check if inventory is available for a booking.
        
        Returns:
            {
                "available": bool,
                "inventory_item_id": Optional[str],
                "reason": Optional[str]
            }
        """
        url = f"{self.base_url}/api/v1/inventory/check-availability"
        
        payload = {
            "venue_id": str(venue_id),
            "venue_type": venue_type,
            "booking_time": booking_time.isoformat(),
            "booking_date": booking_date.isoformat(),
            "party_size": party_size,
        }
        
        if duration_minutes:
            payload["duration_minutes"] = duration_minutes
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Inventory service error: {e}")
            # Return unavailable on service error (fail-safe)
            return {
                "available": False,
                "inventory_item_id": None,
                "reason": f"Inventory service unavailable: {str(e)}"
            }
    
    async def reserve_inventory(
        self,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        duration_minutes: Optional[int],
        party_size: int,
        booking_reference: str,
        booking_id: UUID
    ) -> Dict[str, Any]:
        """
        Reserve inventory for a booking.
        
        Returns:
            {
                "reservation_id": str,
                "inventory_item_id": str,
                "expires_at": Optional[datetime]
            }
        """
        url = f"{self.base_url}/api/v1/inventory/reserve"
        
        payload = {
            "venue_id": str(venue_id),
            "venue_type": venue_type,
            "booking_time": booking_time.isoformat(),
            "party_size": party_size,
            "booking_reference": booking_reference,
            "booking_id": str(booking_id),
        }
        
        if duration_minutes:
            payload["duration_minutes"] = duration_minutes
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Inventory reservation error: {e}")
            raise Exception(f"Failed to reserve inventory: {str(e)}")
    
    async def release_inventory(
        self,
        reservation_id: str,
        booking_reference: str
    ) -> bool:
        """
        Release inventory reservation.
        
        Returns:
            bool: True if released successfully
        """
        url = f"{self.base_url}/api/v1/inventory/release"
        
        payload = {
            "reservation_id": reservation_id,
            "booking_reference": booking_reference,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            logger.error(f"Inventory release error: {e}")
            # Log but don't fail - inventory service should handle cleanup
            return False
    
    async def update_inventory_reservation(
        self,
        reservation_id: str,
        booking_time: datetime,
        duration_minutes: Optional[int],
        party_size: int
    ) -> Dict[str, Any]:
        """
        Update an existing inventory reservation.
        
        Returns:
            {
                "reservation_id": str,
                "updated": bool
            }
        """
        url = f"{self.base_url}/api/v1/inventory/update-reservation"
        
        payload = {
            "reservation_id": reservation_id,
            "booking_time": booking_time.isoformat(),
            "party_size": party_size,
        }
        
        if duration_minutes:
            payload["duration_minutes"] = duration_minutes
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Inventory update error: {e}")
            raise Exception(f"Failed to update inventory reservation: {str(e)}")


# Global client instance
inventory_client = InventoryClient()


