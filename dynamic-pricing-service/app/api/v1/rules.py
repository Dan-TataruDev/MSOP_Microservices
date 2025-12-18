"""
Pricing Rules management API endpoints.

CRUD operations for pricing rules that define
how dynamic prices are calculated.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.services.rule_service import RuleService
from app.models.pricing_rule import RuleType, RuleStatus
from app.schemas.rule import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PricingRuleResponse,
    PricingRuleListResponse,
)

router = APIRouter(prefix="/rules", tags=["Pricing Rules"])


@router.post(
    "",
    response_model=PricingRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a pricing rule",
    description="""
    Create a new pricing rule.
    
    Rules define how prices are dynamically adjusted based on conditions like:
    - Seasonality (Christmas, Summer, etc.)
    - Time of day/week (Peak hours, weekends)
    - Demand levels (High occupancy)
    - Customer segments (Loyalty tiers)
    
    New rules are created in DRAFT status and must be activated.
    """
)
async def create_rule(
    rule_data: PricingRuleCreate,
    db: Session = Depends(get_db),
    # In production, get from auth token
    created_by: Optional[str] = Query(None, description="User creating the rule"),
) -> PricingRuleResponse:
    """Create a new pricing rule."""
    service = RuleService(db)
    
    try:
        rule = service.create_rule(rule_data, created_by)
        return _rule_to_response(rule)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=PricingRuleListResponse,
    summary="List pricing rules",
    description="Get a paginated list of pricing rules with optional filtering."
)
async def list_rules(
    rule_type: Optional[RuleType] = Query(None, description="Filter by rule type"),
    status: Optional[RuleStatus] = Query(None, description="Filter by status"),
    venue_type: Optional[str] = Query(None, description="Filter by venue type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> PricingRuleListResponse:
    """List pricing rules with filtering and pagination."""
    service = RuleService(db)
    return service.list_rules(
        rule_type=rule_type,
        status=status,
        venue_type=venue_type,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{rule_id}",
    response_model=PricingRuleResponse,
    summary="Get a pricing rule",
    description="Get details of a specific pricing rule by ID."
)
async def get_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
) -> PricingRuleResponse:
    """Get a single pricing rule."""
    service = RuleService(db)
    rule = service.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    return _rule_to_response(rule)


@router.patch(
    "/{rule_id}",
    response_model=PricingRuleResponse,
    summary="Update a pricing rule",
    description="Update an existing pricing rule. Creates a new version."
)
async def update_rule(
    rule_id: UUID,
    rule_data: PricingRuleUpdate,
    db: Session = Depends(get_db),
    updated_by: Optional[str] = Query(None, description="User updating the rule"),
) -> PricingRuleResponse:
    """Update a pricing rule."""
    service = RuleService(db)
    rule = service.update_rule(rule_id, rule_data, updated_by)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    return _rule_to_response(rule)


@router.post(
    "/{rule_id}/activate",
    response_model=PricingRuleResponse,
    summary="Activate a pricing rule",
    description="Activate a pricing rule. Only active rules are applied to pricing."
)
async def activate_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    activated_by: Optional[str] = Query(None, description="User activating the rule"),
) -> PricingRuleResponse:
    """Activate a pricing rule."""
    service = RuleService(db)
    rule = service.activate_rule(rule_id, activated_by)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    return _rule_to_response(rule)


@router.post(
    "/{rule_id}/deactivate",
    response_model=PricingRuleResponse,
    summary="Deactivate a pricing rule",
    description="Deactivate (pause) a pricing rule. The rule will no longer be applied."
)
async def deactivate_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    deactivated_by: Optional[str] = Query(None, description="User deactivating the rule"),
) -> PricingRuleResponse:
    """Deactivate a pricing rule."""
    service = RuleService(db)
    rule = service.deactivate_rule(rule_id, deactivated_by)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    return _rule_to_response(rule)


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pricing rule",
    description="Soft delete a pricing rule. The rule is archived and no longer applied."
)
async def delete_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    deleted_by: Optional[str] = Query(None, description="User deleting the rule"),
):
    """Delete a pricing rule."""
    service = RuleService(db)
    success = service.delete_rule(rule_id, deleted_by)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )


def _rule_to_response(rule) -> PricingRuleResponse:
    """Convert rule model to response schema."""
    return PricingRuleResponse(
        id=rule.id,
        rule_code=rule.rule_code,
        name=rule.name,
        description=rule.description,
        rule_type=rule.rule_type,
        status=rule.status,
        priority=rule.priority,
        venue_types=rule.venue_types,
        venue_ids=[UUID(v) for v in rule.venue_ids] if rule.venue_ids else None,
        conditions=rule.conditions or [],
        action_type=rule.action_type,
        action_value=rule.action_value,
        min_price=rule.min_price,
        max_price=rule.max_price,
        is_stackable=rule.is_stackable,
        exclusive_group=rule.exclusive_group,
        valid_from=rule.valid_from,
        valid_until=rule.valid_until,
        time_restrictions=rule.time_restrictions,
        version=rule.version,
        is_active=rule.is_active(),
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        created_by=rule.created_by,
    )


