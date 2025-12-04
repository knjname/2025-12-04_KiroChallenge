"""User API handlers."""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from .service import UserService
from ..models.user import User, UserCreate
from ..models.event import Event
from ..core.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError
)


router = APIRouter(prefix="/users", tags=["users"])


def get_user_service() -> UserService:
    """Dependency to get UserService instance."""
    from ..core.config import Config
    from .repository import UserRepository
    
    config = Config()
    repository = UserRepository(config)
    return UserService(repository)


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    Create a new user.
    """
    try:
        user_data = user.model_dump()
        created_user = service.create_user(user_data)
        return created_user
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Get a specific user by ID.
    """
    try:
        user = service.get_user(user_id)
        return user
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@router.get("/{user_id}/registrations", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_user_registrations(user_id: str):
    """
    Get all events a user is registered for.
    
    This endpoint will be fully implemented after the registration service is created.
    """
    try:
        # Import here to avoid circular dependencies
        from ..core.config import Config
        from .repository import UserRepository
        from ..registrations.repository import RegistrationRepository
        from ..events.repository import EventRepository
        
        config = Config()
        user_repo = UserRepository(config)
        registration_repo = RegistrationRepository(config)
        event_repo = EventRepository(config)
        
        # Check if user exists
        user = user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Get user's registrations
        registrations = registration_repo.list_by_user(user_id)
        
        # Get full event details for each registration
        events = []
        for reg in registrations:
            if reg.status == 'registered':
                event = event_repo.get_by_id(reg.eventId)
                if event:
                    events.append(event)
        
        return events
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user registrations: {str(e)}"
        )
