"""
Event Handlers for the Dynamic Pricing Service.

Processes incoming events from other services.
"""
import logging
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.price_decision import PriceDecision, DecisionStatus
from app.services.demand_service import DemandService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class PricingEventHandlers:
    """
    Handlers for pricing-related events from other services.
    """
    
    @staticmethod
    def handle_booking_created(data: Dict[str, Any]):
        """
        Handle booking.created event.
        
        Updates the price decision status to ACCEPTED when
        a booking is successfully created with our quoted price.
        """
        db = SessionLocal()
        try:
            decision_reference = data.get("price_decision_reference")
            booking_id = data.get("booking_id")
            booking_reference = data.get("booking_reference")
            
            if not decision_reference:
                logger.warning("Booking created without price decision reference")
                return
            
            decision = db.query(PriceDecision).filter(
                PriceDecision.decision_reference == decision_reference
            ).first()
            
            if decision:
                decision.status = DecisionStatus.ACCEPTED
                decision.accepted_at = datetime.utcnow()
                decision.booking_id = UUID(booking_id) if booking_id else None
                decision.booking_reference = booking_reference
                db.commit()
                
                # Log audit
                audit = AuditService(db)
                audit.log_price_accepted(decision)
                
                logger.info(
                    f"Price decision {decision_reference} accepted for booking {booking_reference}"
                )
            else:
                logger.warning(f"Price decision {decision_reference} not found")
                
        finally:
            db.close()
    
    @staticmethod
    def handle_booking_cancelled(data: Dict[str, Any]):
        """
        Handle booking.cancelled event.
        
        For analytics purposes - track price decisions
        that were accepted but later cancelled.
        """
        db = SessionLocal()
        try:
            booking_id = data.get("booking_id")
            
            if booking_id:
                decision = db.query(PriceDecision).filter(
                    PriceDecision.booking_id == UUID(booking_id)
                ).first()
                
                if decision:
                    logger.info(
                        f"Booking {booking_id} cancelled for decision {decision.decision_reference}"
                    )
                    # We don't change the decision status - it was accepted
                    # This is useful for analytics on cancellation patterns
                    
        finally:
            db.close()
    
    @staticmethod
    def handle_inventory_availability_changed(data: Dict[str, Any]):
        """
        Handle inventory.availability.changed event.
        
        Updates demand data when inventory availability changes.
        """
        db = SessionLocal()
        try:
            venue_id = data.get("venue_id")
            venue_type = data.get("venue_type")
            availability_data = data.get("availability", {})
            
            if not venue_id:
                return
            
            demand_service = DemandService(db)
            
            # Calculate occupancy rate
            capacity = availability_data.get("total_capacity", 0)
            available = availability_data.get("available", 0)
            
            if capacity > 0:
                occupied = capacity - available
                occupancy_rate = occupied / capacity
                
                # Determine demand level
                if occupancy_rate >= 0.9:
                    demand_level = "peak"
                elif occupancy_rate >= 0.8:
                    demand_level = "high"
                elif occupancy_rate >= 0.5:
                    demand_level = "normal"
                elif occupancy_rate >= 0.3:
                    demand_level = "low"
                else:
                    demand_level = "very_low"
                
                # Update demand data
                demand_service.update_demand_data(
                    venue_id=UUID(venue_id),
                    venue_type=venue_type or "unknown",
                    target_date=datetime.utcnow().date(),
                    hour=datetime.utcnow().hour,
                    data={
                        "capacity": capacity,
                        "occupied": occupied,
                        "occupancy_rate": occupancy_rate,
                        "demand_level": demand_level,
                        "demand_score": occupancy_rate,
                    },
                    source="inventory_event",
                )
                
                logger.info(
                    f"Updated demand data for {venue_id}: {demand_level} ({occupancy_rate:.1%})"
                )
                
        finally:
            db.close()
    
    @staticmethod
    def handle_analytics_demand_forecast(data: Dict[str, Any]):
        """
        Handle analytics.demand.forecast event.
        
        Updates demand forecasts from the Analytics Service.
        """
        db = SessionLocal()
        try:
            venue_id = data.get("venue_id")
            venue_type = data.get("venue_type")
            forecasts = data.get("forecasts", [])
            
            if not venue_id or not forecasts:
                return
            
            demand_service = DemandService(db)
            
            for forecast in forecasts:
                target_date = forecast.get("date")
                if target_date:
                    demand_service.update_demand_data(
                        venue_id=UUID(venue_id),
                        venue_type=venue_type or "unknown",
                        target_date=datetime.fromisoformat(target_date).date(),
                        hour=forecast.get("hour"),
                        data={
                            "forecasted_demand": forecast.get("demand_level"),
                            "forecast_confidence": forecast.get("confidence"),
                            "suggested_multiplier": forecast.get("suggested_multiplier"),
                        },
                        source="analytics_forecast",
                    )
            
            logger.info(f"Updated demand forecasts for {venue_id}")
            
        finally:
            db.close()
    
    @classmethod
    def register_all(cls, consumer):
        """Register all handlers with the consumer."""
        consumer.register_handler("booking.created", cls.handle_booking_created)
        consumer.register_handler("booking.cancelled", cls.handle_booking_cancelled)
        consumer.register_handler(
            "inventory.availability.changed",
            cls.handle_inventory_availability_changed
        )
        consumer.register_handler(
            "analytics.demand.forecast",
            cls.handle_analytics_demand_forecast
        )


