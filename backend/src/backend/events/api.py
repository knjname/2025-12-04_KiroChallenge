"""Event API handlers."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional

from .service import EventService
from ..models.event import Event, EventCreate, EventUpdate
from ..core.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    DomainException
)


router = APIRouter(prefix="/events", tags=["events"])


def get_event_service() -> EventService:
    """Dependency to get EventService instance."""
    from ..core.config import Config
    from .repository import EventRepository
    
    config = Config()
    repository = EventRepository(config)
    return EventService(repository)


@router.get("", response_model=List[Event], status_code=status.HTTP_200_OK)
async def list_events(
    status_filter: Optional[str] = Query(None, alias="status"),
    service: EventService = Depends(get_event_service)
):
    """
    List all events, optionally filtered by status.
    """
    try:
        events = service.list_events(status_filter)
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve events: {str(e)}"
        )


@router.get("/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
async def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """
    Get a specific event by ID.
    """
    try:
        event = service.get_event(event_id)
        return event
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve event: {str(e)}"
        )


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    service: EventService = Depends(get_event_service)
):
    """
    Create a new event.
    """
    try:
        event_data = event.model_dump()
        created_event = service.create_event(event_data)
        return created_event
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@router.put("/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
async def update_event(
    event_id: str,
    event: EventUpdate,
    service: EventService = Depends(get_event_service)
):
    """
    Update an existing event.
    """
    try:
        update_data = event.model_dump(exclude_unset=True)
        updated_event = service.update_event(event_id, update_data)
        return updated_event
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """
    Delete an event.
    """
    try:
        service.delete_event(event_id)
        return {"message": f"Event {event_id} deleted successfully"}
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}"
        )
