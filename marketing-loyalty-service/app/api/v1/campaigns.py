"""
Campaign API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.services.campaign_service import CampaignService
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse
from app.models.campaign import CampaignStatus

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignResponse, status_code=201)
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new marketing campaign."""
    service = CampaignService(db)
    campaign = service.create_campaign(data)
    return campaign


@router.get("", response_model=CampaignListResponse)
def list_campaigns(
    status: Optional[CampaignStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List campaigns with optional filters."""
    service = CampaignService(db)
    items, total = service.list_campaigns(status, page, page_size)
    return CampaignListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/active", response_model=list[CampaignResponse])
def get_active_campaigns(venue_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    """Get all currently active campaigns."""
    service = CampaignService(db)
    return service.get_active_campaigns(venue_id)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: UUID, db: Session = Depends(get_db)):
    """Get campaign by ID."""
    service = CampaignService(db)
    campaign = service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/{campaign_id}/activate", response_model=CampaignResponse)
def activate_campaign(campaign_id: UUID, db: Session = Depends(get_db)):
    """Activate a draft campaign."""
    service = CampaignService(db)
    campaign = service.activate_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


