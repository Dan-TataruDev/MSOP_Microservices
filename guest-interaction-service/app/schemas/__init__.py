"""
Pydantic schemas for API request/response validation.
"""
from app.schemas.guest import (
    GuestCreate,
    GuestUpdate,
    GuestResponse,
    GuestIdentityMappingCreate,
    GuestIdentityMappingResponse,
)
from app.schemas.preference import (
    PreferenceCreate,
    PreferenceUpdate,
    PreferenceResponse,
    PreferenceCategoryResponse,
    PreferenceHistoryResponse,
)
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionTypeResponse,
    InteractionFilter,
)
from app.schemas.personalization import (
    GuestSegmentResponse,
    BehaviorSignalResponse,
    PersonalizationContextResponse,
)

__all__ = [
    "GuestCreate",
    "GuestUpdate",
    "GuestResponse",
    "GuestIdentityMappingCreate",
    "GuestIdentityMappingResponse",
    "PreferenceCreate",
    "PreferenceUpdate",
    "PreferenceResponse",
    "PreferenceCategoryResponse",
    "PreferenceHistoryResponse",
    "InteractionCreate",
    "InteractionResponse",
    "InteractionTypeResponse",
    "InteractionFilter",
    "GuestSegmentResponse",
    "BehaviorSignalResponse",
    "PersonalizationContextResponse",
]
