"""
Rule-Based Pricing Engine.

This engine evaluates pricing rules against booking context
to calculate price adjustments. Used as:
1. Primary pricing method when AI is not needed
2. Fallback when AI is unavailable
3. Hybrid mode (rules + AI adjustments)
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.pricing_rule import (
    PricingRule, RuleType, RuleStatus, RuleAction, RuleCondition
)
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RuleMatch:
    """Represents a matched pricing rule."""
    rule_id: UUID
    rule_code: str
    rule_type: RuleType
    action_type: RuleAction
    action_value: Decimal
    priority: int
    effect: Decimal  # Calculated effect on price


@dataclass
class RuleEvaluationResult:
    """Result from rule engine evaluation."""
    base_price: Decimal
    adjusted_price: Decimal
    matched_rules: List[RuleMatch] = field(default_factory=list)
    adjustments_breakdown: Dict[str, Decimal] = field(default_factory=dict)
    evaluation_time_ms: int = 0


class RuleEngine:
    """
    Rule-based pricing engine.
    
    Evaluates pricing rules against booking context
    and calculates the final adjusted price.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate(
        self,
        base_price: Decimal,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        party_size: int,
        guest_tier: Optional[str] = None,
        demand_data: Optional[Dict[str, Any]] = None,
    ) -> RuleEvaluationResult:
        """
        Evaluate all applicable rules and calculate adjusted price.
        
        Args:
            base_price: Starting price
            venue_id: Venue identifier
            venue_type: Type of venue
            booking_time: Booking date and time
            party_size: Number of guests
            guest_tier: Guest loyalty tier
            demand_data: Current demand signals
        
        Returns:
            RuleEvaluationResult with adjusted price and applied rules
        """
        import time
        start_time = time.time()
        
        # Build evaluation context
        context = self._build_context(
            venue_id=venue_id,
            venue_type=venue_type,
            booking_time=booking_time,
            party_size=party_size,
            guest_tier=guest_tier,
            demand_data=demand_data,
        )
        
        # Get active rules sorted by priority
        rules = self._get_applicable_rules(venue_id, venue_type)
        
        # Evaluate each rule
        matched_rules = []
        exclusive_groups_applied = set()
        
        for rule in rules:
            # Skip if exclusive group already applied
            if rule.exclusive_group and rule.exclusive_group in exclusive_groups_applied:
                continue
            
            # Evaluate rule conditions
            if self._evaluate_conditions(rule, context):
                match = self._create_rule_match(rule, base_price, context)
                matched_rules.append(match)
                
                # Track exclusive groups
                if rule.exclusive_group:
                    exclusive_groups_applied.add(rule.exclusive_group)
                
                # Check stacking
                if not rule.is_stackable:
                    break  # Stop if non-stackable rule matches
        
        # Calculate final price
        adjusted_price, breakdown = self._calculate_final_price(
            base_price, matched_rules
        )
        
        # Apply price boundaries
        adjusted_price = self._apply_boundaries(adjusted_price, base_price)
        
        evaluation_time = int((time.time() - start_time) * 1000)
        
        return RuleEvaluationResult(
            base_price=base_price,
            adjusted_price=adjusted_price,
            matched_rules=matched_rules,
            adjustments_breakdown=breakdown,
            evaluation_time_ms=evaluation_time,
        )
    
    def _build_context(
        self,
        venue_id: UUID,
        venue_type: str,
        booking_time: datetime,
        party_size: int,
        guest_tier: Optional[str],
        demand_data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build context dictionary for rule evaluation."""
        return {
            "venue_id": str(venue_id),
            "venue_type": venue_type,
            "booking_date": booking_time.date(),
            "booking_time": booking_time.time(),
            "booking_datetime": booking_time,
            "day_of_week": booking_time.weekday(),  # 0=Monday
            "hour": booking_time.hour,
            "party_size": party_size,
            "guest_tier": guest_tier,
            "demand": demand_data or {},
            "occupancy_rate": demand_data.get("occupancy_rate", 0.5) if demand_data else 0.5,
            "is_weekend": booking_time.weekday() >= 5,
            "is_holiday": self._check_holiday(booking_time.date()),
        }
    
    def _get_applicable_rules(
        self, venue_id: UUID, venue_type: str
    ) -> List[PricingRule]:
        """Get all applicable active rules sorted by priority."""
        now = datetime.utcnow()
        
        # Query active rules
        rules = (
            self.db.query(PricingRule)
            .filter(PricingRule.status == RuleStatus.ACTIVE)
            .filter(PricingRule.is_deleted == False)
            .filter(
                (PricingRule.valid_from == None) | (PricingRule.valid_from <= now)
            )
            .filter(
                (PricingRule.valid_until == None) | (PricingRule.valid_until >= now)
            )
            .order_by(PricingRule.priority.asc())
            .all()
        )
        
        # Filter by venue applicability
        applicable = []
        for rule in rules:
            # Check venue type applicability
            if rule.venue_types:
                if venue_type not in rule.venue_types:
                    continue
            
            # Check venue ID applicability
            if rule.venue_ids:
                if str(venue_id) not in [str(v) for v in rule.venue_ids]:
                    continue
            
            applicable.append(rule)
        
        return applicable
    
    def _evaluate_conditions(
        self, rule: PricingRule, context: Dict[str, Any]
    ) -> bool:
        """Evaluate all conditions of a rule against context."""
        if not rule.conditions:
            return True  # No conditions means always matches
        
        for condition in rule.conditions:
            if not self._evaluate_single_condition(condition, context):
                return False
        
        # Check time restrictions
        if rule.time_restrictions:
            if not self._check_time_restrictions(rule.time_restrictions, context):
                return False
        
        return True
    
    def _evaluate_single_condition(
        self, condition: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Evaluate a single condition against context."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        values = condition.get("values", [])
        
        # Get context value
        context_value = context.get(field)
        if context_value is None:
            return False
        
        # Evaluate based on operator
        try:
            if operator == "equals":
                return context_value == value
            elif operator == "not_equals":
                return context_value != value
            elif operator == "greater_than":
                return context_value > value
            elif operator == "less_than":
                return context_value < value
            elif operator == "between":
                return values[0] <= context_value <= values[1]
            elif operator == "in":
                return context_value in values
            elif operator == "not_in":
                return context_value not in values
            elif operator == "contains":
                return value in str(context_value)
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    def _check_time_restrictions(
        self, restrictions: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Check if current time matches restrictions."""
        # Check day of week
        if "days" in restrictions:
            if context["day_of_week"] not in restrictions["days"]:
                return False
        
        # Check hours
        if "hours" in restrictions:
            hour = context["hour"]
            start_hour = restrictions["hours"].get("start", 0)
            end_hour = restrictions["hours"].get("end", 24)
            if not (start_hour <= hour < end_hour):
                return False
        
        return True
    
    def _check_holiday(self, check_date: date) -> Optional[str]:
        """Check if date is a known holiday."""
        # Simple holiday check - in production, use a proper holiday library
        holidays = {
            (12, 25): "Christmas",
            (12, 31): "New Year's Eve",
            (1, 1): "New Year's Day",
            (7, 4): "Independence Day",
            (11, 25): "Thanksgiving",  # Simplified
        }
        return holidays.get((check_date.month, check_date.day))
    
    def _create_rule_match(
        self, rule: PricingRule, base_price: Decimal, context: Dict[str, Any]
    ) -> RuleMatch:
        """Create a RuleMatch object from a matched rule."""
        effect = self._calculate_rule_effect(rule, base_price)
        
        return RuleMatch(
            rule_id=rule.id,
            rule_code=rule.rule_code,
            rule_type=rule.rule_type,
            action_type=rule.action_type,
            action_value=rule.action_value,
            priority=rule.priority,
            effect=effect,
        )
    
    def _calculate_rule_effect(
        self, rule: PricingRule, base_price: Decimal
    ) -> Decimal:
        """Calculate the monetary effect of a rule."""
        value = rule.action_value
        
        if rule.action_type == RuleAction.MULTIPLY:
            return base_price * (value - Decimal("1"))
        elif rule.action_type == RuleAction.ADD:
            return value
        elif rule.action_type == RuleAction.SUBTRACT:
            return -value
        elif rule.action_type == RuleAction.SET:
            return value - base_price
        elif rule.action_type == RuleAction.PERCENTAGE_INCREASE:
            return base_price * (value / Decimal("100"))
        elif rule.action_type == RuleAction.PERCENTAGE_DECREASE:
            return -base_price * (value / Decimal("100"))
        else:
            return Decimal("0")
    
    def _calculate_final_price(
        self, base_price: Decimal, matched_rules: List[RuleMatch]
    ) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Calculate final price from all matched rules."""
        breakdown = {}
        total_adjustment = Decimal("0")
        
        for match in matched_rules:
            # Group by rule type for breakdown
            rule_type = match.rule_type.value
            if rule_type not in breakdown:
                breakdown[rule_type] = Decimal("0")
            breakdown[rule_type] += match.effect
            total_adjustment += match.effect
        
        final_price = base_price + total_adjustment
        
        return final_price.quantize(Decimal("0.01")), breakdown
    
    def _apply_boundaries(
        self, price: Decimal, base_price: Decimal
    ) -> Decimal:
        """Apply price floor and ceiling."""
        min_price = base_price * Decimal(str(settings.price_floor_multiplier))
        max_price = base_price * Decimal(str(settings.price_ceiling_multiplier))
        
        if price < min_price:
            logger.info(f"Price {price} below floor, adjusted to {min_price}")
            return min_price
        if price > max_price:
            logger.info(f"Price {price} above ceiling, adjusted to {max_price}")
            return max_price
        
        return price


