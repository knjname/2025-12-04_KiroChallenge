from pydantic import BaseModel, Field
from typing import Optional, List


# User Models
class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)


class User(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    createdAt: Optional[str] = None


# Registration Models
class RegistrationRequest(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)


class Registration(BaseModel):
    userId: str
    eventId: str
    registeredAt: str
    status: str  # "registered" or "waitlisted"
    waitlistPosition: Optional[int] = None


class RegistrationStatus(BaseModel):
    eventId: str
    registeredCount: int
    waitlistCount: int
    registeredUsers: List[str] = []
    waitlistUsers: List[str] = []


# Event Models
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    location: str = Field(..., min_length=1, max_length=200)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., pattern=r'^(active|cancelled|completed)$')


class EventCreate(EventBase):
    eventId: str = Field(..., min_length=1, max_length=100)
    hasWaitlist: bool = False


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern=r'^(active|cancelled|completed)$')
    hasWaitlist: Optional[bool] = None


class Event(EventBase):
    eventId: str
    hasWaitlist: bool = False
