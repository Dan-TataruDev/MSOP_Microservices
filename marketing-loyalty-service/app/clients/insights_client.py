"""
Client for consuming insights from external services.

This service CONSUMES insights but does NOT generate them.
Insights come from:
- Personalization Service: Guest segments, preferences
- Sentiment Service: Feedback scores, satisfaction levels
- Analytics Service: Behavior patterns, trends
"""
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class InsightsClient:
    """
    Client for fetching insights from external services.
    
    Used for eligibility decisions and offer targeting.
    Gracefully degrades if services are unavailable.
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(5.0)
    
    async def get_guest_segments(self, guest_id: UUID) -> List[str]:
        """
        Fetch guest segments from personalization service.
        
        Returns: List of segment identifiers (e.g., ["frequent_guest", "business_traveler"])
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.personalization_service_url}/api/v1/guests/{guest_id}/segments"
                )
                if response.status_code == 200:
                    return response.json().get("segments", [])
        except Exception as e:
            logger.warning(f"Failed to fetch guest segments: {e}")
        return []
    
    async def get_guest_sentiment(self, guest_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Fetch guest sentiment summary from sentiment service.
        
        Returns: {"average_score": 0.8, "recent_feedback": "positive", ...}
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.sentiment_service_url}/api/v1/insights/guest/{guest_id}"
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch guest sentiment: {e}")
        return None
    
    async def get_guest_insights(self, guest_id: UUID) -> Dict[str, Any]:
        """
        Aggregate all available insights for a guest.
        
        Used for eligibility evaluation and offer personalization.
        """
        segments = await self.get_guest_segments(guest_id)
        sentiment = await self.get_guest_sentiment(guest_id)
        
        return {
            "segments": segments,
            "sentiment": sentiment,
            "sentiment_score": sentiment.get("average_score") if sentiment else None,
        }


# Singleton instance
insights_client = InsightsClient()


