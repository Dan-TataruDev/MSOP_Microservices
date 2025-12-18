"""
Guest service - business logic for guest profile management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from app.models.guest import Guest, GuestIdentityMapping
from app.schemas.guest import GuestCreate, GuestUpdate, GuestResponse, GuestIdentityMappingCreate
from app.config import settings


class GuestService:
    """Service for managing guest profiles and identity."""
    
    @staticmethod
    def get_guest_by_id(db: Session, guest_id: UUID) -> Optional[Guest]:
        """Get guest by ID."""
        return db.query(Guest).filter(Guest.id == guest_id).first()
    
    @staticmethod
    def get_guest_by_email(db: Session, email: str) -> Optional[Guest]:
        """Get guest by email."""
        return db.query(Guest).filter(Guest.email == email).first()
    
    @staticmethod
    def find_guest_by_identity(
        db: Session, 
        identity_type: str, 
        identity_value: str
    ) -> Optional[Guest]:
        """Find guest by identity mapping."""
        mapping = db.query(GuestIdentityMapping).filter(
            and_(
                GuestIdentityMapping.identity_type == identity_type,
                GuestIdentityMapping.identity_value == identity_value
            )
        ).first()
        
        if mapping:
            return db.query(Guest).filter(Guest.id == mapping.guest_id).first()
        return None
    
    @staticmethod
    def create_guest(db: Session, guest_data: GuestCreate) -> Guest:
        """Create a new guest profile."""
        guest = Guest(
            email=guest_data.email,
            name=guest_data.name,
            phone=guest_data.phone,
            is_anonymous=guest_data.is_anonymous,
            consent_marketing=guest_data.consent_marketing,
            consent_analytics=guest_data.consent_analytics,
            consent_personalization=guest_data.consent_personalization,
            status="active",
        )
        
        # Set data retention date if configured
        if settings.data_retention_days > 0:
            guest.data_retention_until = datetime.utcnow() + timedelta(
                days=settings.data_retention_days
            )
        
        db.add(guest)
        db.commit()
        db.refresh(guest)
        return guest
    
    @staticmethod
    def update_guest(db: Session, guest_id: UUID, guest_data: GuestUpdate) -> Optional[Guest]:
        """Update guest profile."""
        guest = GuestService.get_guest_by_id(db, guest_id)
        if not guest:
            return None
        
        update_data = guest_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(guest, field, value)
        
        guest.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(guest)
        return guest
    
    @staticmethod
    def add_identity_mapping(
        db: Session,
        guest_id: UUID,
        mapping_data: GuestIdentityMappingCreate
    ) -> GuestIdentityMapping:
        """Add or update identity mapping for a guest."""
        # Check if mapping already exists
        existing = db.query(GuestIdentityMapping).filter(
            and_(
                GuestIdentityMapping.identity_type == mapping_data.identity_type,
                GuestIdentityMapping.identity_value == mapping_data.identity_value
            )
        ).first()
        
        if existing:
            # Update existing mapping
            existing.guest_id = guest_id
            existing.last_used_at = datetime.utcnow()
            if mapping_data.is_primary:
                existing.is_primary = True
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new mapping
        mapping = GuestIdentityMapping(
            guest_id=guest_id,
            identity_type=mapping_data.identity_type,
            identity_value=mapping_data.identity_value,
            is_primary=mapping_data.is_primary,
        )
        
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        return mapping
    
    @staticmethod
    def merge_guests(db: Session, primary_guest_id: UUID, secondary_guest_id: UUID) -> Guest:
        """Merge two guest profiles (for identity resolution)."""
        primary_guest = GuestService.get_guest_by_id(db, primary_guest_id)
        secondary_guest = GuestService.get_guest_by_id(db, secondary_guest_id)
        
        if not primary_guest or not secondary_guest:
            raise ValueError("One or both guests not found")
        
        # Transfer preferences, interactions, etc. to primary guest
        # (This would be implemented based on business rules)
        
        # Update secondary guest status
        secondary_guest.status = "merged"
        secondary_guest.updated_at = datetime.utcnow()
        
        # Update primary guest's last interaction
        if secondary_guest.last_interaction_at:
            if not primary_guest.last_interaction_at or \
               secondary_guest.last_interaction_at > primary_guest.last_interaction_at:
                primary_guest.last_interaction_at = secondary_guest.last_interaction_at
        
        db.commit()
        db.refresh(primary_guest)
        return primary_guest
    
    @staticmethod
    def anonymize_guest(db: Session, guest_id: UUID) -> Optional[Guest]:
        """Anonymize guest data for GDPR compliance."""
        guest = GuestService.get_guest_by_id(db, guest_id)
        if not guest:
            return None
        
        # Anonymize personal data
        guest.email = None
        guest.name = None
        guest.phone = None
        guest.status = "anonymized"
        guest.is_anonymous = True
        guest.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(guest)
        return guest
    
    @staticmethod
    def delete_guest(db: Session, guest_id: UUID) -> bool:
        """Delete guest and all related data (GDPR right to erasure)."""
        guest = GuestService.get_guest_by_id(db, guest_id)
        if not guest:
            return False
        
        # Cascade delete will handle related records
        db.delete(guest)
        db.commit()
        return True
    
    @staticmethod
    def update_last_interaction(db: Session, guest_id: UUID) -> None:
        """Update guest's last interaction timestamp."""
        guest = GuestService.get_guest_by_id(db, guest_id)
        if guest:
            guest.last_interaction_at = datetime.utcnow()
            db.commit()
