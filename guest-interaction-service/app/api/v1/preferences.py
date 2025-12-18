"""
API endpoints for preference management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.preference import (
    PreferenceCreate,
    PreferenceUpdate,
    PreferenceResponse,
    PreferenceCategoryResponse,
    PreferenceHistoryResponse,
)
from app.services.preference_service import PreferenceService
from app.events.publisher import event_publisher

router = APIRouter(prefix="/api/v1/guests", tags=["preferences"])


@router.get("/{guest_id}/preferences", response_model=List[PreferenceResponse])
def get_guest_preferences(
    guest_id: UUID,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all preferences for a guest."""
    preferences = PreferenceService.get_guest_preferences(db, guest_id, active_only)
    return preferences


@router.get("/{guest_id}/preferences/{preference_key}", response_model=PreferenceResponse)
def get_guest_preference_by_key(
    guest_id: UUID,
    preference_key: str,
    db: Session = Depends(get_db)
):
    """Get a specific preference by key."""
    preference = PreferenceService.get_preference_by_key(db, guest_id, preference_key)
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    return preference


@router.post("/{guest_id}/preferences", response_model=PreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_preference(
    guest_id: UUID,
    preference_data: PreferenceCreate,
    db: Session = Depends(get_db)
):
    """Create a new preference for a guest."""
    # Verify guest exists
    from app.services.guest_service import GuestService
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    preference = PreferenceService.create_preference(db, guest_id, preference_data)
    
    # Publish event
    event_publisher.publish_preferences_updated(
        guest_id,
        preference.key,
        None,
        preference.value
    )
    
    return preference


@router.put("/{guest_id}/preferences/{preference_id}", response_model=PreferenceResponse)
def update_preference(
    guest_id: UUID,
    preference_id: UUID,
    preference_data: PreferenceUpdate,
    db: Session = Depends(get_db)
):
    """Update a preference."""
    preference = PreferenceService.get_preference_by_id(db, preference_id)
    if not preference or preference.guest_id != guest_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    old_value = preference.value
    updated_preference = PreferenceService.update_preference(
        db,
        preference_id,
        preference_data,
        changed_by="user"  # In production, get from auth context
    )
    
    # Publish event
    event_publisher.publish_preferences_updated(
        guest_id,
        updated_preference.key,
        old_value,
        updated_preference.value
    )
    
    return updated_preference


@router.get("/{guest_id}/preferences/history", response_model=List[PreferenceHistoryResponse])
def get_preference_history(
    guest_id: UUID,
    preference_id: UUID,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get preference change history."""
    preference = PreferenceService.get_preference_by_id(db, preference_id)
    if not preference or preference.guest_id != guest_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    history = PreferenceService.get_preference_history(db, preference_id, limit)
    return history


@router.get("/preference-categories", response_model=List[PreferenceCategoryResponse])
def get_preference_categories(db: Session = Depends(get_db)):
    """Get all preference categories."""
    categories = PreferenceService.get_all_categories(db)
    return categories


# Separate router for preference categories (not guest-specific)
categories_router = APIRouter(prefix="/api/v1", tags=["preference-categories"])


@categories_router.get("/preference-categories", response_model=List[PreferenceCategoryResponse])
def get_all_preference_categories(db: Session = Depends(get_db)):
    """Get all preference categories."""
    categories = PreferenceService.get_all_categories(db)
    return categories
