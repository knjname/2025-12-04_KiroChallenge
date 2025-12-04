# Implementation Plan

- [x] 1. Create new folder structure and core modules
  - Create domain folders: events/, users/, registrations/, models/, core/
  - Create __init__.py files for all new packages
  - _Requirements: 3.1, 3.3, 3.4, 3.5_

- [x] 1.1 Implement core exceptions module
  - Create core/exceptions.py with exception hierarchy
  - Implement DomainException, EntityNotFoundError, EntityAlreadyExistsError, BusinessRuleViolationError, CapacityExceededError, AlreadyRegisteredError
  - Add docstrings and type hints
  - _Requirements: 6.1, 6.2, 7.2, 7.3_

- [x] 1.2 Implement core configuration module
  - Create core/config.py for shared configuration
  - Implement Config class for DynamoDB table name and resource
  - _Requirements: 3.5, 7.2_

- [x] 2. Reorganize data models by domain
  - Split models.py into models/event.py, models/user.py, models/registration.py
  - Update models/__init__.py to export all models
  - Maintain all existing Pydantic model definitions unchanged
  - _Requirements: 3.4, 4.3, 7.4_

- [ ]* 2.1 Write unit tests for model organization
  - Verify all models are importable from new locations
  - Test that model validation still works correctly
  - _Requirements: 4.3, 4.5_

- [x] 3. Implement Event repository layer
  - Create events/repository.py with EventRepository class
  - Implement create, get_by_id, list_all, update, delete methods
  - Extract DynamoDB operations from database.py for events
  - Ensure methods return Event domain objects, not raw dicts
  - Handle DynamoDB ClientError and raise domain exceptions
  - _Requirements: 2.1, 2.2, 2.4, 2.5, 6.1, 7.2, 7.3_

- [ ]* 3.1 Write property test for Event repository type safety
  - **Property 1: Repository type safety**
  - **Validates: Requirements 2.4**
  - Generate random event data and verify repository methods return Event objects
  - _Requirements: 2.4_

- [ ]* 3.2 Write unit tests for Event repository
  - Test CRUD operations with mocked DynamoDB
  - Test exception raising for not found, already exists cases
  - _Requirements: 2.1, 2.2, 6.1_

- [x] 4. Implement Event service layer
  - Create events/service.py with EventService class
  - Implement create_event, get_event, list_events, update_event, delete_event methods
  - Move business logic from main.py event handlers to service
  - Inject EventRepository as dependency
  - Raise appropriate domain exceptions for business rule violations
  - _Requirements: 1.1, 1.4, 5.5, 6.2, 7.2, 7.3, 7.5_

- [ ]* 4.1 Write unit tests for Event service
  - Test business logic with mocked repository
  - Test exception handling and propagation
  - Verify service methods can be tested without HTTP layer
  - _Requirements: 1.3, 6.2_

- [x] 5. Implement Event API handlers
  - Create events/api.py with FastAPI router
  - Implement list_events, get_event, create_event, update_event, delete_event endpoints
  - Delegate all logic to EventService
  - Map domain exceptions to HTTP status codes
  - Ensure handlers only contain HTTP concerns
  - _Requirements: 1.1, 1.5, 5.1, 6.3, 7.2, 7.3_

- [ ]* 5.1 Write API tests for Event endpoints
  - Test HTTP request/response handling
  - Verify status code mapping for success and error cases
  - Test exception-to-HTTP mapping
  - _Requirements: 4.2, 6.3_

- [x] 6. Implement User repository layer
  - Create users/repository.py with UserRepository class
  - Implement create, get_by_id, exists methods
  - Extract DynamoDB operations from database.py for users
  - Ensure methods return User domain objects
  - Handle errors and raise domain exceptions
  - _Requirements: 2.1, 2.2, 2.4, 2.5, 6.1, 7.2, 7.3_

- [ ]* 6.1 Write unit tests for User repository
  - Test CRUD operations with mocked DynamoDB
  - Test exception raising for error cases
  - _Requirements: 2.1, 2.2, 6.1_

- [x] 7. Implement User service layer
  - Create users/service.py with UserService class
  - Implement create_user, get_user, get_user_registrations methods
  - Move business logic from main.py user handlers to service
  - Inject UserRepository and EventRepository as dependencies
  - _Requirements: 1.1, 1.4, 5.5, 6.2, 7.2, 7.3, 7.5_

