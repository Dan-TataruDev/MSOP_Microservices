"""
Personalization service - business logic for personalization data management.
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.personalization import (
    GuestSegment,
    BehaviorSignal,
    PersonalizationContext
)
from app.models.preference import Preference
from app.models.interaction import Interaction
from app.services.guest_service import GuestService


class PersonalizationService:
    """Service for managing personalization data and context."""
    
    @staticmethod
    def get_personalization_context(
        db: Session,
        guest_id: UUID
    ) -> Optional[PersonalizationContext]:
        """Get or create personalization context for a guest."""
        context = db.query(PersonalizationContext).filter(
            PersonalizationContext.guest_id == guest_id
        ).first()
        
        if not context:
            # Create initial context
            context = PersonalizationService._compute_context(db, guest_id)
        
        return context
    
    @staticmethod
    def _compute_context(
        db: Session,
        guest_id: UUID
    ) -> PersonalizationContext:
        """Compute personalization context from guest data."""
        # Get active preferences
        preferences = db.query(Preference).filter(
            Preference.guest_id == guest_id,
            Preference.is_active == True
        ).all()
        
        # Build preference vector
        preference_vector = {}
        for pref in preferences:
            preference_vector[pref.key] = {
                "value": pref.value,
                "type": pref.value_type,
                "confidence": pref.confidence,
                "source": pref.source,
            }
        
        # Get recent interactions summary
        recent_interactions = db.query(Interaction).filter(
            Interaction.guest_id == guest_id
        ).order_by(Interaction.occurred_at.desc()).limit(100).all()
        
        behavior_summary = {
            "total_interactions": len(recent_interactions),
            "recent_interaction_types": {},
            "frequent_entities": {},
        }
        
        for interaction in recent_interactions[:50]:  # Last 50
            # Count interaction types
            it_name = interaction.interaction_type.name if interaction.interaction_type else "unknown"
            behavior_summary["recent_interaction_types"][it_name] = \
                behavior_summary["recent_interaction_types"].get(it_name, 0) + 1
            
            # Track frequent entities
            if interaction.entity_type and interaction.entity_id:
                key = f"{interaction.entity_type}:{interaction.entity_id}"
                behavior_summary["frequent_entities"][key] = \
                    behavior_summary["frequent_entities"].get(key, 0) + 1
        
        # Get active segments
        segments = db.query(GuestSegment).filter(
            GuestSegment.guest_id == guest_id,
            GuestSegment.is_active == True
        ).all()
        segment_names = [seg.segment_name for seg in segments]
        
        # Get active signals
        signals = db.query(BehaviorSignal).filter(
            BehaviorSignal.guest_id == guest_id,
            BehaviorSignal.is_active == True
        ).all()
        signal_data = [
            {
                "type": sig.signal_type,
                "name": sig.signal_name,
                "value": sig.signal_value,
                "strength": sig.strength,
            }
            for sig in signals
        ]
        
        # Create or update context
        context = db.query(PersonalizationContext).filter(
            PersonalizationContext.guest_id == guest_id
        ).first()
        
        if context:
            context.preference_vector = preference_vector
            context.behavior_summary = behavior_summary
            context.segments = segment_names
            context.signals = signal_data
            context.version += 1
            context.computed_at = datetime.utcnow()
        else:
            context = PersonalizationContext(
                guest_id=guest_id,
                preference_vector=preference_vector,
                behavior_summary=behavior_summary,
                segments=segment_names,
                signals=signal_data,
            )
            db.add(context)
        
        db.commit()
        db.refresh(context)
        return context
    
    @staticmethod
    def get_guest_segments(
        db: Session,
        guest_id: UUID,
        active_only: bool = True
    ) -> List[GuestSegment]:
        """Get segments for a guest."""
        query = db.query(GuestSegment).filter(GuestSegment.guest_id == guest_id)
        if active_only:
            query = query.filter(GuestSegment.is_active == True)
        return query.all()
    
    @staticmethod
    def get_behavior_signals(
        db: Session,
        guest_id: UUID,
        active_only: bool = True
    ) -> List[BehaviorSignal]:
        """Get behavior signals for a guest."""
        query = db.query(BehaviorSignal).filter(BehaviorSignal.guest_id == guest_id)
        if active_only:
            query = query.filter(BehaviorSignal.is_active == True)
        return query.all()
    
    @staticmethod
    def recompute_context(db: Session, guest_id: UUID) -> Optional[PersonalizationContext]:
        """Manually trigger context recomputation."""
        return PersonalizationService._compute_context(db, guest_id)
