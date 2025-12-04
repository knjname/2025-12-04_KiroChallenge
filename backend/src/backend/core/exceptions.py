"""
Custom domain exceptions for the Events API.

This module defines the exception hierarchy used throughout the application
to represent domain-specific error conditions.
"""


class DomainException(Exception):
    """Base exception for all domain errors."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found in the database."""
    
    def __init__(self, entity_type: str, entity_id: str):
        """
        Initialize EntityNotFoundError.
        
        Args:
            entity_type: The type of entity (e.g., "Event", "User")
            entity_id: The ID of the entity that was not found
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID {entity_id} not found")


class EntityAlreadyExistsError(DomainException):
    """Raised when attempting to create a duplicate entity."""
    
    def __init__(self, entity_type: str, entity_id: str):
        """
        Initialize EntityAlreadyExistsError.
        
        Args:
            entity_type: The type of entity (e.g., "Event", "User")
            entity_id: The ID of the entity that already exists
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID {entity_id} already exists")


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass


class CapacityExceededError(BusinessRuleViolationError):
    """Raised when event capacity is exceeded and no waitlist is available."""
    
    def __init__(self, event_id: str):
        """
        Initialize CapacityExceededError.
        
        Args:
            event_id: The ID of the event that is at capacity
        """
        self.event_id = event_id
        super().__init__(f"Event {event_id} is full and has no waitlist")


class AlreadyRegisteredError(BusinessRuleViolationError):
    """Raised when a user is already registered for an event."""
    
    def __init__(self, user_id: str, event_id: str, status: str = "registered"):
        """
        Initialize AlreadyRegisteredError.
        
        Args:
            user_id: The ID of the user
            event_id: The ID of the event
            status: The registration status ("registered" or "waitlisted")
        """
        self.user_id = user_id
        self.event_id = event_id
        self.status = status
        if status == "waitlisted":
            super().__init__(f"User {user_id} is already on the waitlist for event {event_id}")
        else:
            super().__init__(f"User {user_id} is already registered for event {event_id}")
