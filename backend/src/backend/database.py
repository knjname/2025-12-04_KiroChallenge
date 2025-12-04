import boto3
import os
from typing import List, Optional, Dict, Any
from botocore.exceptions import ClientError


class DynamoDBClient:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('EVENTS_TABLE_NAME', 'Events')
        self.table = self.dynamodb.Table(self.table_name)
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event"""
        try:
            # Add PK/SK for single-table design
            event_data['PK'] = f"EVENT#{event_data['eventId']}"
            event_data['SK'] = f"EVENT#{event_data['eventId']}"
            
            self.table.put_item(
                Item=event_data,
                ConditionExpression='attribute_not_exists(PK)'
            )
            return event_data
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"Event with ID {event_data['eventId']} already exists")
            raise
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a single event by ID"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"EVENT#{event_id}"
                }
            )
            return response.get('Item')
        except ClientError:
            return None
    
    def list_events(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events, optionally filtered by status"""
        try:
            if status:
                response = self.table.scan(
                    FilterExpression='begins_with(PK, :pk) AND begins_with(SK, :sk) AND #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':pk': 'EVENT#',
                        ':sk': 'EVENT#',
                        ':status': status
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
            return response.get('Items', [])
        except ClientError:
            return []
    
    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing event"""
        if not update_data:
            return self.get_event(event_id)
        
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
            return response.get('Attributes')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return None
            raise
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
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

    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            from datetime import datetime
            user_data['createdAt'] = datetime.utcnow().isoformat()
            user_data['PK'] = f"USER#{user_data['userId']}"
            user_data['SK'] = f"USER#{user_data['userId']}"
            
            self.table.put_item(
                Item=user_data,
                ConditionExpression='attribute_not_exists(PK)'
            )
            return user_data
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"User with ID {user_data['userId']} already exists")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"USER#{user_id}",
                    'SK': f"USER#{user_id}"
                }
            )
            return response.get('Item')
        except ClientError:
            return None
    
    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists"""
        return self.get_user(user_id) is not None
    
    # Registration operations
    def register_user(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Register a user for an event"""
        from datetime import datetime
        
        # Get event to check capacity and waitlist
        event = self.get_event(event_id)
        if not event:
            raise ValueError(f"Event with ID {event_id} not found")
        
        # Check if user exists
        if not self.user_exists(user_id):
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check if already registered or waitlisted
        existing = self.get_registration(event_id, user_id)
        if existing:
            if existing['status'] == 'registered':
                raise ValueError(f"User {user_id} is already registered for event {event_id}")
            elif existing['status'] == 'waitlisted':
                raise ValueError(f"User {user_id} is already on the waitlist for event {event_id}")
        
        # Get current registration count
        registrations = self.get_event_registrations(event_id)
        registered_count = len([r for r in registrations if r['status'] == 'registered'])
        capacity = event.get('capacity', 0)
        has_waitlist = event.get('hasWaitlist', False)
        
        # Determine status
        if registered_count < capacity:
            status = 'registered'
            waitlist_position = None
        elif has_waitlist:
            status = 'waitlisted'
            waitlist_count = len([r for r in registrations if r['status'] == 'waitlisted'])
            waitlist_position = waitlist_count + 1
        else:
            raise ValueError(f"Event {event_id} is full and has no waitlist")
        
        # Create registration
        registration = {
            'PK': f"EVENT#{event_id}",
            'SK': f"USER#{user_id}",
            'userId': user_id,
            'eventId': event_id,
            'status': status,
            'registeredAt': datetime.utcnow().isoformat(),
            'waitlistPosition': waitlist_position
        }
        
        self.table.put_item(Item=registration)
        return registration
    
    def unregister_user(self, user_id: str, event_id: str) -> bool:
        """Unregister a user from an event"""
        # Check if registration exists
        registration = self.get_registration(event_id, user_id)
        if not registration:
            raise ValueError(f"User {user_id} is not registered or waitlisted for event {event_id}")
        
        was_registered = registration['status'] == 'registered'
        
        # Delete the registration
        self.table.delete_item(
            Key={
                'PK': f"EVENT#{event_id}",
                'SK': f"USER#{user_id}"
            }
        )
        
        # If user was registered and event has waitlist, promote first waitlisted user
        if was_registered:
            event = self.get_event(event_id)
            if event and event.get('hasWaitlist', False):
                self._promote_from_waitlist(event_id)
        
        return True
    
    def get_registration(self, event_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific registration"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"USER#{user_id}"
                }
            )
            return response.get('Item')
        except ClientError:
            return None
    
    def get_event_registrations(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all registrations for an event"""
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
                ExpressionAttributeValues={
                    ':pk': f"EVENT#{event_id}",
                    ':sk': 'USER#'
                }
            )
            return response.get('Items', [])
        except ClientError:
            return []
    
    def get_user_registrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all events a user is registered for (not waitlisted)"""
        try:
            # Query using GSI (would need to be created in infrastructure)
            # For now, scan and filter
            response = self.table.scan(
                FilterExpression='SK = :sk AND #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':sk': f"USER#{user_id}",
                    ':status': 'registered'
                }
            )
            
            registrations = response.get('Items', [])
            
            # Get full event details for each registration
            events = []
            for reg in registrations:
                event = self.get_event(reg['eventId'])
                if event:
                    events.append(event)
            
            return events
        except ClientError:
            return []
    
    def _promote_from_waitlist(self, event_id: str):
        """Promote the first user from waitlist to registered"""
        registrations = self.get_event_registrations(event_id)
        waitlisted = [r for r in registrations if r['status'] == 'waitlisted']
        
        if not waitlisted:
            return
        
        # Sort by waitlist position or registeredAt
        waitlisted.sort(key=lambda x: (x.get('waitlistPosition', 999), x.get('registeredAt', '')))
        first_waitlisted = waitlisted[0]
        
        # Update status to registered
        from datetime import datetime
        self.table.update_item(
            Key={
                'PK': f"EVENT#{event_id}",
                'SK': f"USER#{first_waitlisted['userId']}"
            },
            UpdateExpression='SET #status = :status, waitlistPosition = :null, promotedAt = :promoted',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'registered',
                ':null': None,
                ':promoted': datetime.utcnow().isoformat()
            }
        )
