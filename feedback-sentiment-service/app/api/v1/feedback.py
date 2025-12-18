"""
Feedback API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.services.feedback_service import FeedbackService
from app.schemas.feedback import (
    FeedbackCreate, FeedbackResponse, FeedbackListResponse, FeedbackStatusResponse
)
from app.models.feedback import FeedbackStatus

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201)
def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    # guest_id: Optional[UUID] = None,  # From auth middleware in production
):
    """
    Submit customer feedback (real-time, non-blocking).
    
    Feedback is stored immediately and the user receives an acknowledgment.
    Sentiment analysis happens asynchronously in the background.
    """
    service = FeedbackService(db)
    feedback = service.submit_feedback(data)
    return service.to_response(feedback)


@router.get("/{feedback_reference}", response_model=FeedbackResponse)
def get_feedback(
    feedback_reference: str,
    db: Session = Depends(get_db),
):
    """Get feedback by reference with sentiment analysis if available."""
    service = FeedbackService(db)
    feedback = service.get_feedback_by_reference(feedback_reference)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return service.to_response(feedback)


@router.get("/{feedback_reference}/status", response_model=FeedbackStatusResponse)
def get_feedback_status(
    feedback_reference: str,
    db: Session = Depends(get_db),
):
    """
    Check feedback analysis status.
    
    Use this endpoint to poll for analysis completion.
    """
    service = FeedbackService(db)
    feedback = service.get_feedback_by_reference(feedback_reference)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    response = service.to_response(feedback)
    return FeedbackStatusResponse(
        feedback_reference=feedback.feedback_reference,
        status=feedback.status,
        sentiment=response.sentiment,
        analyzed_at=feedback.analyzed_at,
    )


@router.get("", response_model=FeedbackListResponse)
def list_feedback(
    venue_id: Optional[UUID] = Query(None),
    status: Optional[FeedbackStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List feedback with optional filters."""
    service = FeedbackService(db)
    items, total = service.list_feedback(venue_id, status, page, page_size)
    
    return FeedbackListResponse(
        items=[service.to_response(f) for f in items],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )


