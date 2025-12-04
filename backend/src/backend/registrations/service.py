"""Registration service for business logic."""

from datetime import datetime
from typing import List

from .repository import RegistrationRepository
from ..events.repository import EventRepository
from ..users.repository import UserRepository
from ..core.exceptions import (
    EntityNotFoundError,
    AlreadyRegisteredError,
    CapacityExceededError,
    BusinessRuleViolationError
)
from ..models.registration import Registration, RegistrationStatus


class RegistrationService:
    """Service for Registration business logic."""
    
    def __init__(
        self,
        registration_repository: RegistrationRepository,
        event_repository: EventRepository,
        user_repository: UserRepository
    ):
        """
        Initialize RegistrationService.
        
        Args:
            registration_repository: Registration repository instance
            event_repository: Event repository instance
            user_repository: User repository instance
        """
        self.registration_repository = registration_repository
        self.event_repository = event_repository
        self.user_repository = user_repository
    
    def register_user(self, user_id: str, event_id: str) -> Registration:
        """
        Register a user for an event.
        
        Args:
            user_id: User ID
            event_id: Event ID
            
        Returns:
            Created Registration object
            
        Raises:
            EntityNotFoundError: If event or user not found
            AlreadyRegisteredError: If user already registered or waitlisted
            CapacityExceededError: If event is full and has no waitlist
        """
        # Get event to check capacity and waitlist
        event = self.event_repository.get_by_id(event_id)
        if not event:
            raise EntityNotFoundError("Event", event_id)
        
        # Check if user exists
        if not self.user_repository.exists(user_id):
            raise EntityNotFoundError("User", user_id)
        
        # Check if already registered or waitlisted
        existing = self.registration_repository.get(event_id, user_id)
        if existing:
            if existing.status == 'registered':
                raise AlreadyRegisteredError(user_id, event_id, 'registered')
            elif existing.status == 'waitlisted':
                raise AlreadyRegisteredError(user_id, event_id, 'waitlisted')
        
        # Get current registration count
        registrations = self.registration_repository.list_by_event(event_id)
        registered_count = len([r for r in registrations if r.status == 'registered'])
        capacity = event.capacity
        has_waitlist = event.hasWaitlist
        
        # Determine status
        if registered_count < capacity:
            status = 'registered'
            waitlist_position = None
        elif has_waitlist:
            status = 'waitlisted'
            waitlist_count = len([r for r in registrations if r.status == 'waitlisted'])
            waitlist_position = waitlist_count + 1
        else:
            raise CapacityExceededError(event_id)
        
        # Create registration
        registration_data = {
            'PK': f"EVENT#{event_id}",
            'SK': f"USER#{user_id}",
            'userId': user_id,
            'eventId': event_id,
            'status': status,
            'registeredAt': datetime.utcnow().isoformat(),
            'waitlistPosition': waitlist_position
        }
        
        return self.registration_repository.create(registration_data)
    
    def unregister_user(self, user_id: str, event_id: str) -> None:
        """
        Unregister a user from an event.
        
        Args:
            user_id: User ID
            event_id: Event ID
            
        Raises:
            BusinessRuleViolationError: If user is not registered or waitlisted
        """
        # Check if registration exists
        registration = self.registration_repository.get(event_id, user_id)
        if not registration:
            raise BusinessRuleViolationError(
                f"User {user_id} is not registered or waitlisted for event {event_id}"
            )
        
        was_registered = registration.status == 'registered'
        
        # Delete the registration
        self.registration_repository.delete(event_id, user_id)
        
        # If user was registered and event has waitlist, promote first waitlisted user
        if was_registered:
            event = self.event_repository.get_by_id(event_id)
            if event and event.hasWaitlist:
                self.promote_from_waitlist(event_id)
    
    def get_event_registrations(self, event_id: str) -> RegistrationStatus:
        """
        Get registration status for an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            RegistrationStatus object
            
        Raises:
            EntityNotFoundError: If event not found
        """
        # Check if event exists
        event = self.event_repository.get_by_id(event_id)
        if not event:
            raise EntityNotFoundError("Event", event_id)
        
        registrations = self.registration_repository.list_by_event(event_id)
        
        registered_users = [r.userId for r in registrations if r.status == 'registered']
        waitlisted = [r for r in registrations if r.status == 'waitlisted']
        waitlisted.sort(key=lambda x: (x.waitlistPosition or 999, x.registeredAt))
        waitlist_users = [r.userId for r in waitlisted]
        
        return RegistrationStatus(
            eventId=event_id,
            registeredCount=len(registered_users),
            waitlistCount=len(waitlist_users),
            registeredUsers=registered_users,
            waitlistUsers=waitlist_users
        )
    
    def promote_from_waitlist(self, event_id: str) -> None:
        """
        Promote the first user from waitlist to registered.
        
        Args:
            event_id: Event ID
        """
        registrations = self.registration_repository.list_by_event(event_id)
        waitlisted = [r for r in registrations if r.status == 'waitlisted']
        
        if not waitlisted:
            return
        
        # Sort by waitlist position or registeredAt
        waitlisted.sort(key=lambda x: (x.waitlistPosition or 999, x.registeredAt))
        first_waitlisted = waitlisted[0]
        
        # Update status to registered
        self.registration_repository.update_status(
            event_id,
            first_waitlisted.userId,
            'registered',
            None
        )
