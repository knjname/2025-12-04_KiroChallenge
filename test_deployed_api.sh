#!/bin/bash

# Test the deployed registration API
API_URL="https://we903is324.execute-api.us-west-2.amazonaws.com/prod"

echo "=========================================="
echo "Testing Deployed User Registration API"
echo "=========================================="

# Generate unique IDs
TIMESTAMP=$(date +%s)
EVENT_ID="event-${TIMESTAMP}"
USER1_ID="user1-${TIMESTAMP}"
USER2_ID="user2-${TIMESTAMP}"
USER3_ID="user3-${TIMESTAMP}"

echo ""
echo "1. Creating event with waitlist..."
EVENT_RESPONSE=$(curl -s -X POST "${API_URL}/events" \
  -H "Content-Type: application/json" \
  -d "{
    \"eventId\": \"${EVENT_ID}\",
    \"title\": \"Test Conference\",
    \"description\": \"A test conference for registration\",
    \"date\": \"2025-12-15\",
    \"location\": \"Test City\",
    \"capacity\": 2,
    \"organizer\": \"Test Organizer\",
    \"status\": \"active\",
    \"hasWaitlist\": true
  }")
echo "Response: ${EVENT_RESPONSE}"

echo ""
echo "2. Creating users..."
curl -s -X POST "${API_URL}/users" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER1_ID}\", \"name\": \"Test User 1\"}"
echo ""

curl -s -X POST "${API_URL}/users" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER2_ID}\", \"name\": \"Test User 2\"}"
echo ""

curl -s -X POST "${API_URL}/users" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER3_ID}\", \"name\": \"Test User 3\"}"
echo ""

echo ""
echo "3. Registering first 2 users (filling capacity)..."
REG1=$(curl -s -X POST "${API_URL}/events/${EVENT_ID}/register" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER1_ID}\"}")
echo "User 1: ${REG1}"

REG2=$(curl -s -X POST "${API_URL}/events/${EVENT_ID}/register" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER2_ID}\"}")
echo "User 2: ${REG2}"

echo ""
echo "4. Checking event registrations..."
REG_STATUS=$(curl -s -X GET "${API_URL}/events/${EVENT_ID}/registrations")
echo "${REG_STATUS}"

echo ""
echo "5. Registering 3rd user (should go to waitlist)..."
REG3=$(curl -s -X POST "${API_URL}/events/${EVENT_ID}/register" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"${USER3_ID}\"}")
echo "${REG3}"

echo ""
echo "6. Checking event registrations after waitlist..."
REG_STATUS=$(curl -s -X GET "${API_URL}/events/${EVENT_ID}/registrations")
echo "${REG_STATUS}"

echo ""
echo "7. Unregistering first user (should promote from waitlist)..."
UNREG=$(curl -s -X DELETE "${API_URL}/events/${EVENT_ID}/register/${USER1_ID}")
echo "${UNREG}"

echo ""
echo "8. Checking final event registrations..."
REG_STATUS=$(curl -s -X GET "${API_URL}/events/${EVENT_ID}/registrations")
echo "${REG_STATUS}"

echo ""
echo "9. Checking user registrations..."
USER_REGS=$(curl -s -X GET "${API_URL}/users/${USER2_ID}/registrations")
echo "User 2 registrations: ${USER_REGS}"

echo ""
echo "=========================================="
echo "Test completed!"
echo "=========================================="
