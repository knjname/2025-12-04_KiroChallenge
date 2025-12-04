# Design Document: Code Organization Refactoring

## Overview

This design document outlines the refactoring of the Events API backend from a monolithic structure to a layered, domain-driven architecture. The refactoring will separate concerns into distinct layers (API, Service, Repository) and organize code by domain (events, users, registrations) while maintaining complete backward compatibility with existing API endpoints.

The refactoring follows the principle of separation of concerns, where each layer has a single, well-defined responsibility:
- **API Layer**: Handles HTTP concerns (request/response, status codes, validation)
- **Service Layer**: Contains business logic and orchestrates operations
- **Repository Layer**: Encapsulates all database operations

## Architecture

### Current Architecture

```
backend/src/backend/
├── main.py (API handlers + business logic mixed)
├── database.py (DynamoDB operations)
└── models.py (Pydantic models)
```

Problems with current architecture:
- API handlers contain business logic (capacity checks, waitlist promotion)
- Database operations are tightly coupled with business logic
- Difficult to test business logic without HTTP layer
- No clear separation of concerns
- All code in a single flat structure

### Target Architecture

```
backend/src/backend/
├── main.py (FastAPI app initialization)
├── core/
│   ├── __init__.py
│   ├── config.py (Configuration management)
│   └── exceptions.py (Custom exceptions)
├── models/
│   ├── __init__.py
│   ├── event.py (Event models)
│   ├── user.py (User models)
│   └── registration.py (Registration models)
├── events/
│   ├── __init__.py
│   ├── api.py (Event API handlers)
│   ├── service.py (Event business logic)
│   └── repository.py (Event database operations)
├── users/
│   ├── __init__.py
│   ├── api.py (User API handlers)
│   ├── service.py (User business logic)
│   └── repository.py (User database operations)
└── registrations/
    ├── __init__.py
    ├── api.py (Registration API handlers)
    ├── service.py (Registration business logic)
    └── repository.py (Registration database operations)
```

### Layer Responsibilities

**API Layer (api.py files)**
- Receive and validate HTTP requests
- Call appropriate service methods
- Map service responses to HTTP responses
- Handle HTTP status codes
- Map exceptions to HTTP errors

**Service Layer (service.py files)**
- Implement business logic and domain rules
- Orchestrate operations across repositories
- Validate business constraints
- Raise domain-specific exceptions
- Return domain objects

**Repository Layer (repository.py files)**
- Execute database queries
- Map database records to domain objects
- Handle database-specific errors
- Encapsulate DynamoDB operations
- Provide clean data access interface

## Components and Interfaces

### Core Components

#### Configuration (core/config.py)
```python
class Config:
    table_name: str
    dynamodb_resource: boto3.resource
```

#### Custom Exceptions (core/exceptions.py)
```python
class DomainException(Exception): pass
class EntityNotFoundError(DomainException): pass
class EntityAlreadyExistsError(DomainException): pass
class BusinessRuleViolationError(DomainException): pass
class CapacityExceededError(BusinessRuleViolationError): pass
```

### Events Domain

#### EventRepository
```python
class EventRepository:
    def create(event_data: dict) -> Event
    def get_by_id(event_id: str) -> Optional[Event]
    def list_all(status_filter: Optional[str]) -> List[Event]
    def update(event_id: str, update_data: dict) -> Optional[Event]
    def delete(event_id: str) -> bool
```

#### EventService
```python
class EventService:
    def create_event(event_data: dict) -> Event
    def get_event(event_id: str) -> Event
    def list_events(status_filter: Optional[str]) -> List[Event]
    def update_event(event_id: str, update_data: dict) -> Event
    def delete_event(event_id: str) -> None
```

### Users Domain

#### UserRepository
```python
class UserRepository:
    def create(user_data: dict) -> User
    def get_by_id(user_id: str) -> Optional[User]
    def exists(user_id: str) -> bool
```

#### UserService
```python
class UserService:
    def create_user(user_data: dict) -> User
    def get_user(user_id: str) -> User
    def get_user_registrations(user_id: str) -> List[Event]
```

### Registrations Domain

#### RegistrationRepository
```python
class RegistrationRepository:
    def create(registration_data: dict) -> Registration
    def get(event_id: str, user_id: str) -> Optional[Registration]
    def delete(event_id: str, user_id: str) -> bool
    def list_by_event(event_id: str) -> List[Registration]
    def list_by_user(user_id: str) -> List[Registration]
    def update_status(event_id: str, user_id: str, status: str) -> None
```

#### RegistrationService
```python
class RegistrationService:
    def register_user(user_id: str, event_id: str) -> Registration
    def unregister_user(user_id: str, event_id: str) -> None
    def get_event_registrations(event_id: str) -> RegistrationStatus
    def promote_from_waitlist(event_id: str) -> None
```

## Data Models

Models will be reorganized into separate files by domain:

### models/event.py
- EventBase
- EventCreate
- EventUpdate
- Event

### models/user.py
- UserCreate
- User

### models/registration.py
- RegistrationRequest
- Registration
- RegistrationStatus

All models remain unchanged in structure, only relocated for better organization.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Repository type safety

*For any* repository method call, the returned value should be a properly typed domain object (Event, User, Registration) or a collection of domain objects, never raw database dictionaries.
**Validates: Requirements 2.4**

### Property 2: API behavioral equivalence

*For any* existing API endpoint and any valid request, the refactored system should return the same response body, status code, and headers as the original system.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 3: Business rule preservation

