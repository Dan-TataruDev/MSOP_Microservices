"""
API endpoints for personalization data.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.personalization import (
    GuestSegmentResponse,
    BehaviorSignalResponse,
    PersonalizationContextResponse,
)
from app.services.personalization_service import PersonalizationService

router = APIRouter(prefix="/api/v1/guests", tags=["personalization"])


@router.get("/{guest_id}/personalization-context", response_model=PersonalizationContextResponse)
def get_personalization_context(guest_id: UUID, db: Session = Depends(get_db)):
    """Get personalization context for a guest (for AI services)."""
    # Verify guest exists
    from app.services.guest_service import GuestService
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    context = PersonalizationService.get_personalization_context(db, guest_id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get personalization context"
        )
    
    return context


@router.get("/{guest_id}/segments", response_model=List[GuestSegmentResponse])
def get_guest_segments(
    guest_id: UUID,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get guest segments."""
    # Verify guest exists
    from app.services.guest_service import GuestService
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    segments = PersonalizationService.get_guest_segments(db, guest_id, active_only)
    return segments


@router.get("/{guest_id}/behavior-signals", response_model=List[BehaviorSignalResponse])
def get_behavior_signals(
    guest_id: UUID,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get behavior signals for a guest."""
    # Verify guest exists
    from app.services.guest_service import GuestService
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    signals = PersonalizationService.get_behavior_signals(db, guest_id, active_only)
    return signals


@router.post("/{guest_id}/personalization-context/recompute", response_model=PersonalizationContextResponse)
def recompute_personalization_context(guest_id: UUID, db: Session = Depends(get_db)):
    """Manually trigger recomputation of personalization context."""
    # Verify guest exists
    from app.services.guest_service import GuestService
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    context = PersonalizationService.recompute_context(db, guest_id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to recompute personalization context"
        )
    
    return context
