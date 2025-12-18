"""
Pydantic schemas for guest-related APIs.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class GuestCreate(BaseModel):
    """Schema for creating a new guest profile."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    is_anonymous: bool = False
    consent_marketing: bool = False
    consent_analytics: bool = True
    consent_personalization: bool = True


class GuestUpdate(BaseModel):
    """Schema for updating guest profile."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    consent_marketing: Optional[bool] = None
    consent_analytics: Optional[bool] = None
    consent_personalization: Optional[bool] = None


class GuestResponse(BaseModel):
    """Schema for guest profile response."""
    id: UUID
    email: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    status: str
    is_anonymous: bool
    consent_marketing: bool
    consent_analytics: bool
    consent_personalization: bool
    created_at: datetime
    updated_at: datetime
    last_interaction_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GuestIdentityMappingCreate(BaseModel):
    """Schema for creating identity mapping."""
    identity_type: str = Field(..., description="Type of identity: session_id, device_id, auth_user_id, email")
    identity_value: str = Field(..., description="The identity value")
    is_primary: bool = False


class GuestIdentityMappingResponse(BaseModel):
    """Schema for identity mapping response."""
    id: UUID
    guest_id: UUID
    identity_type: str
    identity_value: str
    is_primary: bool
    created_at: datetime
    last_used_at: datetime
    
    class Config:
        from_attributes = True


class GuestDataExport(BaseModel):
    """Schema for GDPR data export."""
    guest: GuestResponse
    preferences: List[dict]
    interactions: List[dict]
    segments: List[dict]
    behavior_signals: List[dict]
    exported_at: datetime
