"""
Fallback Controller for Dynamic Pricing.

Manages fallback strategies when AI pricing is unavailable:
1. Rule-based pricing (primary fallback)
2. Cached prices (recent AI prices)
3. Base price with simple adjustments (last resort)

Ensures the service NEVER fails to return a price.
"""
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.engines.rule_engine import RuleEngine, RuleEvaluationResult
from app.models.price_decision import PriceDecision, DecisionSource
from app.models.base_price import BasePrice

logger = logging.getLogger(__name__)


@dataclass
class FallbackResult:
    """Result from fallback pricing."""
    price: Decimal
    source: DecisionSource
    confidence: float
    breakdown: Dict[str, Any]
    message: str


class FallbackController:
    """
    Controls fallback pricing strategies.
    
    Ensures pricing service always returns a valid price,
    even when AI or external services are unavailable.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rule_engine = RuleEngine(db)
    
    def get_fallback_price(
        self,
        base_price: Decimal,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        party_size: int,
        guest_tier: Optional[str] = None,
        demand_data: Optional[Dict[str, Any]] = None,
        fallback_reason: str = "ai_unavailable",
    ) -> FallbackResult:
        """
        Get a fallback price using configured strategy.
        
        Fallback order:
        1. Rule-based engine
        2. Cached AI price (if recent enough)
        3. Base price with simple demand adjustment
        
        Args:
            base_price: The base price for the venue
            venue_id: Venue identifier
            venue_type: Type of venue
            booking_time: When the booking is for
            party_size: Number of guests
            guest_tier: Guest loyalty tier
            demand_data: Current demand signals
            fallback_reason: Why fallback was triggered
        
        Returns:
            FallbackResult with price and metadata
        """
        logger.warning(f"Fallback triggered: {fallback_reason}")
        
        strategy = settings.fallback_strategy
        
        if strategy == "rule_based":
            return self._rule_based_fallback(
                base_price, venue_id, venue_type, booking_time,
                party_size, guest_tier, demand_data
            )
        elif strategy == "cached":
            cached = self._try_cached_price(venue_id, booking_time, party_size)
            if cached:
                return cached
            # Fall through to rule-based if no cache
            return self._rule_based_fallback(
                base_price, venue_id, venue_type, booking_time,
                party_size, guest_tier, demand_data
            )
        else:  # "base_price" or default
            return self._base_price_fallback(base_price, demand_data)
    
    def _rule_based_fallback(
        self,
        base_price: Decimal,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        party_size: int,
        guest_tier: Optional[str],
        demand_data: Optional[Dict[str, Any]],
    ) -> FallbackResult:
        """Use rule engine as fallback."""
        try:
            result = self.rule_engine.evaluate(
                base_price=base_price,
                venue_id=venue_id,
                venue_type=venue_type,
                booking_time=booking_time,
                party_size=party_size,
                guest_tier=guest_tier,
                demand_data=demand_data,
            )
            
            return FallbackResult(
                price=result.adjusted_price,
                source=DecisionSource.RULE_ENGINE,
                confidence=0.8,  # Rules are deterministic but less optimal
                breakdown={
                    "base_price": float(base_price),
                    "rule_adjustments": {
                        k: float(v) for k, v in result.adjustments_breakdown.items()
                    },
                    "rules_applied": [
                        {"code": m.rule_code, "effect": float(m.effect)}
                        for m in result.matched_rules
                    ]
                },
                message="Price calculated using rule-based engine (AI fallback)"
            )
            
        except Exception as e:
            logger.error(f"Rule engine fallback failed: {e}")
            return self._base_price_fallback(base_price, demand_data)
    
    def _try_cached_price(
        self,
        venue_id: UUID,
        booking_time: datetime,
        party_size: int,
    ) -> Optional[FallbackResult]:
        """Try to use a cached AI price."""
        try:
            # Look for recent price decisions for similar context
            cache_threshold = datetime.utcnow() - timedelta(
                seconds=settings.fallback_cache_ttl_seconds
            )
            
            # Find similar recent decision
            similar_decision = (
                self.db.query(PriceDecision)
                .filter(PriceDecision.venue_id == venue_id)
                .filter(PriceDecision.source == DecisionSource.AI_MODEL)
                .filter(PriceDecision.created_at >= cache_threshold)
                .filter(PriceDecision.party_size == party_size)
                # Same hour of day for similar demand context
                .filter(
                    self.db.func.extract('hour', PriceDecision.booking_time) == 
                    booking_time.hour
                )
                .order_by(PriceDecision.created_at.desc())
                .first()
            )
            
            if similar_decision:
                logger.info(
                    f"Using cached price from {similar_decision.decision_reference}"
                )
                return FallbackResult(
                    price=similar_decision.total_price,
                    source=DecisionSource.FALLBACK_CACHED,
                    confidence=0.6,  # Lower confidence for cached prices
                    breakdown={
                        "cached_from": similar_decision.decision_reference,
                        "cached_at": similar_decision.created_at.isoformat(),
                        "original_source": similar_decision.source.value,
                    },
                    message="Price from cached AI decision (AI currently unavailable)"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Cache lookup failed: {e}")
            return None
    
    def _base_price_fallback(
        self,
        base_price: Decimal,
        demand_data: Optional[Dict[str, Any]],
    ) -> FallbackResult:
        """
        Last resort fallback using base price with simple adjustments.
        
        Applies basic demand-based adjustment only.
        """
        adjustment = Decimal("1.0")
        adjustment_reason = "standard"
        
        if demand_data:
            occupancy = demand_data.get("occupancy_rate", 0.5)
            
            if occupancy >= settings.high_demand_threshold:
                # High demand - slight increase
                adjustment = Decimal("1.10")
                adjustment_reason = "high_demand"
            elif occupancy <= settings.low_demand_threshold:
                # Low demand - slight discount
                adjustment = Decimal("0.95")
                adjustment_reason = "low_demand"
        
        final_price = (base_price * adjustment).quantize(Decimal("0.01"))
        
        return FallbackResult(
            price=final_price,
            source=DecisionSource.FALLBACK_BASE,
            confidence=0.5,  # Lowest confidence for basic fallback
            breakdown={
                "base_price": float(base_price),
                "adjustment_multiplier": float(adjustment),
                "adjustment_reason": adjustment_reason,
            },
            message="Base price with demand adjustment (fallback mode)"
        )
    
    def get_base_price(
        self,
        venue_id: UUID,
        venue_type: str,
        product_id: Optional[UUID] = None,
    ) -> Optional[BasePrice]:
        """Retrieve base price for a venue/product."""
        query = (
            self.db.query(BasePrice)
            .filter(BasePrice.venue_id == venue_id)
            .filter(BasePrice.is_active == True)
        )
        
        if product_id:
            query = query.filter(BasePrice.product_id == product_id)
        
        # Check validity
        now = datetime.utcnow()
        query = query.filter(
            (BasePrice.valid_until == None) | (BasePrice.valid_until >= now)
        )
        
        return query.first()
    
    def get_default_base_price(self, venue_type: str) -> Decimal:
        """Get default base price for a venue type when no specific price exists."""
        defaults = {
            "hotel": Decimal("150.00"),
            "restaurant": Decimal("50.00"),
            "cafe": Decimal("15.00"),
            "retail": Decimal("25.00"),
            "spa": Decimal("100.00"),
            "event_space": Decimal("500.00"),
        }
        return defaults.get(venue_type.lower(), Decimal("50.00"))


