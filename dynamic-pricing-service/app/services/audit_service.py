"""
Audit Service - Comprehensive audit logging for pricing decisions.

All pricing-related actions are logged for:
- Regulatory compliance
- Business analytics
- Debugging and troubleshooting
- Customer dispute resolution
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import PriceAuditLog, AuditAction
from app.models.price_decision import PriceDecision
from app.models.pricing_rule import PricingRule, RuleStatus
from app.config import settings

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _create_log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[UUID],
        entity_reference: Optional[str] = None,
        actor_type: str = "system",
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        venue_id: Optional[UUID] = None,
        venue_type: Optional[str] = None,
        booking_id: Optional[UUID] = None,
        guest_id: Optional[UUID] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        request_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PriceAuditLog:
        """Create an audit log entry."""
        log = PriceAuditLog(
            action=action,
            action_description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_reference=entity_reference,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            venue_id=venue_id,
            venue_type=venue_type,
            booking_id=booking_id,
            guest_id=guest_id,
            old_value=old_value,
            new_value=new_value,
            changes=changes,
            metadata=metadata,
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        self.db.add(log)
        self.db.commit()
        
        return log
    
    # =========================================================================
    # Price Decision Audit Methods
    # =========================================================================
    
    def log_price_calculated(self, decision: PriceDecision) -> None:
        """Log a price calculation event."""
        self._create_log(
            action=AuditAction.PRICE_CALCULATED,
            entity_type="price_decision",
            entity_id=decision.id,
            entity_reference=decision.decision_reference,
            venue_id=decision.venue_id,
            venue_type=decision.venue_type,
            guest_id=decision.guest_id,
            new_value={
                "base_price": float(decision.base_price),
                "total_price": float(decision.total_price),
                "source": decision.source.value,
                "confidence": float(decision.ai_confidence) if decision.ai_confidence else None,
            },
            metadata={
                "calculation_time_ms": decision.calculation_time_ms,
                "party_size": decision.party_size,
                "booking_time": decision.booking_time.isoformat(),
            },
            description=f"Price calculated: {decision.total_price} {decision.currency}",
            request_id=decision.request_id,
            client_ip=decision.client_ip,
            user_agent=decision.user_agent,
        )
    
    def log_price_served(self, decision: PriceDecision) -> None:
        """Log when a price is served to client."""
        self._create_log(
            action=AuditAction.PRICE_SERVED,
            entity_type="price_decision",
            entity_id=decision.id,
            entity_reference=decision.decision_reference,
            venue_id=decision.venue_id,
            venue_type=decision.venue_type,
            guest_id=decision.guest_id,
            new_value={
                "total_price": float(decision.total_price),
                "served_at": decision.served_at.isoformat() if decision.served_at else None,
            },
            description=f"Price served to client: {decision.decision_reference}",
        )
    
    def log_price_accepted(self, decision: PriceDecision) -> None:
        """Log when a price is accepted (booking created)."""
        self._create_log(
            action=AuditAction.PRICE_ACCEPTED,
            entity_type="price_decision",
            entity_id=decision.id,
            entity_reference=decision.decision_reference,
            venue_id=decision.venue_id,
            venue_type=decision.venue_type,
            booking_id=decision.booking_id,
            guest_id=decision.guest_id,
            new_value={
                "total_price": float(decision.total_price),
                "booking_reference": decision.booking_reference,
                "accepted_at": decision.accepted_at.isoformat() if decision.accepted_at else None,
            },
            description=f"Price accepted for booking {decision.booking_reference}",
        )
    
    def log_fallback_triggered(
        self,
        decision_reference: str,
        reason: str,
        fallback_source: str,
    ) -> None:
        """Log when fallback pricing is used."""
        self._create_log(
            action=AuditAction.FALLBACK_TRIGGERED,
            entity_type="price_decision",
            entity_id=None,
            entity_reference=decision_reference,
            metadata={
                "reason": reason,
                "fallback_source": fallback_source,
            },
            description=f"Fallback triggered: {reason}",
        )
    
    def log_ai_model_called(
        self,
        decision_id: UUID,
        model_version: str,
        response_time_ms: int,
        success: bool,
    ) -> None:
        """Log AI model call."""
        self._create_log(
            action=AuditAction.AI_MODEL_CALLED if success else AuditAction.AI_MODEL_FAILED,
            entity_type="price_decision",
            entity_id=decision_id,
            metadata={
                "model_version": model_version,
                "response_time_ms": response_time_ms,
                "success": success,
            },
            description=f"AI model {'succeeded' if success else 'failed'}: {model_version}",
        )
    
    # =========================================================================
    # Pricing Rule Audit Methods
    # =========================================================================
    
    def log_rule_created(
        self, rule: PricingRule, created_by: Optional[str]
    ) -> None:
        """Log rule creation."""
        self._create_log(
            action=AuditAction.RULE_CREATED,
            entity_type="pricing_rule",
            entity_id=rule.id,
            entity_reference=rule.rule_code,
            actor_type="user" if created_by else "system",
            actor_id=created_by,
            new_value={
                "rule_code": rule.rule_code,
                "name": rule.name,
                "rule_type": rule.rule_type.value,
                "action_type": rule.action_type.value,
                "action_value": float(rule.action_value),
            },
            description=f"Created pricing rule: {rule.rule_code}",
        )
    
    def log_rule_updated(
        self,
        rule: PricingRule,
        old_values: Dict[str, Any],
        updated_by: Optional[str],
    ) -> None:
        """Log rule update."""
        self._create_log(
            action=AuditAction.RULE_UPDATED,
            entity_type="pricing_rule",
            entity_id=rule.id,
            entity_reference=rule.rule_code,
            actor_type="user" if updated_by else "system",
            actor_id=updated_by,
            old_value=old_values,
            new_value={
                "name": rule.name,
                "status": rule.status.value if rule.status else None,
                "priority": rule.priority,
                "action_value": float(rule.action_value) if rule.action_value else None,
                "version": rule.version,
            },
            description=f"Updated pricing rule: {rule.rule_code} (v{rule.version})",
        )
    
    def log_rule_activated(
        self,
        rule: PricingRule,
        old_status: RuleStatus,
        activated_by: Optional[str],
    ) -> None:
        """Log rule activation."""
        self._create_log(
            action=AuditAction.RULE_ACTIVATED,
            entity_type="pricing_rule",
            entity_id=rule.id,
            entity_reference=rule.rule_code,
            actor_type="user" if activated_by else "system",
            actor_id=activated_by,
            old_value={"status": old_status.value},
            new_value={"status": rule.status.value},
            description=f"Activated pricing rule: {rule.rule_code}",
        )
    
    def log_rule_deactivated(
        self,
        rule: PricingRule,
        old_status: RuleStatus,
        deactivated_by: Optional[str],
    ) -> None:
        """Log rule deactivation."""
        self._create_log(
            action=AuditAction.RULE_DEACTIVATED,
            entity_type="pricing_rule",
            entity_id=rule.id,
            entity_reference=rule.rule_code,
            actor_type="user" if deactivated_by else "system",
            actor_id=deactivated_by,
            old_value={"status": old_status.value},
            new_value={"status": rule.status.value},
            description=f"Deactivated pricing rule: {rule.rule_code}",
        )
    
    def log_rule_deleted(
        self, rule: PricingRule, deleted_by: Optional[str]
    ) -> None:
        """Log rule deletion."""
        self._create_log(
            action=AuditAction.RULE_DELETED,
            entity_type="pricing_rule",
            entity_id=rule.id,
            entity_reference=rule.rule_code,
            actor_type="user" if deleted_by else "system",
            actor_id=deleted_by,
            old_value={
                "rule_code": rule.rule_code,
                "name": rule.name,
                "status": rule.status.value if rule.status else None,
            },
            description=f"Deleted pricing rule: {rule.rule_code}",
        )
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get_decision_audit_trail(
        self, decision_id: UUID
    ) -> List[PriceAuditLog]:
        """Get all audit logs for a price decision."""
        return (
            self.db.query(PriceAuditLog)
            .filter(
                PriceAuditLog.entity_type == "price_decision",
                PriceAuditLog.entity_id == decision_id,
            )
            .order_by(PriceAuditLog.created_at.asc())
            .all()
        )
    
    def get_rule_audit_trail(self, rule_id: UUID) -> List[PriceAuditLog]:
        """Get all audit logs for a pricing rule."""
        return (
            self.db.query(PriceAuditLog)
            .filter(
                PriceAuditLog.entity_type == "pricing_rule",
                PriceAuditLog.entity_id == rule_id,
            )
            .order_by(PriceAuditLog.created_at.asc())
            .all()
        )
    
    def get_venue_audit_logs(
        self,
        venue_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[PriceAuditLog]:
        """Get audit logs for a specific venue."""
        query = self.db.query(PriceAuditLog).filter(
            PriceAuditLog.venue_id == venue_id
        )
        
        if from_date:
            query = query.filter(PriceAuditLog.created_at >= from_date)
        if to_date:
            query = query.filter(PriceAuditLog.created_at <= to_date)
        
        return (
            query
            .order_by(PriceAuditLog.created_at.desc())
            .limit(limit)
            .all()
        )


