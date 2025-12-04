"""Registration domain models."""

from pydantic import BaseModel, Field
from typing import Optional, List


class RegistrationRequest(BaseModel):
    """Model for registration request."""
    userId: str = Field(..., min_length=1, max_length=100)


class Registration(BaseModel):
    """Complete registration model."""
    userId: str
    eventId: str
    registeredAt: str
    status: str  # "registered" or "waitlisted"
    waitlistPosition: Optional[int] = None


class RegistrationStatus(BaseModel):
    """Model for event registration status."""
    eventId: str
    registeredCount: int
    waitlistCount: int
    registeredUsers: List[str] = []
    waitlistUsers: List[str] = []
