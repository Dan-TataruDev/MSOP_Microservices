"""
GDPR compliance utilities.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID
from datetime import datetime
from app.services.guest_service import GuestService
from app.services.preference_service import PreferenceService
from app.services.interaction_service import InteractionService
from app.services.personalization_service import PersonalizationService
from app.schemas.guest import GuestDataExport


def export_guest_data(db: Session, guest_id: UUID) -> Dict[str, Any]:
    """
    Export all guest data in a structured format (GDPR Article 15 - Right to Access).
    """
    # Get guest profile
    guest = GuestService.get_guest_by_id(db, guest_id)
    if not guest:
        raise ValueError("Guest not found")
    
    # Get preferences
    preferences = PreferenceService.get_guest_preferences(db, guest_id, active_only=False)
    preferences_data = [
        {
            "id": str(pref.id),
            "key": pref.key,
            "value": pref.value,
            "value_type": pref.value_type,
            "source": pref.source,
            "confidence": pref.confidence,
            "is_active": pref.is_active,
            "created_at": pref.created_at.isoformat(),
            "updated_at": pref.updated_at.isoformat(),
        }
        for pref in preferences
    ]
    
    # Get interactions (limited to recent for export size)
    interactions = InteractionService.get_guest_interactions(db, guest_id, None)
    interactions_data = [
        {
            "id": str(inter.id),
            "interaction_type": inter.interaction_type.name if inter.interaction_type else None,
            "entity_type": inter.entity_type,
            "entity_id": inter.entity_id,
            "context": inter.context,
            "occurred_at": inter.occurred_at.isoformat(),
        }
        for inter in interactions[:1000]  # Limit for export size
    ]
    
    # Get segments
    segments = PersonalizationService.get_guest_segments(db, guest_id, active_only=False)
    segments_data = [
        {
            "id": str(seg.id),
            "segment_name": seg.segment_name,
            "segment_category": seg.segment_category,
            "confidence": seg.confidence,
            "assigned_at": seg.assigned_at.isoformat(),
            "is_active": seg.is_active,
        }
        for seg in segments
    ]
    
    # Get behavior signals
    signals = PersonalizationService.get_behavior_signals(db, guest_id, active_only=False)
    signals_data = [
        {
            "id": str(sig.id),
            "signal_type": sig.signal_type,
            "signal_name": sig.signal_name,
            "signal_value": sig.signal_value,
            "strength": sig.strength,
            "computed_at": sig.computed_at.isoformat(),
            "is_active": sig.is_active,
        }
        for sig in signals
    ]
    
    return {
        "guest": {
            "id": str(guest.id),
            "email": guest.email,
            "name": guest.name,
            "phone": guest.phone,
            "status": guest.status,
            "is_anonymous": guest.is_anonymous,
            "consent_marketing": guest.consent_marketing,
            "consent_analytics": guest.consent_analytics,
            "consent_personalization": guest.consent_personalization,
            "created_at": guest.created_at.isoformat(),
            "updated_at": guest.updated_at.isoformat(),
            "last_interaction_at": guest.last_interaction_at.isoformat() if guest.last_interaction_at else None,
        },
        "preferences": preferences_data,
        "interactions": interactions_data,
        "segments": segments_data,
        "behavior_signals": signals_data,
        "exported_at": datetime.utcnow().isoformat(),
    }
