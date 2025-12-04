"""Registration repository for database operations."""

from typing import List, Optional, Dict, Any
from botocore.exceptions import ClientError

from ..core.config import Config
from ..models.registration import Registration


class RegistrationRepository:
    """Repository for Registration entity database operations."""
    
    def __init__(self, config: Config):
        """
        Initialize RegistrationRepository.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.table = config.get_table()
    
    def create(self, registration_data: Dict[str, Any]) -> Registration:
        """
        Create a new registration.
        
        Args:
            registration_data: Registration data dictionary
            
        Returns:
            Created Registration object
        """
        self.table.put_item(Item=registration_data)
        return Registration(**registration_data)
    
    def get(self, event_id: str, user_id: str) -> Optional[Registration]:
        """
        Get a specific registration.
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Returns:
            Registration object if found, None otherwise
        """
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"USER#{user_id}"
                }
            )
            item = response.get('Item')
            return Registration(**item) if item else None
        except ClientError:
            return None
    
    def delete(self, event_id: str, user_id: str) -> bool:
        """
        Delete a registration.
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Returns:
            True if deleted successfully
        """
        self.table.delete_item(
            Key={
                'PK': f"EVENT#{event_id}",
                'SK': f"USER#{user_id}"
            }
        )
        return True
    
    def list_by_event(self, event_id: str) -> List[Registration]:
        """
        Get all registrations for an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            List of Registration objects
        """
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
                ExpressionAttributeValues={
                    ':pk': f"EVENT#{event_id}",
                    ':sk': 'USER#'
                }
            )
            items = response.get('Items', [])
            return [Registration(**item) for item in items]
        except ClientError:
            return []
    
    def list_by_user(self, user_id: str) -> List[Registration]:
        """
        Get all registrations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Registration objects
        """
        try:
            response = self.table.scan(
                FilterExpression='SK = :sk',
                ExpressionAttributeValues={
                    ':sk': f"USER#{user_id}"
                }
            )
            items = response.get('Items', [])
            # Filter to only include registration items (not user profile)
            registration_items = [item for item in items if item.get('PK', '').startswith('EVENT#')]
            return [Registration(**item) for item in registration_items]
        except ClientError:
            return []
    
    def update_status(self, event_id: str, user_id: str, status: str, waitlist_position: Optional[int] = None) -> None:
        """
        Update registration status.
        
        Args:
            event_id: Event ID
            user_id: User ID
            status: New status
            waitlist_position: New waitlist position (optional)
        """
        from datetime import datetime, UTC
        
        if waitlist_position is None:
            self.table.update_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"USER#{user_id}"
                },
                UpdateExpression='SET #status = :status, waitlistPosition = :null, promotedAt = :promoted',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':null': None,
                    ':promoted': datetime.now(UTC).isoformat()
                }
            )
        else:
            self.table.update_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"USER#{user_id}"
                },
                UpdateExpression='SET #status = :status, waitlistPosition = :position',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':position': waitlist_position
                }
            )
