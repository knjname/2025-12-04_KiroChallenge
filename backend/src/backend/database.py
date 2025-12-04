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
            self.table.put_item(
                Item=event_data,
                ConditionExpression='attribute_not_exists(eventId)'
            )
            return event_data
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"Event with ID {event_data['eventId']} already exists")
            raise
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a single event by ID"""
        try:
            response = self.table.get_item(Key={'eventId': event_id})
            return response.get('Item')
        except ClientError:
            return None
    
    def list_events(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events, optionally filtered by status"""
        try:
            if status:
                response = self.table.scan(
                    FilterExpression='#status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': status}
                )
            else:
                response = self.table.scan()
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
                Key={'eventId': event_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ConditionExpression='attribute_exists(eventId)',
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
                Key={'eventId': event_id},
                ConditionExpression='attribute_exists(eventId)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise
