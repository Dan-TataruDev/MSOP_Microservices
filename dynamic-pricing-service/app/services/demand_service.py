"""
Demand Service - Manages demand data for pricing decisions.

Collects demand signals from:
- Inventory Service (availability)
- Analytics Service (booking patterns)
- Internal tracking (booking velocity)
- External sources (events, weather)
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session
import httpx

from app.config import settings
from app.models.demand_data import DemandData, DemandLevel

logger = logging.getLogger(__name__)


class DemandService:
    """Service for demand data management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_demand_data(
        self,
        venue_id: UUID,
        venue_type: str,
        target_date: datetime,
    ) -> Dict[str, Any]:
        """
        Get current demand data for pricing decisions.
        
        Aggregates data from multiple sources:
        1. Stored demand data (from analytics)
        2. Real-time inventory data
        3. Historical patterns
        """
        # Try to get stored demand data
        stored_data = self._get_stored_demand(venue_id, target_date)
        
        # Get real-time data from inventory service
        inventory_data = await self._fetch_inventory_data(venue_id, target_date)
        
        # Get historical patterns
        historical_data = self._get_historical_patterns(venue_id, target_date)
        
        # Merge and calculate final demand metrics
        return self._merge_demand_data(
            stored_data, inventory_data, historical_data
        )
    
    def _get_stored_demand(
        self, venue_id: UUID, target_date: datetime
    ) -> Optional[DemandData]:
        """Get stored demand data from database."""
        target_date_only = target_date.date() if isinstance(target_date, datetime) else target_date
        target_hour = target_date.hour if isinstance(target_date, datetime) else None
        
        # Try to get hourly data first
        if target_hour is not None:
            demand = (
                self.db.query(DemandData)
                .filter(
                    DemandData.venue_id == venue_id,
                    DemandData.date == target_date_only,
                    DemandData.hour == target_hour,
                )
                .first()
            )
            if demand:
                return demand
        
        # Fall back to daily aggregate
        return (
            self.db.query(DemandData)
            .filter(
                DemandData.venue_id == venue_id,
                DemandData.date == target_date_only,
                DemandData.hour == None,
            )
            .first()
        )
    
    async def _fetch_inventory_data(
        self, venue_id: UUID, target_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Fetch real-time availability from Inventory Service."""
        try:
            async with httpx.AsyncClient(
                timeout=settings.external_service_timeout
            ) as client:
                response = await client.get(
                    f"{settings.inventory_service_url}/api/v1/availability/{venue_id}",
                    params={
                        "date": target_date.date().isoformat(),
                        "time": target_date.time().isoformat() if hasattr(target_date, 'time') else None,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "capacity": data.get("total_capacity"),
                        "available": data.get("available"),
                        "occupied": data.get("occupied"),
                        "occupancy_rate": data.get("occupancy_rate", 0.5),
                    }
        except Exception as e:
            logger.warning(f"Failed to fetch inventory data: {e}")
        
        return None
    
    def _get_historical_patterns(
        self, venue_id: UUID, target_date: datetime
    ) -> Dict[str, Any]:
        """Get historical demand patterns for similar dates/times."""
        target_day = target_date.weekday()
        target_hour = target_date.hour if hasattr(target_date, 'hour') else 12
        
        # Look at same day of week for past 4 weeks
        historical_data = []
        for weeks_ago in range(1, 5):
            past_date = (target_date - timedelta(weeks=weeks_ago)).date()
            past_demand = (
                self.db.query(DemandData)
                .filter(
                    DemandData.venue_id == venue_id,
                    DemandData.date == past_date,
                )
                .first()
            )
            if past_demand and past_demand.occupancy_rate:
                historical_data.append(float(past_demand.occupancy_rate))
        
        if historical_data:
            avg_occupancy = sum(historical_data) / len(historical_data)
            return {
                "avg_occupancy_same_day": avg_occupancy,
                "data_points": len(historical_data),
            }
        
        return {}
    
    def _merge_demand_data(
        self,
        stored: Optional[DemandData],
        inventory: Optional[Dict[str, Any]],
        historical: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge demand data from multiple sources."""
        result = {
            "demand_level": DemandLevel.NORMAL.value,
            "demand_score": 0.5,
            "occupancy_rate": 0.5,
        }
        
        # Priority: real-time inventory > stored data > historical
        if inventory:
            result["occupancy_rate"] = inventory.get("occupancy_rate", 0.5)
            result["capacity"] = inventory.get("capacity")
            result["available"] = inventory.get("available")
        elif stored:
            result["occupancy_rate"] = float(stored.occupancy_rate) if stored.occupancy_rate else 0.5
            result["capacity"] = stored.capacity
            result["demand_level"] = stored.demand_level.value
            result["demand_score"] = float(stored.demand_score)
        
        # Add historical context
        if historical:
            result["historical_avg"] = historical.get("avg_occupancy_same_day")
            
            # Calculate demand vs historical
            if result.get("historical_avg"):
                current = result["occupancy_rate"]
                historical_avg = result["historical_avg"]
                if historical_avg > 0:
                    result["demand_vs_historical"] = current / historical_avg
        
        # Determine demand level from occupancy
        occupancy = result["occupancy_rate"]
        if occupancy >= 0.9:
            result["demand_level"] = DemandLevel.PEAK.value
            result["demand_score"] = 0.95
        elif occupancy >= settings.high_demand_threshold:
            result["demand_level"] = DemandLevel.HIGH.value
            result["demand_score"] = 0.8
        elif occupancy >= 0.5:
            result["demand_level"] = DemandLevel.NORMAL.value
            result["demand_score"] = 0.5
        elif occupancy >= settings.low_demand_threshold:
            result["demand_level"] = DemandLevel.LOW.value
            result["demand_score"] = 0.3
        else:
            result["demand_level"] = DemandLevel.VERY_LOW.value
            result["demand_score"] = 0.1
        
        return result
    
    def update_demand_data(
        self,
        venue_id: UUID,
        venue_type: str,
        target_date: date,
        hour: Optional[int],
        data: Dict[str, Any],
        source: str = "analytics",
    ) -> DemandData:
        """Update or create demand data entry."""
        existing = (
            self.db.query(DemandData)
            .filter(
                DemandData.venue_id == venue_id,
                DemandData.date == target_date,
                DemandData.hour == hour,
            )
            .first()
        )
        
        if existing:
            # Update existing
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.data_freshness = datetime.utcnow()
            existing.data_source = source
        else:
            # Create new
            existing = DemandData(
                venue_id=venue_id,
                venue_type=venue_type,
                date=target_date,
                hour=hour,
                demand_level=DemandLevel(data.get("demand_level", "normal")),
                demand_score=Decimal(str(data.get("demand_score", 0.5))),
                occupancy_rate=Decimal(str(data.get("occupancy_rate", 0.5))) if data.get("occupancy_rate") else None,
                capacity=data.get("capacity"),
                occupied=data.get("occupied"),
                data_source=source,
                data_freshness=datetime.utcnow(),
            )
            self.db.add(existing)
        
        self.db.commit()
        self.db.refresh(existing)
        
        return existing


