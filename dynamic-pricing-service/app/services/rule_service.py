"""
Rule Service - Manages pricing rules.

Provides CRUD operations for pricing rules and
handles rule versioning and auditing.
"""
import logging
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.pricing_rule import PricingRule, RuleType, RuleStatus
from app.schemas.rule import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PricingRuleResponse,
    PricingRuleListResponse,
)
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class RuleService:
    """Service for managing pricing rules."""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def create_rule(
        self,
        rule_data: PricingRuleCreate,
        created_by: Optional[str] = None,
    ) -> PricingRule:
        """Create a new pricing rule."""
        # Check for duplicate rule code
        existing = self.db.query(PricingRule).filter(
            PricingRule.rule_code == rule_data.rule_code,
            PricingRule.is_deleted == False,
        ).first()
        
        if existing:
            raise ValueError(f"Rule code '{rule_data.rule_code}' already exists")
        
        rule = PricingRule(
            rule_code=rule_data.rule_code,
            name=rule_data.name,
            description=rule_data.description,
            rule_type=rule_data.rule_type,
            status=RuleStatus.DRAFT,  # New rules start as draft
            priority=rule_data.priority,
            venue_types=rule_data.venue_types,
            venue_ids=[str(v) for v in rule_data.venue_ids] if rule_data.venue_ids else None,
            conditions=[c.model_dump() for c in rule_data.conditions],
            action_type=rule_data.action_type,
            action_value=rule_data.action_value,
            min_price=rule_data.min_price,
            max_price=rule_data.max_price,
            is_stackable=rule_data.is_stackable,
            exclusive_group=rule_data.exclusive_group,
            valid_from=rule_data.valid_from,
            valid_until=rule_data.valid_until,
            time_restrictions=rule_data.time_restrictions.model_dump() if rule_data.time_restrictions else None,
            created_by=created_by,
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        # Audit
        self.audit_service.log_rule_created(rule, created_by)
        
        logger.info(f"Created pricing rule: {rule.rule_code}")
        return rule
    
    def update_rule(
        self,
        rule_id: UUID,
        rule_data: PricingRuleUpdate,
        updated_by: Optional[str] = None,
    ) -> Optional[PricingRule]:
        """Update an existing pricing rule."""
        rule = self.db.query(PricingRule).filter(
            PricingRule.id == rule_id,
            PricingRule.is_deleted == False,
        ).first()
        
        if not rule:
            return None
        
        # Store old values for audit
        old_values = {
            "name": rule.name,
            "status": rule.status.value if rule.status else None,
            "priority": rule.priority,
            "action_value": float(rule.action_value) if rule.action_value else None,
        }
        
        # Update fields
        update_data = rule_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "conditions" and value is not None:
                value = [c.model_dump() if hasattr(c, 'model_dump') else c for c in value]
            if field == "time_restrictions" and value is not None:
                value = value.model_dump() if hasattr(value, 'model_dump') else value
            if field == "venue_ids" and value is not None:
                value = [str(v) for v in value]
            setattr(rule, field, value)
        
        rule.version += 1
        rule.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(rule)
        
        # Audit
        self.audit_service.log_rule_updated(rule, old_values, updated_by)
        
        logger.info(f"Updated pricing rule: {rule.rule_code}")
        return rule
    
    def activate_rule(
        self, rule_id: UUID, activated_by: Optional[str] = None
    ) -> Optional[PricingRule]:
        """Activate a pricing rule."""
        rule = self.db.query(PricingRule).filter(
            PricingRule.id == rule_id,
            PricingRule.is_deleted == False,
        ).first()
        
        if not rule:
            return None
        
        old_status = rule.status
        rule.status = RuleStatus.ACTIVE
        rule.updated_by = activated_by
        
        self.db.commit()
        self.db.refresh(rule)
        
        # Audit
        self.audit_service.log_rule_activated(rule, old_status, activated_by)
        
        logger.info(f"Activated pricing rule: {rule.rule_code}")
        return rule
    
    def deactivate_rule(
        self, rule_id: UUID, deactivated_by: Optional[str] = None
    ) -> Optional[PricingRule]:
        """Deactivate (pause) a pricing rule."""
        rule = self.db.query(PricingRule).filter(
            PricingRule.id == rule_id,
            PricingRule.is_deleted == False,
        ).first()
        
        if not rule:
            return None
        
        old_status = rule.status
        rule.status = RuleStatus.PAUSED
        rule.updated_by = deactivated_by
        
        self.db.commit()
        self.db.refresh(rule)
        
        # Audit
        self.audit_service.log_rule_deactivated(rule, old_status, deactivated_by)
        
        logger.info(f"Deactivated pricing rule: {rule.rule_code}")
        return rule
    
    def delete_rule(
        self, rule_id: UUID, deleted_by: Optional[str] = None
    ) -> bool:
        """Soft delete a pricing rule."""
        rule = self.db.query(PricingRule).filter(
            PricingRule.id == rule_id,
            PricingRule.is_deleted == False,
        ).first()
        
        if not rule:
            return False
        
        rule.is_deleted = True
        rule.deleted_at = datetime.utcnow()
        rule.status = RuleStatus.ARCHIVED
        rule.updated_by = deleted_by
        
        self.db.commit()
        
        # Audit
        self.audit_service.log_rule_deleted(rule, deleted_by)
        
        logger.info(f"Deleted pricing rule: {rule.rule_code}")
        return True
    
    def get_rule(self, rule_id: UUID) -> Optional[PricingRule]:
        """Get a single pricing rule by ID."""
        return self.db.query(PricingRule).filter(
            PricingRule.id == rule_id,
            PricingRule.is_deleted == False,
        ).first()
    
    def get_rule_by_code(self, rule_code: str) -> Optional[PricingRule]:
        """Get a single pricing rule by code."""
        return self.db.query(PricingRule).filter(
            PricingRule.rule_code == rule_code,
            PricingRule.is_deleted == False,
        ).first()
    
    def list_rules(
        self,
        rule_type: Optional[RuleType] = None,
        status: Optional[RuleStatus] = None,
        venue_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PricingRuleListResponse:
        """List pricing rules with filtering and pagination."""
        query = self.db.query(PricingRule).filter(
            PricingRule.is_deleted == False
        )
        
        # Apply filters
        if rule_type:
            query = query.filter(PricingRule.rule_type == rule_type)
        if status:
            query = query.filter(PricingRule.status == status)
        if venue_type:
            query = query.filter(
                or_(
                    PricingRule.venue_types == None,
                    PricingRule.venue_types.contains([venue_type])
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        rules = (
            query
            .order_by(PricingRule.priority.asc(), PricingRule.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        
        # Convert to response
        rule_responses = [
            PricingRuleResponse(
                id=r.id,
                rule_code=r.rule_code,
                name=r.name,
                description=r.description,
                rule_type=r.rule_type,
                status=r.status,
                priority=r.priority,
                venue_types=r.venue_types,
                venue_ids=[UUID(v) for v in r.venue_ids] if r.venue_ids else None,
                conditions=r.conditions or [],
                action_type=r.action_type,
                action_value=r.action_value,
                min_price=r.min_price,
                max_price=r.max_price,
                is_stackable=r.is_stackable,
                exclusive_group=r.exclusive_group,
                valid_from=r.valid_from,
                valid_until=r.valid_until,
                time_restrictions=r.time_restrictions,
                version=r.version,
                is_active=r.is_active(),
                created_at=r.created_at,
                updated_at=r.updated_at,
                created_by=r.created_by,
            )
            for r in rules
        ]
        
        total_pages = (total + page_size - 1) // page_size
        
        return PricingRuleListResponse(
            rules=rule_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    
    def get_active_rules_count(self) -> int:
        """Get count of currently active rules."""
        return self.db.query(PricingRule).filter(
            PricingRule.status == RuleStatus.ACTIVE,
            PricingRule.is_deleted == False,
        ).count()