- [ ]* 7.1 Write unit tests for User service
  - Test business logic with mocked repositories
  - Verify service testability without HTTP layer
  - _Requirements: 1.3, 6.2_

- [x] 8. Implement User API handlers
  - Create users/api.py with FastAPI router
  - Implement create_user, get_user, get_user_registrations endpoints
  - Delegate all logic to UserService
  - Map domain exceptions to HTTP status codes
  - _Requirements: 1.1, 1.5, 5.1, 6.3, 7.2, 7.3_

- [ ]* 8.1 Write API tests for User endpoints
  - Test HTTP handling and status codes
  - Verify exception-to-HTTP mapping
  - _Requirements: 4.2, 6.3_

- [x] 9. Implement Registration repository layer
  - Create registrations/repository.py with RegistrationRepository class
  - Implement create, get, delete, list_by_event, list_by_user, update_status methods
  - Extract DynamoDB operations from database.py for registrations
  - Ensure methods return Registration domain objects
  - _Requirements: 2.1, 2.2, 2.4, 2.5, 6.1, 7.2, 7.3_

- [ ]* 9.1 Write unit tests for Registration repository
  - Test CRUD operations with mocked DynamoDB
  - Test query operations for event and user lookups
  - _Requirements: 2.1, 2.2, 6.1_

- [x] 10. Implement Registration service layer
  - Create registrations/service.py with RegistrationService class
  - Implement register_user, unregister_user, get_event_registrations, promote_from_waitlist methods
  - Move complex business logic: capacity checks, waitlist management, promotion logic
  - Inject RegistrationRepository, EventRepository, UserRepository as dependencies
  - Raise appropriate exceptions for business rule violations
  - _Requirements: 1.1, 1.4, 4.4, 5.5, 6.2, 7.2, 7.3, 7.5_

- [ ]* 10.1 Write property test for business rule preservation
  - **Property 3: Business rule preservation**
  - **Validates: Requirements 4.4**
  - Generate random event capacities and registration sequences
  - Verify capacity limits and waitlist promotion work correctly
  - _Requirements: 4.4_

- [ ]* 10.2 Write unit tests for Registration service
  - Test registration logic with mocked repositories
  - Test waitlist promotion logic
  - Test capacity enforcement
  - Verify service testability without HTTP layer
  - _Requirements: 1.3, 4.4, 6.2_

- [x] 11. Implement Registration API handlers
  - Create registrations/api.py with FastAPI router
  - Implement register_for_event, unregister_from_event, get_event_registrations endpoints
  - Delegate all logic to RegistrationService
  - Map domain exceptions to HTTP status codes (404, 409, 422)
  - _Requirements: 1.1, 1.5, 5.1, 6.3, 7.2, 7.3_

- [ ]* 11.1 Write API tests for Registration endpoints
  - Test HTTP handling and status codes
  - Verify exception-to-HTTP mapping for all error cases
  - _Requirements: 4.2, 6.3_

- [x] 12. Update main application
  - Update main.py to initialize repositories and services
  - Register API routers from events, users, registrations modules
  - Remove old endpoint definitions
  - Configure dependency injection
  - Maintain CORS middleware configuration
  - Keep Lambda handler (Mangum)
  - _Requirements: 1.1, 5.5, 7.5_

- [x] 13. Remove old database.py module
  - Delete database.py as all operations are now in repositories
  - Verify no imports of database.py remain
  - _Requirements: 2.2, 2.3_

- [x] 14. Checkpoint - Run existing test suite
  - Run test_registration_api.py and test_local.py
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 4.5_

- [ ]* 14.1 Write property test for API behavioral equivalence
  - **Property 2: API behavioral equivalence**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.5**
  - Compare responses from refactored endpoints with expected behavior
  - Verify status codes, response bodies, and headers match
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 14.2 Write property test for exception handling consistency
  - **Property 4: Exception handling consistency**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
  - Generate various error conditions
  - Verify correct exception types at each layer
  - Validate HTTP status code mapping
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 15. Update imports and cleanup
  - Update all import statements to use new module structure
  - Remove any unused imports
  - Organize imports according to Python conventions (stdlib, third-party, local)
  - _Requirements: 7.4_

- [x] 16. Final checkpoint - Verify all functionality
  - Ensure all tests pass, ask the user if questions arise
  - Verify API endpoints work correctly
  - Check that error handling is consistent
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 6.4, 6.5_
