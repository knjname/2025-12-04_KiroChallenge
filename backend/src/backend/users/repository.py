"""User repository for database operations."""

from typing import Optional, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError

from ..core.config import Config
from ..core.exceptions import EntityAlreadyExistsError
from ..models.user import User


class UserRepository:
    """Repository for User entity database operations."""
    
    def __init__(self, config: Config):
        """
        Initialize UserRepository.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.table = config.get_table()
    
    def create(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Created User object
            
        Raises:
            EntityAlreadyExistsError: If user with same ID already exists
        """
        try:
            user_data['createdAt'] = datetime.utcnow().isoformat()
            user_data['PK'] = f"USER#{user_data['userId']}"
            user_data['SK'] = f"USER#{user_data['userId']}"
            
            self.table.put_item(
                Item=user_data,
                ConditionExpression='attribute_not_exists(PK)'
            )
            return User(**user_data)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise EntityAlreadyExistsError("User", user_data['userId'])
            raise
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"USER#{user_id}",
                    'SK': f"USER#{user_id}"
                }
            )
            item = response.get('Item')
            return User(**item) if item else None
        except ClientError:
            return None
    
    def exists(self, user_id: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user exists, False otherwise
        """
        return self.get_by_id(user_id) is not None
