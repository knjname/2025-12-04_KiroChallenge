"""Registration API handlers."""

from fastapi import APIRouter, HTTPException, status, Depends

from .service import RegistrationService
from ..models.registration import Registration, RegistrationRequest, RegistrationStatus
from ..core.exceptions import (
    EntityNotFoundError,
    AlreadyRegisteredError,
    CapacityExceededError,
    BusinessRuleViolationError
)


router = APIRouter(tags=["registrations"])


def get_registration_service() -> RegistrationService:
    """Dependency to get RegistrationService instance."""
    from ..core.config import Config
    from .repository import RegistrationRepository
    from ..events.repository import EventRepository
    from ..users.repository import UserRepository
    
    config = Config()
    registration_repo = RegistrationRepository(config)
    event_repo = EventRepository(config)
    user_repo = UserRepository(config)
    return RegistrationService(registration_repo, event_repo, user_repo)


@router.post("/events/{event_id}/registrations", response_model=Registration, status_code=status.HTTP_200_OK)
async def register_for_event(
    event_id: str,
    request: RegistrationRequest,
    service: RegistrationService = Depends(get_registration_service)
):
    """
    Register a user for an event.
    """
    try:
        registration = service.register_user(request.userId, event_id)
        return registration
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AlreadyRegisteredError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except CapacityExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )


@router.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_200_OK)
async def unregister_from_event(
    event_id: str,
    user_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """
    Unregister a user from an event.
    """
    try:
        service.unregister_user(user_id, event_id)
        return {"message": f"User {user_id} unregistered from event {event_id} successfully"}
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unregister user: {str(e)}"
        )


@router.get("/events/{event_id}/registrations", response_model=RegistrationStatus, status_code=status.HTTP_200_OK)
async def get_event_registrations(
    event_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """
    Get registration status for an event.
    """
    try:
        registration_status = service.get_event_registrations(event_id)
        return registration_status
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve event registrations: {str(e)}"
        )
