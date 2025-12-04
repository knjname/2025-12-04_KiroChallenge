"""User service for business logic."""

from typing import Dict, Any, List

from .repository import UserRepository
from ..core.exceptions import EntityNotFoundError
from ..models.user import User
from ..models.event import Event


class UserService:
    """Service for User business logic."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize UserService.
        
        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Created User object
            
        Raises:
            EntityAlreadyExistsError: If user with same ID already exists
        """
        return self.user_repository.create(user_data)
    
    def get_user(self, user_id: str) -> User:
        """
        Get a specific user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object
            
        Raises:
            EntityNotFoundError: If user not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        return user
    
    def get_user_registrations(self, user_id: str) -> List[Event]:
        """
        Get all events a user is registered for.
        
        This method requires access to registration and event repositories,
        which will be injected when called from the API layer.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Event objects
            
        Raises:
            EntityNotFoundError: If user not found
        """
        # Verify user exists
        user = self.get_user(user_id)
        
        # This will be implemented by injecting registration repository
        # For now, return empty list as placeholder
        # The actual implementation will be in the registrations service
        return []
