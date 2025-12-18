"""
Client for communicating with Inventory Service.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class InventoryClient:
    """HTTP client for Inventory Service coordination."""
    
    def __init__(self):
        self.base_url = settings.inventory_service_url
        self.timeout = settings.external_service_timeout
    
    async def get_availability(
        self,
        venue_id: UUID,
        target_date: datetime,
    ) -> Optional[Dict[str, Any]]:
        """
        Get availability data from Inventory Service.
        
        Returns:
            {
                "total_capacity": int,
                "available": int,
                "occupied": int,
                "occupancy_rate": float
            }
        """
        url = f"{self.base_url}/api/v1/availability/{venue_id}"
        
        params = {
            "date": target_date.date().isoformat(),
        }
        if hasattr(target_date, 'hour'):
            params["hour"] = target_date.hour
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Venue {venue_id} not found in inventory")
                    return None
                else:
                    logger.error(
                        f"Inventory service error: {response.status_code}"
                    )
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch availability: {e}")
            return None
    
    async def get_venue_details(
        self, venue_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get venue details from Inventory Service."""
        url = f"{self.base_url}/api/v1/venues/{venue_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch venue details: {e}")
            return None


# Singleton instance
inventory_client = InventoryClient()


