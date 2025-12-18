"""
API endpoints for guest profile management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.guest import GuestCreate, GuestUpdate, GuestResponse, GuestDataExport
from app.services.guest_service import GuestService
from app.services.preference_service import PreferenceService
from app.services.interaction_service import InteractionService
from app.services.personalization_service import PersonalizationService
from app.events.publisher import event_publisher
from app.utils.gdpr import export_guest_data

router = APIRouter(prefix="/api/v1/guests", tags=["guests"])


@router.get("/{guest_id}/profile", response_model=GuestResponse)
def get_guest_profile(guest_id: UUID, db: Session = Depends(get_db)):
    """Get guest profile by ID."""
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    return guest


@router.get("/me/profile", response_model=GuestResponse)
def get_current_guest_profile(
    # In production, extract guest_id from JWT token
    guest_id: UUID = None,  # Placeholder - should come from auth middleware
    db: Session = Depends(get_db)
):
    """Get current authenticated guest's profile."""
    if not guest_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return get_guest_profile(guest_id, db)


@router.post("", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
def create_guest(guest_data: GuestCreate, db: Session = Depends(get_db)):
    """Create a new guest profile."""
    # Check if guest with email already exists
    if guest_data.email:
        existing = GuestService.get_guest_by_email(db, guest_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Guest with this email already exists"
            )
    
    guest = GuestService.create_guest(db, guest_data)
    
    # Publish event
    event_publisher.publish_profile_created(
        guest.id,
        {
            "email": guest.email,
            "name": guest.name,
            "is_anonymous": guest.is_anonymous,
        }
    )
    
    return guest


@router.patch("/{guest_id}/profile", response_model=GuestResponse)
def update_guest_profile(
    guest_id: UUID,
    guest_data: GuestUpdate,
    db: Session = Depends(get_db)
):
    """Update guest profile."""
    guest = GuestService.update_guest(db, guest_id, guest_data)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    # Publish event
    changes = guest_data.model_dump(exclude_unset=True)
    if changes:
        event_publisher.publish_profile_updated(guest_id, changes)
    
    return guest


@router.get("/{guest_id}/data-export")
def export_guest_data_gdpr(guest_id: UUID, db: Session = Depends(get_db)):
    """Export all guest data (GDPR right to access)."""
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    export_data = export_guest_data(db, guest_id)
    
    # Publish event
    event_publisher.publish_data_exported(guest_id)
    
    return export_data


@router.delete("/{guest_id}/data", status_code=status.HTTP_204_NO_CONTENT)
def delete_guest_data(guest_id: UUID, db: Session = Depends(get_db)):
    """Delete guest data (GDPR right to erasure)."""
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    success = GuestService.delete_guest(db, guest_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete guest data"
        )
    
    # Publish event
    event_publisher.publish_data_deleted(guest_id)
    
    return None


@router.get("/{guest_id}/consent")
def get_guest_consent(guest_id: UUID, db: Session = Depends(get_db)):
    """Get guest consent preferences."""
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    return {
        "consent_marketing": guest.consent_marketing,
        "consent_analytics": guest.consent_analytics,
        "consent_personalization": guest.consent_personalization,
    }


@router.put("/{guest_id}/consent")
def update_guest_consent(
    guest_id: UUID,
    consent_data: dict,
    db: Session = Depends(get_db)
):
    """Update guest consent preferences."""
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    # Update consent fields
    if "consent_marketing" in consent_data:
        guest.consent_marketing = consent_data["consent_marketing"]
        event_publisher.publish_consent_updated(guest_id, "marketing", consent_data["consent_marketing"])
    
    if "consent_analytics" in consent_data:
        guest.consent_analytics = consent_data["consent_analytics"]
        event_publisher.publish_consent_updated(guest_id, "analytics", consent_data["consent_analytics"])
    
    if "consent_personalization" in consent_data:
        guest.consent_personalization = consent_data["consent_personalization"]
        event_publisher.publish_consent_updated(guest_id, "personalization", consent_data["consent_personalization"])
    
    db.commit()
    db.refresh(guest)
    
    return {
        "consent_marketing": guest.consent_marketing,
        "consent_analytics": guest.consent_analytics,
        "consent_personalization": guest.consent_personalization,
    }
