# Design Document: User Registration Feature

## Overview

The user-registration feature extends the existing Events API to support user management and event registration with capacity constraints and waitlist functionality. The system will manage user profiles, track event registrations, enforce capacity limits, and automatically handle waitlist promotion when spots become available.

The feature integrates with the existing FastAPI backend and DynamoDB infrastructure, adding new data models, API endpoints, and business logic for registration management.

## Architecture

### High-Level Architecture

The user-registration feature follows the existing three-tier architecture:

1. **API Layer (FastAPI)**: RESTful endpoints for user and registration operations
2. **Business Logic Layer**: Registration management, capacity enforcement, and waitlist handling
3. **Data Layer (DynamoDB)**: Persistent storage for users, registrations, and waitlist entries

### Integration Points

- Extends existing `backend/src/backend/main.py` with new endpoints
- Adds new models to `backend/src/backend/models.py`
- Extends `backend/src/backend/database.py` with new DynamoDB operations
- Leverages existing Event model and DynamoDB table structure

### Data Flow

```
Client Request → FastAPI Endpoint → Business Logic → DynamoDB Client → DynamoDB
                                         ↓
                                  Validation & Rules
                                  (Capacity, Waitlist)
```

## Components and Interfaces

### 1. User Management Component

**Responsibilities:**
- Create and store user profiles
- Validate user data
- Prevent duplicate user IDs

**Interfaces:**
```python
class UserManager:
    def create_user(user_id: str, name: str) -> User
    def get_user(user_id: str) -> Optional[User]
    def user_exists(user_id: str) -> bool
```

### 2. Registration Management Component

**Responsibilities:**
- Handle registration requests
- Enforce capacity constraints
- Manage waitlist operations
- Handle unregistration and waitlist promotion

**Interfaces:**
```python
class RegistrationManager:
    def register_user(user_id: str, event_id: str) -> RegistrationResult
    def unregister_user(user_id: str, event_id: str) -> UnregistrationResult
    def get_user_registrations(user_id: str) -> List[Event]
    def get_event_registrations(event_id: str) -> RegistrationStatus
```

### 3. Waitlist Management Component

**Responsibilities:**
- Add users to waitlist in order
- Promote users from waitlist when spots open
- Maintain waitlist ordering

**Interfaces:**
```python
class WaitlistManager:
    def add_to_waitlist(user_id: str, event_id: str) -> WaitlistEntry
    def remove_from_waitlist(user_id: str, event_id: str) -> bool
    def promote_from_waitlist(event_id: str) -> Optional[str]
    def get_waitlist_position(user_id: str, event_id: str) -> Optional[int]
```

### 4. API Endpoints

**User Endpoints:**
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user details
- `GET /users/{user_id}/registrations` - List user's registered events

**Registration Endpoints:**
- `POST /events/{event_id}/register` - Register user for an event
- `DELETE /events/{event_id}/register/{user_id}` - Unregister user from an event
- `GET /events/{event_id}/registrations` - Get event registration status

## Data Models

### User Model

```python
class User(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
```

### Registration Model

```python
class Registration(BaseModel):
    userId: str
    eventId: str
    registeredAt: str  # ISO 8601 timestamp
    status: str  # "registered" or "waitlisted"
```

### Event Model Extension

The existing Event model will be extended with:

```python
class EventWithRegistration(Event):
    hasWaitlist: bool = False
    registeredCount: int = 0
    waitlistCount: int = 0
```

### DynamoDB Schema

**Users Table:**
- Partition Key: `userId` (String)
- Attributes: `name`, `createdAt`

