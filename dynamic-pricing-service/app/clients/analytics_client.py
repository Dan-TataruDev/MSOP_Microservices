"""
Client for communicating with Analytics Service.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """HTTP client for Analytics Service coordination."""
    
    def __init__(self):
        self.base_url = settings.analytics_service_url
        self.timeout = settings.external_service_timeout
    
    async def get_demand_insights(
        self,
        venue_id: UUID,
        target_date: date,
    ) -> Optional[Dict[str, Any]]:
        """
        Get demand insights from Analytics Service.
        
        Returns:
            {
                "demand_level": str,
                "demand_score": float,
                "historical_comparison": float,
                "forecast": {...}
            }
        """
        url = f"{self.base_url}/api/v1/insights/demand"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params={
                        "venue_id": str(venue_id),
                        "date": target_date.isoformat(),
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"Analytics service returned {response.status_code}"
                    )
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch demand insights: {e}")
            return None
    
    async def get_pricing_recommendations(
        self,
        venue_id: UUID,
        venue_type: str,
        target_dates: List[date],
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get pricing recommendations from Analytics Service.
        
        Returns list of recommendations per date with suggested
        multipliers based on historical patterns.
        """
        url = f"{self.base_url}/api/v1/insights/pricing-recommendations"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json={
                        "venue_id": str(venue_id),
                        "venue_type": venue_type,
                        "dates": [d.isoformat() for d in target_dates],
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("recommendations", [])
                else:
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch pricing recommendations: {e}")
            return None
    
    async def get_competitor_pricing(
        self,
        venue_type: str,
        location: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get competitor pricing insights (if available).
        
        Returns aggregated competitor pricing data for benchmarking.
        """
        url = f"{self.base_url}/api/v1/insights/competitor-pricing"
        
        params = {"venue_type": venue_type}
        if location:
            params["location"] = location
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch competitor pricing: {e}")
            return None


# Singleton instance
analytics_client = AnalyticsClient()


