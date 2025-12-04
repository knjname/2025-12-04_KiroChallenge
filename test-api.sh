#!/bin/bash

API_URL="https://we903is324.execute-api.us-west-2.amazonaws.com/prod"

echo "=== Testing Events API ==="
echo ""

echo "1. GET /events (empty list)"
curl -s -X GET "$API_URL/events" | python3 -m json.tool
echo ""

echo "2. POST /events (create event)"
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-15",
    "eventId": "api-test-event-456",
    "organizer": "API Test Organizer",
    "description": "Testing API Gateway integration",
    "location": "API Test Location",
    "title": "API Gateway Test Event",
    "capacity": 200,
    "status": "active"
  }' | python3 -m json.tool
echo ""

echo "3. GET /events/{eventId}"
curl -s -X GET "$API_URL/events/api-test-event-456" | python3 -m json.tool
echo ""

echo "4. GET /events?status=active"
curl -s -X GET "$API_URL/events?status=active" | python3 -m json.tool
echo ""

echo "5. PUT /events/{eventId} (update event)"
curl -s -X PUT "$API_URL/events/api-test-event-456" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated API Gateway Test Event",
    "capacity": 250
  }' | python3 -m json.tool
echo ""

echo "6. DELETE /events/{eventId}"
curl -s -w "\nHTTP Status: %{http_code}\n" -X DELETE "$API_URL/events/api-test-event-456"
echo ""

echo "7. GET /events (verify deletion)"
curl -s -X GET "$API_URL/events" | python3 -m json.tool
echo ""

echo "=== All tests completed ==="
