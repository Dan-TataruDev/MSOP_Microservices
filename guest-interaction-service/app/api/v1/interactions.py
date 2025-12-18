"""
API endpoints for interaction history management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionTypeResponse,
    InteractionFilter,
)
from app.services.interaction_service import InteractionService
from app.events.publisher import event_publisher

router = APIRouter(prefix="/api/v1/guests", tags=["interactions"])


@router.post("/{guest_id}/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_interaction(
    guest_id: UUID,
    interaction_data: InteractionCreate,
    db: Session = Depends(get_db)
):
    """Record a new interaction for a guest."""
    # Verify guest exists
    from app.services.guest_service import GuestService
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    interaction = InteractionService.create_interaction(db, guest_id, interaction_data)
    
    # Publish event
    interaction_type_name = interaction.interaction_type.name if interaction.interaction_type else "unknown"
    event_publisher.publish_interaction_recorded(
        guest_id,
        interaction_type_name,
        interaction.entity_type,
        interaction.entity_id
    )
    
    return interaction


@router.get("/{guest_id}/interactions", response_model=List[InteractionResponse])
def get_guest_interactions(
    guest_id: UUID,
    filters: InteractionFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get interaction history for a guest with optional filtering."""
    # Verify guest exists
    from app.services.guest_service import GuestService
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    interactions = InteractionService.get_guest_interactions(db, guest_id, filters)
    return interactions


@router.get("/interaction-types", response_model=List[InteractionTypeResponse])
def get_interaction_types(db: Session = Depends(get_db)):
    """Get all interaction types."""
    types = InteractionService.get_all_interaction_types(db)
    return types
