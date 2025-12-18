"""
Campaign Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.campaign import CampaignStatus, CampaignType


class CampaignCreate(BaseModel):
    """Schema for creating a campaign."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    campaign_type: CampaignType
    venue_id: Optional[UUID] = None
    start_date: datetime
    end_date: datetime
    eligibility_rules: Dict[str, Any] = Field(default_factory=dict)
    campaign_config: Dict[str, Any] = Field(default_factory=dict)
    max_redemptions: Optional[int] = None
    max_per_guest: int = 1
    priority: int = 0
    is_stackable: bool = False


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    end_date: Optional[datetime] = None
    eligibility_rules: Optional[Dict[str, Any]] = None
    campaign_config: Optional[Dict[str, Any]] = None
    max_redemptions: Optional[int] = None


class CampaignResponse(BaseModel):
    """Schema for campaign response."""
    id: UUID
    campaign_code: str
    name: str
    description: Optional[str]
    campaign_type: CampaignType
    status: CampaignStatus
    venue_id: Optional[UUID]
    start_date: datetime
    end_date: datetime
    eligibility_rules: Dict[str, Any]
    campaign_config: Dict[str, Any]
    max_redemptions: Optional[int]
    current_redemptions: int
    priority: int
    is_stackable: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    """Paginated campaign list."""
    items: List[CampaignResponse]
    total: int
    page: int
    page_size: int


