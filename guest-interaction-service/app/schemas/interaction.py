"""
Pydantic schemas for interaction-related APIs.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime
from uuid import UUID


class InteractionTypeResponse(BaseModel):
    """Schema for interaction type response."""
    id: UUID
    name: str
    description: Optional[str]
    category: str
    is_system: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    """Schema for creating an interaction."""
    interaction_type_id: UUID
    entity_type: Optional[str] = Field(None, description="Type of entity: venue, product, booking, order, etc.")
    entity_id: Optional[str] = Field(None, description="ID of the interacted entity")
    context: Optional[dict] = Field(None, description="Additional context (search query, filters, etc.)")
    interaction_metadata: Optional[dict] = Field(None, description="Device info, session info, etc.")
    source: str = Field(default="frontend", description="Source: frontend, booking_service, order_service, etc.")
    source_event_id: Optional[str] = Field(None, description="ID of the event that triggered this interaction")
    occurred_at: Optional[datetime] = Field(None, description="When the interaction occurred (defaults to now)")


class InteractionResponse(BaseModel):
    """Schema for interaction response."""
    id: UUID
    guest_id: UUID
    interaction_type_id: UUID
    interaction_type: Optional[InteractionTypeResponse] = None
    entity_type: Optional[str]
    entity_id: Optional[str]
    context: Optional[dict]
    interaction_metadata: Optional[dict]
    source: str
    source_event_id: Optional[str]
    occurred_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class InteractionFilter(BaseModel):
    """Schema for filtering interactions."""
    interaction_type_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    source: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