**Registrations Table:**
- Partition Key: `eventId` (String)
- Sort Key: `userId` (String)
- Attributes: `status`, `registeredAt`, `waitlistPosition`
- GSI: `userId-index` (for querying user's registrations)

Alternative: Use existing Events table with composite keys and GSI for efficient queries.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, the following redundancies were identified:
- Properties 1.4 and 1.5 are subsumed by 1.1 and 1.2 (data storage is verified through creation and uniqueness tests)
- Property 2.5 is subsumed by 2.2 and 2.3 (waitlist configuration is verified through behavior tests)
- Property 4.5 is subsumed by 4.2 (waitlist promotion inherently removes user from waitlist)
- Property 5.5 is subsumed by all other properties (real-time accuracy is verified through all registration operations)

The following properties provide unique validation value:

### User Management Properties

**Property 1: User creation round trip**
*For any* valid userId and name, creating a user and then retrieving that user should return the same userId and name.
**Validates: Requirements 1.1**

**Property 2: Duplicate user rejection**
*For any* userId, after creating a user with that userId, attempting to create another user with the same userId should be rejected with an error.
**Validates: Requirements 1.2**

**Property 3: Invalid user rejection**
*For any* user creation request missing required fields (userId or name), the system should reject the request with a validation error.
**Validates: Requirements 1.3**

### Capacity and Waitlist Properties

**Property 4: Capacity enforcement**
*For any* event with capacity N, after N users are registered, attempting to register an (N+1)th user should either be denied (no waitlist) or result in waitlist addition (with waitlist).
**Validates: Requirements 2.1**

**Property 5: Waitlist ordering**
*For any* event with waitlist enabled, when multiple users are added to the waitlist, they should be ordered by their registration attempt timestamp.
**Validates: Requirements 2.2**

**Property 6: No waitlist rejection**
*For any* event created without waitlist enabled, when the event is at full capacity, registration attempts should be rejected and not result in waitlist entries.
**Validates: Requirements 2.3**

**Property 7: Positive capacity validation**
*For any* event creation request, if the capacity is zero or negative, the system should reject the request with a validation error.
**Validates: Requirements 2.4**

### Registration Properties

**Property 8: Successful registration**
*For any* user and event where the event has available capacity, registering the user should result in the user appearing in the event's registered participants list.
**Validates: Requirements 3.1**

**Property 9: Full event rejection**
*For any* event at full capacity without a waitlist, registration attempts should be denied with an error indicating the event is full.
**Validates: Requirements 3.2**

**Property 10: Waitlist addition**
*For any* event at full capacity with a waitlist enabled, registration attempts should add the user to the waitlist in chronological order.
**Validates: Requirements 3.3**

**Property 11: Registration idempotence**
*For any* user already registered for an event, attempting to register again should be rejected.
**Validates: Requirements 3.4**

**Property 12: Waitlist idempotence**
*For any* user already on an event's waitlist, attempting to register again should be rejected.
**Validates: Requirements 3.5**

### Unregistration Properties

**Property 13: Unregistration removal**
*For any* registered user, unregistering from an event should remove the user from the registered participants list.
**Validates: Requirements 4.1**

**Property 14: Waitlist promotion**
*For any* event with a non-empty waitlist, when a registered user unregisters, the first user on the waitlist should be moved to the registered participants list and removed from the waitlist.
**Validates: Requirements 4.2**

**Property 15: Waitlist removal preserves order**
*For any* event with multiple users on the waitlist, removing a user from the waitlist should maintain the chronological order of the remaining waitlist entries.
**Validates: Requirements 4.3**

**Property 16: Invalid unregistration rejection**
*For any* user not registered for or waitlisted for an event, attempting to unregister should return an error.
**Validates: Requirements 4.4**

### Registration Listing Properties

**Property 17: Registration list completeness**
*For any* user registered for multiple events, querying their registrations should return all and only those events where the user is in the registered participants list.
**Validates: Requirements 5.1**

**Property 18: Waitlist exclusion from registration list**
*For any* user, querying their registered events should not include events where the user is only on the waitlist.
**Validates: Requirements 5.2**

**Property 19: Event details in registration list**
*For any* user's registered events, each returned event should contain at minimum the eventId field.
**Validates: Requirements 5.4**

## Error Handling

### Error Categories

1. **Validation Errors (400 Bad Request)**
   - Missing required fields (userId, name, eventId)
   - Invalid data formats
   - Negative or zero capacity

2. **Conflict Errors (409 Conflict)**
   - Duplicate userId on user creation
   - Duplicate registration attempt
   - Duplicate waitlist entry

3. **Not Found Errors (404 Not Found)**
   - User does not exist
   - Event does not exist
   - Registration does not exist for unregistration

4. **Business Logic Errors (422 Unprocessable Entity)**
   - Event is full (no waitlist)
   - Invalid unregistration (user not registered or waitlisted)

### Error Response Format

All errors should follow the existing FastAPI error format:

```json
{
  "detail": "Descriptive error message"
}
```

### Error Handling Strategy

- Validate input data before processing
- Check business rules (capacity, duplicates) before database operations
- Use atomic operations where possible to prevent race conditions
- Return specific error messages to aid debugging
- Log errors for monitoring and troubleshooting

## Testing Strategy

### Dual Testing Approach

The user-registration feature will employ both unit testing and property-based testing to ensure comprehensive coverage:

- **Unit tests** verify specific examples, edge cases, and error conditions
- **Property tests** verify universal properties that should hold across all inputs
- Together they provide comprehensive coverage: unit tests catch concrete bugs, property tests verify general correctness

### Property-Based Testing

**Framework:** Hypothesis (Python property-based testing library)

**Configuration:**
- Each property-based test will run a minimum of 100 iterations
- Each test will be tagged with a comment explicitly referencing the correctness property from this design document
- Tag format: `# Feature: user-registration, Property {number}: {property_text}`
- Each correctness property will be implemented by a SINGLE property-based test

**Test Generators:**
- `user_id_strategy`: Generate valid user IDs (1-100 characters)
- `name_strategy`: Generate valid names (1-200 characters)
- `event_id_strategy`: Generate valid event IDs
- `capacity_strategy`: Generate positive integers for event capacity
- `timestamp_strategy`: Generate ISO 8601 timestamps

**Property Test Coverage:**
- User creation and validation (Properties 1-3)
- Capacity enforcement (Properties 4, 7)
- Waitlist management (Properties 5, 6, 10, 12, 14, 15)
- Registration operations (Properties 8, 9, 11, 13, 16)
- Registration listing (Properties 17-19)

### Unit Testing

**Framework:** pytest

**Unit Test Coverage:**
- Specific examples of successful user creation
- Specific examples of successful registration
- Edge cases: empty waitlist, single-user waitlist, full capacity
- Integration between registration and waitlist components
- API endpoint request/response validation
- Database operation success and failure cases

**Test Organization:**
- `test_user_management.py`: User creation and retrieval tests
- `test_registration.py`: Registration and unregistration tests
- `test_waitlist.py`: Waitlist operations and promotion tests
- `test_api_endpoints.py`: API endpoint integration tests

### Test Data Management

- Use in-memory or local DynamoDB for testing
- Clean up test data after each test
- Use factories or fixtures for creating test users and events
- Ensure tests are isolated and can run in any order

### Continuous Testing

- Run unit tests on every commit
- Run property-based tests in CI/CD pipeline
- Monitor test coverage and aim for >90% code coverage
- Track property test failures to identify edge cases
