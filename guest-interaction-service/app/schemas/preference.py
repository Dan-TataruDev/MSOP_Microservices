"""
Pydantic schemas for preference-related APIs.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime
from uuid import UUID


class PreferenceCategoryResponse(BaseModel):
    """Schema for preference category response."""
    id: UUID
    name: str
    description: Optional[str]
    is_system: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PreferenceCreate(BaseModel):
    """Schema for creating a preference."""
    category_id: UUID
    key: str = Field(..., description="Preference key (e.g., 'dietary_restrictions', 'favorite_cuisine')")
    value: Any = Field(..., description="Preference value (can be string, array, boolean, number, or object)")
    value_type: str = Field(..., description="Type of value: string, array, boolean, number, object")
    source: str = Field(default="explicit", description="Source: explicit, implicit, inferred, system")
    confidence: int = Field(default=100, ge=0, le=100, description="Confidence score 0-100")


class PreferenceUpdate(BaseModel):
    """Schema for updating a preference."""
    value: Optional[Any] = None
    value_type: Optional[str] = None
    confidence: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    change_reason: Optional[str] = None


class PreferenceResponse(BaseModel):
    """Schema for preference response."""
    id: UUID
    guest_id: UUID
    category_id: UUID
    category: Optional[PreferenceCategoryResponse] = None
    key: str
    value: Any
    value_type: str
    source: str
    confidence: int
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PreferenceHistoryResponse(BaseModel):
    """Schema for preference history response."""
    id: UUID
    preference_id: UUID
    old_value: Optional[Any]
    new_value: Any
    change_reason: Optional[str]
    changed_at: datetime
    changed_by: Optional[str]
    
    class Config:
        from_attributes = True
