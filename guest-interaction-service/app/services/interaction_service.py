"""
Interaction service - business logic for interaction history management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.interaction import Interaction, InteractionType
from app.schemas.interaction import InteractionCreate, InteractionFilter


class InteractionService:
    """Service for managing guest interactions."""
    
    @staticmethod
    def get_interaction_by_id(db: Session, interaction_id: UUID) -> Optional[Interaction]:
        """Get interaction by ID."""
        return db.query(Interaction).filter(Interaction.id == interaction_id).first()
    
    @staticmethod
    def create_interaction(
        db: Session,
        guest_id: UUID,
        interaction_data: InteractionCreate
    ) -> Interaction:
        """Create a new interaction record."""
        interaction = Interaction(
            guest_id=guest_id,
            interaction_type_id=interaction_data.interaction_type_id,
            entity_type=interaction_data.entity_type,
            entity_id=interaction_data.entity_id,
            context=interaction_data.context,
            interaction_metadata=interaction_data.interaction_metadata,
            source=interaction_data.source,
            source_event_id=interaction_data.source_event_id,
            occurred_at=interaction_data.occurred_at or datetime.utcnow(),
        )
        
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        # Update guest's last interaction timestamp
        from app.services.guest_service import GuestService
        GuestService.update_last_interaction(db, guest_id)
        
        return interaction
    
    @staticmethod
    def get_guest_interactions(
        db: Session,
        guest_id: UUID,
        filters: Optional[InteractionFilter] = None
    ) -> List[Interaction]:
        """Get interactions for a guest with optional filtering."""
        query = db.query(Interaction).filter(Interaction.guest_id == guest_id)
        
        if filters:
            if filters.interaction_type_id:
                query = query.filter(Interaction.interaction_type_id == filters.interaction_type_id)
            if filters.entity_type:
                query = query.filter(Interaction.entity_type == filters.entity_type)
            if filters.entity_id:
                query = query.filter(Interaction.entity_id == filters.entity_id)
            if filters.source:
                query = query.filter(Interaction.source == filters.source)
            if filters.start_date:
                query = query.filter(Interaction.occurred_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(Interaction.occurred_at <= filters.end_date)
        
        query = query.order_by(desc(Interaction.occurred_at))
        
        if filters:
            query = query.limit(filters.limit).offset(filters.offset)
        else:
            query = query.limit(100)
        
        return query.all()
    
    @staticmethod
    def get_all_interaction_types(db: Session) -> List[InteractionType]:
        """Get all interaction types."""
        return db.query(InteractionType).all()
    
    @staticmethod
    def get_interaction_type_by_name(db: Session, name: str) -> Optional[InteractionType]:
        """Get interaction type by name."""
        return db.query(InteractionType).filter(InteractionType.name == name).first()
