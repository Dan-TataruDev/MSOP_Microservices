"""
Insights API endpoints for analytics and marketing services.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.services.insights_service import InsightsService
from app.schemas.insights import InsightsSummary, VenueInsights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/summary", response_model=InsightsSummary)
def get_insights_summary(
    venue_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get aggregated sentiment insights (batch endpoint for analytics).
    
    This endpoint is designed for analytics and marketing services
    to retrieve summarized insights. Results can be cached.
    """
    service = InsightsService(db)
    return service.get_summary(venue_id, start_date, end_date)


@router.get("/venues/{venue_id}", response_model=VenueInsights)
def get_venue_insights(
    venue_id: UUID,
    db: Session = Depends(get_db),
):
    """Get insights for a specific venue with comparison to platform average."""
    service = InsightsService(db)
    return service.get_venue_insights(venue_id)