*For any* business operation (event creation, user registration, waitlist promotion), the refactored system should enforce the same business rules and constraints as the original system.
**Validates: Requirements 4.4**

### Property 4: Exception handling consistency

*For any* error condition, the system should raise domain-specific exceptions in repositories, propagate them through services, and map them to appropriate HTTP status codes in API handlers with consistent error message formats.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

## Error Handling

### Exception Hierarchy

```python
# core/exceptions.py
class DomainException(Exception):
    """Base exception for all domain errors"""
    pass

class EntityNotFoundError(DomainException):
    """Raised when an entity is not found"""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID {entity_id} not found")

class EntityAlreadyExistsError(DomainException):
    """Raised when attempting to create a duplicate entity"""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID {entity_id} already exists")

class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated"""
    pass

class CapacityExceededError(BusinessRuleViolationError):
    """Raised when event capacity is exceeded"""
    pass

class AlreadyRegisteredError(BusinessRuleViolationError):
    """Raised when user is already registered"""
    pass
```

### Exception-to-HTTP Mapping

API handlers will map exceptions to HTTP status codes:

- `EntityNotFoundError` → 404 Not Found
- `EntityAlreadyExistsError` → 409 Conflict
- `AlreadyRegisteredError` → 409 Conflict
- `CapacityExceededError` → 422 Unprocessable Entity
- `BusinessRuleViolationError` → 400 Bad Request
- `DomainException` → 400 Bad Request
- `Exception` → 500 Internal Server Error

### Error Response Format

All error responses will follow this format:
```json
{
    "detail": "Error message describing what went wrong"
}
```

This matches FastAPI's default HTTPException format, ensuring consistency.

## Testing Strategy

### Unit Testing

Unit tests will be written for each layer independently:

**Repository Tests**
- Test CRUD operations with mocked DynamoDB
- Verify correct exception raising for error conditions
- Validate that domain objects are returned (not raw dicts)
- Test query filtering and sorting logic

**Service Tests**
- Test business logic without database dependencies (mocked repositories)
- Verify business rule enforcement (capacity checks, waitlist logic)
- Test exception handling and propagation
- Validate orchestration of multiple repository calls

**API Tests**
- Test HTTP request/response handling
- Verify status code mapping
- Test request validation
- Verify exception-to-HTTP mapping

### Property-Based Testing

Property-based tests will verify universal properties using the Hypothesis library for Python:

**Property 1: Repository Type Safety**
- Generate random valid inputs for repository methods
- Verify all returned values are properly typed domain objects
- Check that no raw dictionaries are returned

**Property 2: API Behavioral Equivalence**
- Use existing API test suite as baseline
- Run tests against both original and refactored code
- Verify identical responses for all test cases

**Property 3: Business Rule Preservation**
- Generate random event capacities and registration sequences
- Verify capacity limits are enforced identically
- Test waitlist promotion logic produces same results

**Property 4: Exception Handling Consistency**
- Generate various error conditions
- Verify correct exception types are raised at each layer
- Validate HTTP status code mapping is consistent

### Integration Testing

Integration tests will verify the complete flow from API to database:
- Test complete request/response cycles
- Verify database state changes
- Test error scenarios end-to-end

### Testing Configuration

- Property-based tests will run a minimum of 100 iterations per property
- Each property-based test will include a comment referencing the design document property
- Format: `# Feature: code-organization, Property {number}: {property_text}`

## Implementation Strategy

### Phase 1: Create New Structure
1. Create new folder structure
2. Implement core exceptions
3. Create configuration module

### Phase 2: Extract Repositories
1. Create repository classes for each domain
2. Move database operations from DynamoDBClient to repositories
3. Ensure repositories return domain objects

### Phase 3: Extract Services
1. Create service classes for each domain
2. Move business logic from API handlers to services
3. Implement exception handling in services

### Phase 4: Refactor API Handlers
1. Update API handlers to use services
2. Implement exception-to-HTTP mapping
3. Remove business logic from handlers

### Phase 5: Reorganize Models
1. Split models.py into domain-specific files
2. Update imports across codebase

### Phase 6: Update Main Application
1. Update main.py to initialize and wire dependencies
2. Register API routers
3. Configure middleware

### Phase 7: Testing and Validation
1. Run existing test suite
2. Implement new unit tests for each layer
3. Implement property-based tests
4. Verify all tests pass

## Migration Path

The refactoring will be done incrementally to minimize risk:

1. **Parallel Implementation**: New structure will be built alongside existing code
2. **Gradual Migration**: Endpoints will be migrated one domain at a time (events → users → registrations)
3. **Continuous Testing**: Existing tests will run after each migration step
4. **Rollback Safety**: Old code will remain until all tests pass with new structure

## Dependencies

- **FastAPI**: Web framework (existing)
- **Pydantic**: Data validation (existing)
- **boto3**: AWS SDK (existing)
- **Hypothesis**: Property-based testing library (new)
- **pytest**: Testing framework (existing)

## Performance Considerations

The refactoring should not impact performance:
- Additional layer indirection is negligible (function calls)
- No additional database queries introduced
- Same DynamoDB operations, just reorganized
- Dependency injection overhead is minimal

## Security Considerations

Security posture remains unchanged:
- Same authentication/authorization mechanisms
- Same input validation (Pydantic models)
- Same database access patterns
- Exception handling prevents information leakage

## Backward Compatibility

Complete backward compatibility is maintained:
- All API endpoints remain unchanged
- Request/response schemas identical
- HTTP status codes preserved
- Error messages consistent
- Business logic behavior identical

This is a pure refactoring with no functional changes to the API contract.
