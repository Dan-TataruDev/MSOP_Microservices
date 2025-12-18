"""
Preference service - business logic for preference management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.preference import Preference, PreferenceHistory, PreferenceCategory
from app.schemas.preference import PreferenceCreate, PreferenceUpdate


class PreferenceService:
    """Service for managing guest preferences."""
    
    @staticmethod
    def get_preference_by_id(db: Session, preference_id: UUID) -> Optional[Preference]:
        """Get preference by ID."""
        return db.query(Preference).filter(Preference.id == preference_id).first()
    
    @staticmethod
    def get_guest_preferences(
        db: Session, 
        guest_id: UUID, 
        active_only: bool = True
    ) -> List[Preference]:
        """Get all preferences for a guest."""
        query = db.query(Preference).filter(Preference.guest_id == guest_id)
        if active_only:
            query = query.filter(Preference.is_active == True)
        return query.all()
    
    @staticmethod
    def get_preference_by_key(
        db: Session, 
        guest_id: UUID, 
        key: str, 
        active_only: bool = True
    ) -> Optional[Preference]:
        """Get preference by key for a guest."""
        query = db.query(Preference).filter(
            and_(
                Preference.guest_id == guest_id,
                Preference.key == key
            )
        )
        if active_only:
            query = query.filter(Preference.is_active == True)
        return query.first()
    
    @staticmethod
    def create_preference(
        db: Session, 
        guest_id: UUID, 
        preference_data: PreferenceCreate
    ) -> Preference:
        """Create a new preference."""
        preference = Preference(
            guest_id=guest_id,
            category_id=preference_data.category_id,
            key=preference_data.key,
            value=preference_data.value,
            value_type=preference_data.value_type,
            source=preference_data.source,
            confidence=preference_data.confidence,
        )
        
        db.add(preference)
        db.commit()
        db.refresh(preference)
        return preference
    
    @staticmethod
    def update_preference(
        db: Session,
        preference_id: UUID,
        preference_data: PreferenceUpdate,
        changed_by: Optional[str] = None
    ) -> Optional[Preference]:
        """Update a preference and create history record."""
        preference = PreferenceService.get_preference_by_id(db, preference_id)
        if not preference:
            return None
        
        # Store old value for history
        old_value = preference.value
        
        # Update preference
        update_data = preference_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "change_reason":
                setattr(preference, field, value)
        
        preference.version += 1
        preference.updated_at = datetime.utcnow()
        
        # Create history record
        history = PreferenceHistory(
            preference_id=preference.id,
            old_value=old_value,
            new_value=preference.value,
            change_reason=preference_data.change_reason or "user_update",
            changed_by=changed_by or "system",
        )
        db.add(history)
        
        db.commit()
        db.refresh(preference)
        return preference
    
    @staticmethod
    def get_preference_history(
        db: Session,
        preference_id: UUID,
        limit: int = 100
    ) -> List[PreferenceHistory]:
        """Get preference change history."""
        return db.query(PreferenceHistory).filter(
            PreferenceHistory.preference_id == preference_id
        ).order_by(
            PreferenceHistory.changed_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_all_categories(db: Session) -> List[PreferenceCategory]:
        """Get all preference categories."""
        return db.query(PreferenceCategory).all()
