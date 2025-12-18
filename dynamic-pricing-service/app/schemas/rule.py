"""
Pydantic schemas for pricing rule management APIs.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.models.pricing_rule import RuleType, RuleStatus, RuleAction


class RuleConditionSchema(BaseModel):
    """Schema for a rule condition."""
    field: str = Field(..., description="Field to evaluate (e.g., 'booking_date', 'party_size')")
    operator: str = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")
    values: Optional[List[Any]] = Field(None, description="Values for 'in' or 'between' operators")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "occupancy_rate",
                "operator": "greater_than",
                "value": 0.8
            }
        }


class TimeRestrictionSchema(BaseModel):
    """Schema for time-based restrictions."""
    days: Optional[List[int]] = Field(None, description="Days of week (0=Monday)")
    hours: Optional[Dict[str, int]] = Field(None, description="Hour range {'start': 9, 'end': 17}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "days": [0, 1, 2, 3, 4],
                "hours": {"start": 17, "end": 21}
            }
        }


class PricingRuleCreate(BaseModel):
    """Schema for creating a pricing rule."""
    rule_code: str = Field(..., min_length=1, max_length=50, description="Unique rule code")
    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    
    rule_type: RuleType = Field(..., description="Type of pricing rule")
    priority: int = Field(default=100, ge=1, le=10000, description="Priority (lower = higher)")
    
    # Applicability
    venue_types: Optional[List[str]] = Field(None, description="Applicable venue types")
    venue_ids: Optional[List[UUID]] = Field(None, description="Specific venue IDs")
    
    # Conditions
    conditions: List[RuleConditionSchema] = Field(default=[], description="Rule conditions")
    
    # Action
    action_type: RuleAction = Field(..., description="Action to apply")
    action_value: Decimal = Field(..., description="Action value (multiplier, amount, %)")
    
    # Price boundaries
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price floor")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price ceiling")
    
    # Stacking
    is_stackable: bool = Field(default=True, description="Can combine with other rules")
    exclusive_group: Optional[str] = Field(None, description="Exclusive group name")
    
    # Validity
    valid_from: Optional[datetime] = Field(None, description="Rule valid from")
    valid_until: Optional[datetime] = Field(None, description="Rule valid until")
    
    # Time restrictions
    time_restrictions: Optional[TimeRestrictionSchema] = Field(None, description="Time restrictions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_code": "CHRISTMAS_2024",
                "name": "Christmas Season Pricing",
                "description": "15% increase during Christmas season",
                "rule_type": "seasonal",
                "priority": 50,
                "venue_types": ["hotel", "restaurant"],
                "conditions": [
                    {"field": "booking_date", "operator": "between", "values": ["2024-12-20", "2024-12-31"]}
                ],
                "action_type": "percentage_increase",
                "action_value": "15.00",
                "is_stackable": True,
                "valid_from": "2024-12-20T00:00:00Z",
                "valid_until": "2024-12-31T23:59:59Z"
            }
        }


class PricingRuleUpdate(BaseModel):
    """Schema for updating a pricing rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[RuleStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=10000)
    
    venue_types: Optional[List[str]] = None
    venue_ids: Optional[List[UUID]] = None
    
    conditions: Optional[List[RuleConditionSchema]] = None
    
    action_type: Optional[RuleAction] = None
    action_value: Optional[Decimal] = None
    
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    
    is_stackable: Optional[bool] = None
    exclusive_group: Optional[str] = None
    
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    time_restrictions: Optional[TimeRestrictionSchema] = None


class PricingRuleResponse(BaseModel):
    """Response schema for a pricing rule."""
    id: UUID
    rule_code: str
    name: str
    description: Optional[str]
    
    rule_type: RuleType
    status: RuleStatus
    priority: int
    
    venue_types: Optional[List[str]]
    venue_ids: Optional[List[UUID]]
    
    conditions: List[Dict[str, Any]]
    
    action_type: RuleAction
    action_value: Decimal
    
    min_price: Optional[Decimal]
    max_price: Optional[Decimal]
    
    is_stackable: bool
    exclusive_group: Optional[str]
    
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    
    time_restrictions: Optional[Dict[str, Any]]
    
    version: int
    is_active: bool = Field(..., description="Is rule currently active and valid")
    
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class PricingRuleListResponse(BaseModel):
    """Response schema for paginated rule list."""
    rules: List[PricingRuleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


