"""Event domain models."""

from pydantic import BaseModel, Field
from typing import Optional


class EventBase(BaseModel):
    """Base event model with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    location: str = Field(..., min_length=1, max_length=200)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., pattern=r'^(active|cancelled|completed)$')


class EventCreate(EventBase):
    """Model for creating a new event."""
    eventId: str = Field(..., min_length=1, max_length=100)
    hasWaitlist: bool = False


class EventUpdate(BaseModel):
    """Model for updating an existing event."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern=r'^(active|cancelled|completed)$')
    hasWaitlist: Optional[bool] = None


class Event(EventBase):
    """Complete event model."""
    eventId: str
    hasWaitlist: bool = False
