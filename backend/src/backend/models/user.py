"""User domain models."""

from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    """Model for creating a new user."""
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)


class User(BaseModel):
    """Complete user model."""
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    createdAt: Optional[str] = None
