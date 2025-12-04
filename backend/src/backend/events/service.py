"""Event service for business logic."""

from typing import List, Optional, Dict, Any

from .repository import EventRepository
from ..core.exceptions import EntityNotFoundError
from ..models.event import Event


class EventService:
    """Service for Event business logic."""
    
    def __init__(self, event_repository: EventRepository):
        """
        Initialize EventService.
        
        Args:
            event_repository: Event repository instance
        """
        self.event_repository = event_repository
    
    def create_event(self, event_data: Dict[str, Any]) -> Event:
        """
        Create a new event.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Created Event object
            
        Raises:
            EntityAlreadyExistsError: If event with same ID already exists
        """
        return self.event_repository.create(event_data)
    
    def get_event(self, event_id: str) -> Event:
        """
        Get a specific event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Event object
            
        Raises:
            EntityNotFoundError: If event not found
        """
        event = self.event_repository.get_by_id(event_id)
        if not event:
            raise EntityNotFoundError("Event", event_id)
        return event
    
    def list_events(self, status_filter: Optional[str] = None) -> List[Event]:
        """
        List all events, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of Event objects
        """
        return self.event_repository.list_all(status_filter)
    
    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> Event:
        """
        Update an existing event.
        
        Args:
            event_id: Event ID
            update_data: Dictionary of fields to update
            
        Returns:
            Updated Event object
            
        Raises:
            EntityNotFoundError: If event not found
        """
        updated_event = self.event_repository.update(event_id, update_data)
        if not updated_event:
            raise EntityNotFoundError("Event", event_id)
        return updated_event
    
    def delete_event(self, event_id: str) -> None:
        """
        Delete an event.
        
        Args:
            event_id: Event ID
            
        Raises:
            EntityNotFoundError: If event not found
        """
        deleted = self.event_repository.delete(event_id)
        if not deleted:
            raise EntityNotFoundError("Event", event_id)
