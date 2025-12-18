"""
Pydantic schemas for personalization-related APIs.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime
from uuid import UUID


class GuestSegmentResponse(BaseModel):
    """Schema for guest segment response."""
    id: UUID
    guest_id: UUID
    segment_name: str
    segment_category: Optional[str]
    confidence: float
    assigned_at: datetime
    assigned_by: str
    is_active: bool
    
    class Config:
        from_attributes = True


class BehaviorSignalResponse(BaseModel):
    """Schema for behavior signal response."""
    id: UUID
    guest_id: UUID
    signal_type: str
    signal_name: str
    signal_value: Any
    strength: float
    computed_at: datetime
    computed_by: str
    is_active: bool
    
    class Config:
        from_attributes = True


class PersonalizationContextResponse(BaseModel):
    """Schema for personalization context response."""
    id: UUID
    guest_id: UUID
    preference_vector: Optional[dict]
    behavior_summary: Optional[dict]
    segments: Optional[List[str]]
    signals: Optional[List[dict]]
    version: int
    computed_at: datetime
    computed_by: str
    
    class Config:
        from_attributes = True
