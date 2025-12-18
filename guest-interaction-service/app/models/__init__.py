"""
Database models for the Guest Interaction Service.
"""
from app.models.guest import Guest, GuestIdentityMapping
from app.models.preference import Preference, PreferenceHistory, PreferenceCategory
from app.models.interaction import Interaction, InteractionType
from app.models.personalization import GuestSegment, BehaviorSignal, PersonalizationContext

__all__ = [
    "Guest",
    "GuestIdentityMapping",
    "Preference",
    "PreferenceHistory",
    "PreferenceCategory",
    "Interaction",
    "InteractionType",
    "GuestSegment",
    "BehaviorSignal",
    "PersonalizationContext",
]
