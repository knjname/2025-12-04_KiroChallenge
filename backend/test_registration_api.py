"""
Simple integration test for the registration API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_complete_registration_workflow():
    """Test the complete registration workflow"""
    print("=" * 60)
    print("Testing User Registration API")
    print("=" * 60)
    
    # 1. Create an event with waitlist
    print("\n1. Creating event with waitlist...")
    event_data = {
        "eventId": f"test-event-{datetime.now().timestamp()}",
        "title": "Test Conference",
        "description": "A test conference for registration",
        "date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "location": "Test City",
        "capacity": 2,
        "organizer": "Test Organizer",
        "status": "active",
        "hasWaitlist": True
    }
    
    response = requests.post(f"{BASE_URL}/events", json=event_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        event = response.json()
        print(f"Created event: {event['eventId']}")
        event_id = event['eventId']
    else:
        print(f"Error: {response.text}")
        return
    
    # 2. Create users
    print("\n2. Creating users...")
    users = []
    for i in range(4):
        user_data = {
            "userId": f"user-{i}-{datetime.now().timestamp()}",
            "name": f"Test User {i}"
        }
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        print(f"  User {i}: Status {response.status_code}")
        if response.status_code == 201:
            user = response.json()
            users.append(user['userId'])
            print(f"    Created: {user['userId']}")
    
    # 3. Register first 2 users (should fill capacity)
    print("\n3. Registering first 2 users (filling capacity)...")
    for i in range(2):
        response = requests.post(
            f"{BASE_URL}/events/{event_id}/register",
            json={"userId": users[i]}
        )
        print(f"  User {i}: Status {response.status_code}")
        if response.status_code == 200:
            reg = response.json()
            print(f"    Status: {reg['status']}")
    
    # 4. Check event registrations
    print("\n4. Checking event registrations...")
    response = requests.get(f"{BASE_URL}/events/{event_id}/registrations")
    if response.status_code == 200:
        reg_status = response.json()
        print(f"  Registered: {reg_status['registeredCount']}")
        print(f"  Waitlist: {reg_status['waitlistCount']}")
        print(f"  Registered users: {reg_status['registeredUsers']}")
    
    # 5. Register 3rd user (should go to waitlist)
    print("\n5. Registering 3rd user (should go to waitlist)...")
    response = requests.post(
        f"{BASE_URL}/events/{event_id}/register",
        json={"userId": users[2]}
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        reg = response.json()
        print(f"  Status: {reg['status']}")
        print(f"  Waitlist position: {reg.get('waitlistPosition')}")
    
    # 6. Try to register 4th user (should also go to waitlist)
    print("\n6. Registering 4th user (should also go to waitlist)...")
    response = requests.post(
        f"{BASE_URL}/events/{event_id}/register",
        json={"userId": users[3]}
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        reg = response.json()
        print(f"  Status: {reg['status']}")
        print(f"  Waitlist position: {reg.get('waitlistPosition')}")
    
    # 7. Check registrations again
    print("\n7. Checking event registrations after waitlist additions...")
    response = requests.get(f"{BASE_URL}/events/{event_id}/registrations")
    if response.status_code == 200:
        reg_status = response.json()
        print(f"  Registered: {reg_status['registeredCount']}")
        print(f"  Waitlist: {reg_status['waitlistCount']}")
        print(f"  Waitlist users: {reg_status['waitlistUsers']}")
    
    # 8. Unregister first user (should promote from waitlist)
    print("\n8. Unregistering first user (should promote from waitlist)...")
    response = requests.delete(f"{BASE_URL}/events/{event_id}/register/{users[0]}")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  {response.json()['message']}")
    
    # 9. Check final registrations
    print("\n9. Checking final event registrations...")
    response = requests.get(f"{BASE_URL}/events/{event_id}/registrations")
    if response.status_code == 200:
        reg_status = response.json()
        print(f"  Registered: {reg_status['registeredCount']}")
        print(f"  Waitlist: {reg_status['waitlistCount']}")
        print(f"  Registered users: {reg_status['registeredUsers']}")
        print(f"  Waitlist users: {reg_status['waitlistUsers']}")
    
    # 10. Check user registrations
    print("\n10. Checking user registrations...")
    for i, user_id in enumerate(users[:3]):
        response = requests.get(f"{BASE_URL}/users/{user_id}/registrations")
        if response.status_code == 200:
            events = response.json()
            print(f"  User {i}: {len(events)} registered events")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_complete_registration_workflow()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")
