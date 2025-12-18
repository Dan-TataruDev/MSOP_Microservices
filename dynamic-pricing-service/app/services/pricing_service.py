"""
Main Pricing Service - Orchestrates price calculations.

This is the primary service that:
1. Receives pricing requests from Booking Service
2. Coordinates AI and rule engines
3. Handles fallbacks gracefully
4. Creates versioned, auditable price decisions
5. Publishes pricing events
"""
import logging
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.models.price_decision import PriceDecision, DecisionSource, DecisionStatus
from app.models.base_price import BasePrice
from app.engines.ai_engine import ai_pricing_engine, AIPriceResult
from app.engines.rule_engine import RuleEngine
from app.engines.fallback_controller import FallbackController
from app.services.audit_service import AuditService
from app.services.demand_service import DemandService
from app.schemas.pricing import (
    PriceCalculationRequest,
    PriceCalculationResponse,
    PriceBreakdown,
    PriceEstimateRequest,
    PriceEstimateResponse,
)
from app.utils.reference_generator import generate_decision_reference

logger = logging.getLogger(__name__)


class PricingService:
    """
    Main pricing orchestration service.
    
    Coordinates AI pricing, rule-based pricing, and fallback strategies
    to always provide a valid, auditable price.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rule_engine = RuleEngine(db)
        self.fallback_controller = FallbackController(db)
        self.audit_service = AuditService(db)
        self.demand_service = DemandService(db)
    
    async def calculate_price(
        self,
        request: PriceCalculationRequest,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PriceCalculationResponse:
        """
        Calculate a dynamic price for a booking.
        
        This is the main entry point called by the Booking Service.
        Returns a versioned, auditable price decision.
        """
        start_time = time.time()
        
        # Get base price
        base_price_record = self.fallback_controller.get_base_price(
            venue_id=request.venue_id,
            venue_type=request.venue_type,
            product_id=request.product_id,
        )
        
        if base_price_record:
            base_price = base_price_record.base_price
            tax_rate = base_price_record.tax_rate
        else:
            # Use default if no specific base price
            base_price = self.fallback_controller.get_default_base_price(
                request.venue_type
            )
            tax_rate = Decimal(str(settings.default_tax_rate))
            logger.warning(
                f"No base price for venue {request.venue_id}, using default {base_price}"
            )
        
        # Scale base price by party size if applicable
        if request.venue_type in ["restaurant", "cafe"]:
            base_price = base_price * request.party_size
        
        # Get demand data
        demand_data = await self.demand_service.get_demand_data(
            venue_id=request.venue_id,
            venue_type=request.venue_type,
            target_date=request.booking_time,
        )
        
        # Try AI pricing first
        ai_result, ai_success = await self._try_ai_pricing(
            base_price=base_price,
            request=request,
            demand_data=demand_data,
        )
        
        # Determine pricing source and calculate
        if ai_success and ai_result:
            final_price, breakdown, source = self._use_ai_result(
                ai_result, base_price, request
            )
            confidence = ai_result.confidence
            model_version = ai_result.model_version
            ai_input = {"demand": demand_data}
            ai_output = {"result": ai_result.adjustments, "reasoning": ai_result.reasoning}
        else:
            # Fallback
            fallback_result = self.fallback_controller.get_fallback_price(
                base_price=base_price,
                venue_id=request.venue_id,
                venue_type=request.venue_type,
                booking_time=request.booking_time,
                party_size=request.party_size,
                guest_tier=request.guest_tier,
                demand_data=demand_data,
                fallback_reason="ai_unavailable" if not ai_success else "ai_low_confidence",
            )
            final_price = fallback_result.price
            breakdown = fallback_result.breakdown
            source = fallback_result.source
            confidence = fallback_result.confidence
            model_version = None
            ai_input = None
            ai_output = None
        
        # Calculate tax
        tax_amount = (final_price * tax_rate).quantize(Decimal("0.01"))
        total_price = final_price + tax_amount
        
        # Create price decision record
        calculation_time_ms = int((time.time() - start_time) * 1000)
        
        decision = self._create_decision(
            request=request,
            base_price=base_price,
            final_price=final_price,
            tax_amount=tax_amount,
            total_price=total_price,
            source=source,
            confidence=confidence,
            model_version=model_version,
            breakdown=breakdown,
            demand_data=demand_data,
            ai_input=ai_input,
            ai_output=ai_output,
            calculation_time_ms=calculation_time_ms,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        # Audit log
        self.audit_service.log_price_calculated(decision)
        
        # Build response
        return self._build_response(
            decision=decision,
            breakdown=breakdown if request.include_breakdown else None,
        )
    
    async def estimate_price(
        self, request: PriceEstimateRequest
    ) -> PriceEstimateResponse:
        """
        Get a price estimate (non-binding).
        
        Used for availability checks without creating a committed decision.
        """
        # Get base price
        base_price_record = self.fallback_controller.get_base_price(
            venue_id=request.venue_id,
            venue_type=request.venue_type,
        )
        
        if base_price_record:
            base_price = base_price_record.base_price
        else:
            base_price = self.fallback_controller.get_default_base_price(
                request.venue_type
            )
        
        # Scale by party size
        if request.venue_type in ["restaurant", "cafe"]:
            base_price = base_price * request.party_size
        
        # Get demand data
        demand_data = await self.demand_service.get_demand_data(
            venue_id=request.venue_id,
            venue_type=request.venue_type,
            target_date=request.booking_time,
        )
        
        # Quick rule-based estimate
        rule_result = self.rule_engine.evaluate(
            base_price=base_price,
            venue_id=request.venue_id,
            venue_type=request.venue_type,
            booking_time=request.booking_time,
            party_size=request.party_size,
            demand_data=demand_data,
        )
        
        estimated_price = rule_result.adjusted_price
        
        # Calculate price range
        min_price = (base_price * Decimal(str(settings.price_floor_multiplier))).quantize(Decimal("0.01"))
        max_price = (base_price * Decimal(str(settings.price_ceiling_multiplier))).quantize(Decimal("0.01"))
        
        # Determine demand level
        demand_level = "normal"
        is_peak = False
        if demand_data:
            occupancy = demand_data.get("occupancy_rate", 0.5)
            if occupancy >= settings.high_demand_threshold:
                demand_level = "high"
                is_peak = True
            elif occupancy <= settings.low_demand_threshold:
                demand_level = "low"
        
        return PriceEstimateResponse(
            estimated_price=estimated_price,
            currency=settings.default_currency,
            price_range={"min": min_price, "max": max_price},
            demand_level=demand_level,
            is_peak_time=is_peak,
        )
    
    async def _try_ai_pricing(
        self,
        base_price: Decimal,
        request: PriceCalculationRequest,
        demand_data: Optional[Dict[str, Any]],
    ) -> Tuple[Optional[AIPriceResult], bool]:
        """Try to get AI-driven pricing."""
        try:
            return await ai_pricing_engine.calculate_price(
                base_price=base_price,
                venue_id=request.venue_id,
                venue_type=request.venue_type,
                booking_time=request.booking_time,
                party_size=request.party_size,
                demand_data=demand_data,
                guest_context={
                    "guest_id": str(request.guest_id) if request.guest_id else None,
                    "tier": request.guest_tier,
                },
            )
        except Exception as e:
            logger.error(f"AI pricing failed: {e}")
            return None, False
    
    def _use_ai_result(
        self,
        ai_result: AIPriceResult,
        base_price: Decimal,
        request: PriceCalculationRequest,
    ) -> Tuple[Decimal, Dict[str, Any], DecisionSource]:
        """Process AI result and extract pricing info."""
        breakdown = {
            "base_price": float(base_price),
            "ai_suggested_price": float(ai_result.suggested_price),
            "ai_confidence": ai_result.confidence,
            "ai_adjustments": {k: float(v) for k, v in ai_result.adjustments.items()},
            "ai_reasoning": ai_result.reasoning,
        }
        
        return ai_result.suggested_price, breakdown, DecisionSource.AI_MODEL
    
    def _create_decision(
        self,
        request: PriceCalculationRequest,
        base_price: Decimal,
        final_price: Decimal,
        tax_amount: Decimal,
        total_price: Decimal,
        source: DecisionSource,
        confidence: float,
        model_version: Optional[str],
        breakdown: Dict[str, Any],
        demand_data: Optional[Dict[str, Any]],
        ai_input: Optional[Dict[str, Any]],
        ai_output: Optional[Dict[str, Any]],
        calculation_time_ms: int,
        client_ip: Optional[str],
        user_agent: Optional[str],
    ) -> PriceDecision:
        """Create and persist a price decision."""
        # Generate reference
        decision_reference = generate_decision_reference()
        
        # Calculate validity period
        valid_from = datetime.utcnow()
        valid_until = valid_from + timedelta(minutes=request.quote_validity_minutes)
        
        # Extract adjustments from breakdown
        adjustments = breakdown.get("ai_adjustments", {}) or breakdown.get("rule_adjustments", {})
        
        decision = PriceDecision(
            decision_reference=decision_reference,
            version=1,
            venue_id=request.venue_id,
            venue_type=request.venue_type,
            venue_name=request.venue_name,
            booking_date=request.booking_time.date() if hasattr(request.booking_time, 'date') else request.booking_time,
            booking_time=request.booking_time,
            duration_minutes=request.duration_minutes,
            party_size=request.party_size,
            guest_id=request.guest_id,
            guest_tier=request.guest_tier,
            base_price=base_price,
            demand_adjustment=Decimal(str(adjustments.get("demand", 0))),
            seasonal_adjustment=Decimal(str(adjustments.get("seasonal", 0))),
            time_adjustment=Decimal(str(adjustments.get("time", 0))),
            loyalty_adjustment=Decimal(str(adjustments.get("loyalty", 0))),
            promotional_adjustment=Decimal(str(adjustments.get("promotional", 0))),
            ai_adjustment=Decimal(str(adjustments.get("ai", 0))),
            subtotal=final_price,
            tax_amount=tax_amount,
            total_price=total_price,
            currency=settings.default_currency,
            source=source,
            status=DecisionStatus.CALCULATED,
            ai_confidence=Decimal(str(confidence)) if confidence else None,
            model_version=model_version,
            demand_data=demand_data,
            ai_input=ai_input,
            ai_output=ai_output,
            price_breakdown=breakdown,
            valid_from=valid_from,
            valid_until=valid_until,
            calculation_time_ms=calculation_time_ms,
            request_id=request.request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)
        
        return decision
    
    def _build_response(
        self,
        decision: PriceDecision,
        breakdown: Optional[Dict[str, Any]],
    ) -> PriceCalculationResponse:
        """Build API response from decision."""
        price_breakdown = None
        if breakdown:
            price_breakdown = PriceBreakdown(
                base_price=decision.base_price,
                demand_adjustment=decision.demand_adjustment,
                seasonal_adjustment=decision.seasonal_adjustment,
                time_adjustment=decision.time_adjustment,
                loyalty_adjustment=decision.loyalty_adjustment,
                promotional_adjustment=decision.promotional_adjustment,
                ai_adjustment=decision.ai_adjustment,
                subtotal=decision.subtotal,
                tax_amount=decision.tax_amount,
                discount_amount=decision.discount_amount,
                total=decision.total_price,
                applied_rules=breakdown.get("rules_applied"),
            )
        
        return PriceCalculationResponse(
            decision_reference=decision.decision_reference,
            decision_version=decision.version,
            base_price=decision.base_price,
            tax_amount=decision.tax_amount,
            discount_amount=decision.discount_amount,
            total_price=decision.total_price,
            currency=decision.currency,
            breakdown=price_breakdown,
            valid_from=decision.valid_from,
            valid_until=decision.valid_until,
            pricing_source=decision.source.value,
            confidence=float(decision.ai_confidence) if decision.ai_confidence else None,
            venue_id=decision.venue_id,
            venue_type=decision.venue_type,
            booking_time=decision.booking_time,
            party_size=decision.party_size,
        )
    
    def mark_decision_served(self, decision_reference: str) -> bool:
        """Mark a price decision as served to client."""
        decision = self.db.query(PriceDecision).filter(
            PriceDecision.decision_reference == decision_reference
        ).first()
        
        if decision:
            decision.status = DecisionStatus.SERVED
            decision.served_at = datetime.utcnow()
            self.db.commit()
            self.audit_service.log_price_served(decision)
            return True
        return False
    
    def mark_decision_accepted(
        self,
        decision_reference: str,
        booking_id: UUID,
        booking_reference: str,
    ) -> bool:
        """Mark a price decision as accepted (booking created)."""
        decision = self.db.query(PriceDecision).filter(
            PriceDecision.decision_reference == decision_reference
        ).first()
        
        if decision and decision.is_valid():
            decision.status = DecisionStatus.ACCEPTED
            decision.accepted_at = datetime.utcnow()
            decision.booking_id = booking_id
            decision.booking_reference = booking_reference
            self.db.commit()
            self.audit_service.log_price_accepted(decision)
            return True
        return False


