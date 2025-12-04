"""
Local test script that mocks DynamoDB for testing
"""
import sys
import os

# Mock boto3 before importing the app
# Singleton table to persist data across requests
_mock_table_instance = None

class MockTable:
    def __init__(self):
        self.items = {}
    
    def put_item(self, Item, **kwargs):
        key = (Item.get('PK'), Item.get('SK'))
        if 'ConditionExpression' in kwargs and 'attribute_not_exists' in kwargs['ConditionExpression']:
            if key in self.items:
                from botocore.exceptions import ClientError
                error_response = {'Error': {'Code': 'ConditionalCheckFailedException'}}
                raise ClientError(error_response, 'PutItem')
        self.items[key] = Item
        return Item
    
    def get_item(self, Key, **kwargs):
        key = (Key.get('PK'), Key.get('SK'))
        item = self.items.get(key)
        return {'Item': item} if item else {}
    
    def query(self, **kwargs):
        results = []
        pk = kwargs.get('ExpressionAttributeValues', {}).get(':pk')
        sk_prefix = kwargs.get('ExpressionAttributeValues', {}).get(':sk', '')
        
        for key, item in self.items.items():
            if item.get('PK') == pk:
                # Check if SK condition exists
                if 'begins_with(SK' in kwargs.get('KeyConditionExpression', ''):
                    if item.get('SK', '').startswith(sk_prefix):
                        results.append(item)
                else:
                    results.append(item)
        return {'Items': results}
    
    def scan(self, **kwargs):
        results = []
        filter_expr = kwargs.get('FilterExpression', '')
        expr_values = kwargs.get('ExpressionAttributeValues', {})
        expr_names = kwargs.get('ExpressionAttributeNames', {})
        
        for item in self.items.values():
            # Check filter conditions
            if 'begins_with(PK' in filter_expr and 'begins_with(SK' in filter_expr:
                # Filter for EVENT# items
                pk_prefix = expr_values.get(':pk', '')
                sk_prefix = expr_values.get(':sk', '')
                if item.get('PK', '').startswith(pk_prefix) and item.get('SK', '').startswith(sk_prefix):
                    # Check status filter if present
                    if '#status' in filter_expr:
                        status_value = expr_values.get(':status')
                        if item.get('status') == status_value:
                            results.append(item)
                    else:
                        results.append(item)
            elif 'SK = :sk' in filter_expr:
                # Filter for user registrations
                sk_value = expr_values.get(':sk')
                if item.get('SK') == sk_value:
                    results.append(item)
        
        return {'Items': results}
    
    def update_item(self, Key, **kwargs):
        key = (Key.get('PK'), Key.get('SK'))
        if key not in self.items:
            from botocore.exceptions import ClientError
            error_response = {'Error': {'Code': 'ConditionalCheckFailedException'}}
            raise ClientError(error_response, 'UpdateItem')
        
        item = self.items[key]
        # Simple update logic
        values = kwargs.get('ExpressionAttributeValues', {})
        names = kwargs.get('ExpressionAttributeNames', {})
        
        for k, v in values.items():
            field_name = k[1:]  # Remove the :
            # Handle attribute names
            for name_key, name_val in names.items():
                if name_key == f"#{field_name}":
                    field_name = name_val
                    break
            item[field_name] = v
        
        self.items[key] = item
        return {'Attributes': item}
    
    def delete_item(self, Key, **kwargs):
        key = (Key.get('PK'), Key.get('SK'))
        if key in self.items:
            del self.items[key]
            return True
        if 'ConditionExpression' in kwargs:
            from botocore.exceptions import ClientError
            error_response = {'Error': {'Code': 'ConditionalCheckFailedException'}}
            raise ClientError(error_response, 'DeleteItem')
        return False


class MockDynamoDB:
    def __init__(self):
        global _mock_table_instance
        if _mock_table_instance is None:
            _mock_table_instance = MockTable()
        self.table = _mock_table_instance
    
    def Table(self, name):
        return self.table


class MockBoto3:
    @staticmethod
    def resource(service_name):
        if service_name == 'dynamodb':
            return MockDynamoDB()
        return None


# Replace boto3
sys.modules['boto3'] = MockBoto3()

# Now import the app
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_registration_workflow():
    print("Testing User Registration Workflow")
    print("=" * 60)
    
    # 1. Create an event
    print("\n1. Creating event with waitlist...")
    event_response = client.post("/events", json={
        "eventId": "test-event-1",
        "title": "Test Conference",
        "description": "A test conference",
        "date": "2025-12-15",
        "location": "Test City",
        "capacity": 2,
        "organizer": "Test Org",
        "status": "active",
        "hasWaitlist": True
    })
    print(f"   Status: {event_response.status_code}")
    assert event_response.status_code == 201
    event = event_response.json()
    print(f"   Created: {event['eventId']}")
    
    # 2. Create users
    print("\n2. Creating users...")
    users = []
    for i in range(4):
        user_response = client.post("/users", json={
            "userId": f"user-{i}",
            "name": f"Test User {i}"
        })
        print(f"   User {i}: Status {user_response.status_code}")
        assert user_response.status_code == 201
        users.append(user_response.json()['userId'])
    
    # 3. Register first 2 users
    print("\n3. Registering first 2 users (filling capacity)...")
    for i in range(2):
        reg_response = client.post(f"/events/test-event-1/registrations", json={
            "userId": users[i]
        })
        print(f"   User {i}: Status {reg_response.status_code}")
        if reg_response.status_code != 200:
            print(f"   Error: {reg_response.json()}")
        assert reg_response.status_code == 200
        reg = reg_response.json()
        print(f"   Status: {reg['status']}")
        assert reg['status'] == 'registered'
    
    # 4. Check registrations
    print("\n4. Checking event registrations...")
    reg_status_response = client.get("/events/test-event-1/registrations")
    assert reg_status_response.status_code == 200
    reg_status = reg_status_response.json()
    print(f"   Registered: {reg_status['registeredCount']}")
    print(f"   Waitlist: {reg_status['waitlistCount']}")
    assert reg_status['registeredCount'] == 2
    assert reg_status['waitlistCount'] == 0
    
    # 5. Register 3rd user (should go to waitlist)
    print("\n5. Registering 3rd user (should go to waitlist)...")
    reg_response = client.post(f"/events/test-event-1/registrations", json={
        "userId": users[2]
    })
    print(f"   Status: {reg_response.status_code}")
    assert reg_response.status_code == 200
    reg = reg_response.json()
    print(f"   Status: {reg['status']}")
    print(f"   Waitlist position: {reg.get('waitlistPosition')}")
    assert reg['status'] == 'waitlisted'
    assert reg['waitlistPosition'] == 1
    
    # 6. Register 4th user (should also go to waitlist)
    print("\n6. Registering 4th user (should also go to waitlist)...")
    reg_response = client.post(f"/events/test-event-1/registrations", json={
        "userId": users[3]
    })
    print(f"   Status: {reg_response.status_code}")
    assert reg_response.status_code == 200
    reg = reg_response.json()
    print(f"   Status: {reg['status']}")
    print(f"   Waitlist position: {reg.get('waitlistPosition')}")
    assert reg['status'] == 'waitlisted'
    assert reg['waitlistPosition'] == 2
    
    # 7. Check registrations again
    print("\n7. Checking event registrations after waitlist...")
    reg_status_response = client.get("/events/test-event-1/registrations")
    assert reg_status_response.status_code == 200
    reg_status = reg_status_response.json()
    print(f"   Registered: {reg_status['registeredCount']}")
    print(f"   Waitlist: {reg_status['waitlistCount']}")
    assert reg_status['registeredCount'] == 2
    assert reg_status['waitlistCount'] == 2
    
    # 8. Unregister first user (should promote from waitlist)
    print("\n8. Unregistering first user (should promote from waitlist)...")
    unreg_response = client.delete(f"/events/test-event-1/registrations/{users[0]}")
    print(f"   Status: {unreg_response.status_code}")
    assert unreg_response.status_code == 200
    
    # 9. Check final registrations
    print("\n9. Checking final event registrations...")
    reg_status_response = client.get("/events/test-event-1/registrations")
    assert reg_status_response.status_code == 200
    reg_status = reg_status_response.json()
    print(f"   Registered: {reg_status['registeredCount']}")
    print(f"   Waitlist: {reg_status['waitlistCount']}")
    print(f"   Registered users: {reg_status['registeredUsers']}")
    print(f"   Waitlist users: {reg_status['waitlistUsers']}")
    assert reg_status['registeredCount'] == 2
    assert reg_status['waitlistCount'] == 1
    assert users[2] in reg_status['registeredUsers']  # Promoted from waitlist
    assert users[3] in reg_status['waitlistUsers']  # Still on waitlist
    
    # 10. Check user registrations
    print("\n10. Checking user registrations...")
    user_reg_response = client.get(f"/users/{users[1]}/registrations")
    assert user_reg_response.status_code == 200
    events = user_reg_response.json()
    print(f"   User 1: {len(events)} registered events")
    assert len(events) == 1
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_registration_workflow()
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
