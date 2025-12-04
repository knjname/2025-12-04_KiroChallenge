"""Event repository for database operations."""

from typing import List, Optional, Dict, Any
from botocore.exceptions import ClientError

from ..core.config import Config
from ..core.exceptions import EntityNotFoundError, EntityAlreadyExistsError
from ..models.event import Event


class EventRepository:
    """Repository for Event entity database operations."""
    
    def __init__(self, config: Config):
        """
        Initialize EventRepository.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.table = config.get_table()
    
    def create(self, event_data: Dict[str, Any]) -> Event:
        """
        Create a new event.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Created Event object
            
        Raises:
            EntityAlreadyExistsError: If event with same ID already exists
        """
        try:
            # Add PK/SK for single-table design
            event_data['PK'] = f"EVENT#{event_data['eventId']}"
            event_data['SK'] = f"EVENT#{event_data['eventId']}"
            
            self.table.put_item(
                Item=event_data,
                ConditionExpression='attribute_not_exists(PK)'
            )
            return Event(**event_data)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise EntityAlreadyExistsError("Event", event_data['eventId'])
            raise
    
    def get_by_id(self, event_id: str) -> Optional[Event]:
        """
        Get a single event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Event object if found, None otherwise
        """
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"EVENT#{event_id}"
                }
            )
            item = response.get('Item')
            return Event(**item) if item else None
        except ClientError:
            return None
    
    def list_all(self, status_filter: Optional[str] = None) -> List[Event]:
        """
        List all events, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of Event objects
        """
        try:
            if status_filter:
                response = self.table.scan(
                    FilterExpression='begins_with(PK, :pk) AND begins_with(SK, :sk) AND #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':pk': 'EVENT#',
                        ':sk': 'EVENT#',
                        ':status': status_filter
                    }
                )
            else:
                response = self.table.scan(
                    FilterExpression='begins_with(PK, :pk) AND begins_with(SK, :sk)',
                    ExpressionAttributeValues={
                        ':pk': 'EVENT#',
                        ':sk': 'EVENT#'
                    }
                )
            items = response.get('Items', [])
            return [Event(**item) for item in items]
        except ClientError:
            return []
    
    def update(self, event_id: str, update_data: Dict[str, Any]) -> Optional[Event]:
        """
        Update an existing event.
        
        Args:
            event_id: Event ID
            update_data: Dictionary of fields to update
            
        Returns:
            Updated Event object if found, None otherwise
        """
        if not update_data:
            return self.get_by_id(event_id)
        
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        try:
            response = self.table.update_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"EVENT#{event_id}"
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ConditionExpression='attribute_exists(PK)',
                ReturnValues='ALL_NEW'
            )
            attributes = response.get('Attributes')
            return Event(**attributes) if attributes else None
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return None
            raise
    
    def delete(self, event_id: str) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.table.delete_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"EVENT#{event_id}"
                },
                ConditionExpression='attribute_exists(PK)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise
