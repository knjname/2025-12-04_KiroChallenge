# Implementation Plan

- [ ] 1. Set up testing infrastructure
  - Install Hypothesis for property-based testing
  - Configure pytest for the project
  - Set up test database configuration (local DynamoDB or mocks)
  - Create test fixtures for users and events
  - _Requirements: All (testing foundation)_

- [ ] 2. Implement User data models and validation
- [ ] 2.1 Create User Pydantic models
  - Add User, UserCreate models to models.py
  - Implement validation for userId (1-100 chars) and name (1-200 chars)
  - _Requirements: 1.1, 1.3_

- [ ] 2.2 Write property test for user creation round trip
  - **Property 1: User creation round trip**
  - **Validates: Requirements 1.1**

- [ ] 2.3 Write property test for duplicate user rejection
  - **Property 2: Duplicate user rejection**
  - **Validates: Requirements 1.2**

- [ ] 2.4 Write property test for invalid user rejection
  - **Property 3: Invalid user rejection**
  - **Validates: Requirements 1.3**

- [ ] 3. Implement Registration and Waitlist data models
- [ ] 3.1 Create Registration and Waitlist Pydantic models
  - Add Registration, RegistrationStatus, WaitlistEntry models to models.py
  - Include fields: userId, eventId, registeredAt, status, waitlistPosition
  - _Requirements: 3.1, 3.3, 4.1_

- [ ] 3.2 Extend Event model with registration fields
  - Add hasWaitlist, registeredCount, waitlistCount to Event model
  - Ensure backward compatibility with existing Event endpoints
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 3.3 Write property test for positive capacity validation
  - **Property 7: Positive capacity validation**
  - **Validates: Requirements 2.4**

- [ ] 4. Implement DynamoDB operations for users
- [ ] 4.1 Add user table operations to database.py
  - Implement create_user, get_user, user_exists methods
  - Handle DynamoDB operations with proper error handling
  - Use existing Events table or create Users table
  - _Requirements: 1.1, 1.2_

- [ ]* 4.2 Write unit tests for user database operations
  - Test successful user creation
  - Test user retrieval
  - Test duplicate user handling
  - _Requirements: 1.1, 1.2_

- [ ] 5. Implement DynamoDB operations for registrations
- [ ] 5.1 Add registration table operations to database.py
  - Implement register_user, unregister_user, get_registrations methods
  - Design schema: eventId as partition key, userId as sort key
  - Create GSI for querying by userId
  - _Requirements: 3.1, 4.1, 5.1_

- [ ] 5.2 Add waitlist operations to database.py
  - Implement add_to_waitlist, remove_from_waitlist, get_waitlist methods
  - Maintain waitlist ordering using timestamps or position field
  - Implement promote_from_waitlist for automatic promotion
  - _Requirements: 3.3, 4.2, 4.3_

- [ ]* 5.3 Write unit tests for registration database operations
  - Test registration creation and retrieval
  - Test waitlist addition and ordering
  - Test waitlist promotion logic
  - _Requirements: 3.1, 3.3, 4.2_

- [ ] 6. Implement registration business logic
- [ ] 6.1 Create registration manager with capacity enforcement
  - Implement register_user method with capacity checking
  - Check if event is full before registration
  - Return appropriate errors for full events
  - _Requirements: 2.1, 3.1, 3.2_

- [ ]* 6.2 Write property test for capacity enforcement
  - **Property 4: Capacity enforcement**
  - **Validates: Requirements 2.1**

- [ ]* 6.3 Write property test for successful registration
  - **Property 8: Successful registration**
  - **Validates: Requirements 3.1**

- [ ]* 6.4 Write property test for full event rejection
  - **Property 9: Full event rejection**
  - **Validates: Requirements 3.2**

- [ ] 6.2 Add waitlist logic to registration manager
  - Check if event has waitlist enabled
  - Add user to waitlist when event is full and waitlist is enabled
  - Reject registration when event is full and no waitlist
  - _Requirements: 2.2, 2.3, 3.2, 3.3_

- [ ]* 6.6 Write property test for waitlist ordering
  - **Property 5: Waitlist ordering**
  - **Validates: Requirements 2.2**

- [ ]* 6.7 Write property test for no waitlist rejection
  - **Property 6: No waitlist rejection**
  - **Validates: Requirements 2.3**

- [ ]* 6.8 Write property test for waitlist addition
  - **Property 10: Waitlist addition**
  - **Validates: Requirements 3.3**

- [ ] 6.9 Implement duplicate registration prevention
  - Check if user is already registered before adding
  - Check if user is already on waitlist before adding
  - Return appropriate error for duplicate attempts
  - _Requirements: 3.4, 3.5_

- [ ]* 6.10 Write property test for registration idempotence
  - **Property 11: Registration idempotence**
  - **Validates: Requirements 3.4**

- [ ]* 6.11 Write property test for waitlist idempotence
  - **Property 12: Waitlist idempotence**
  - **Validates: Requirements 3.5**

- [ ] 7. Implement unregistration business logic
- [ ] 7.1 Create unregistration method with waitlist promotion
  - Implement unregister_user method
  - Remove user from registered participants
  - Automatically promote first waitlisted user when applicable
  - Handle unregistration from waitlist
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 7.2 Write property test for unregistration removal
  - **Property 13: Unregistration removal**
  - **Validates: Requirements 4.1**

- [ ]* 7.3 Write property test for waitlist promotion
  - **Property 14: Waitlist promotion**
  - **Validates: Requirements 4.2**

- [ ]* 7.4 Write property test for waitlist removal preserves order
  - **Property 15: Waitlist removal preserves order**
  - **Validates: Requirements 4.3**

- [ ] 7.5 Add validation for unregistration
  - Check if user is registered or waitlisted before unregistering
  - Return error for invalid unregistration attempts
  - _Requirements: 4.4_

- [ ]* 7.6 Write property test for invalid unregistration rejection
  - **Property 16: Invalid unregistration rejection**
  - **Validates: Requirements 4.4**

- [ ] 8. Implement user registration listing
- [ ] 8.1 Create method to get user's registered events
  - Query registrations by userId using GSI
  - Filter to only include registered status (not waitlisted)
  - Return full event details for each registration
  - Handle empty registration list
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 8.2 Write property test for registration list completeness
  - **Property 17: Registration list completeness**
  - **Validates: Requirements 5.1**

- [ ]* 8.3 Write property test for waitlist exclusion from registration list
  - **Property 18: Waitlist exclusion from registration list**
  - **Validates: Requirements 5.2**

- [ ]* 8.4 Write property test for event details in registration list
  - **Property 19: Event details in registration list**
  - **Validates: Requirements 5.4**

- [ ] 9. Create API endpoints for user management
- [ ] 9.1 Add POST /users endpoint
  - Accept userId and name in request body
  - Validate input using Pydantic models
  - Call user creation logic
  - Return 201 Created with user object or appropriate error
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 9.2 Add GET /users/{user_id} endpoint
  - Retrieve user by userId
  - Return 200 OK with user object or 404 Not Found
  - _Requirements: 1.1_

- [ ] 9.3 Add GET /users/{user_id}/registrations endpoint
  - Retrieve all registered events for a user
  - Return 200 OK with list of events
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 9.4 Write unit tests for user API endpoints
  - Test successful user creation
  - Test duplicate user error
  - Test user retrieval
  - Test registration listing
  - _Requirements: 1.1, 1.2, 5.1_

- [ ] 10. Create API endpoints for registration management
- [ ] 10.1 Add POST /events/{event_id}/register endpoint
  - Accept userId in request body
  - Validate user and event exist
  - Call registration logic with capacity and waitlist handling
  - Return 200 OK with registration status or appropriate error
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 10.2 Add DELETE /events/{event_id}/register/{user_id} endpoint
  - Validate user and event exist
  - Call unregistration logic with waitlist promotion
  - Return 200 OK with success message or appropriate error
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 10.3 Add GET /events/{event_id}/registrations endpoint
  - Return registration status including registered count, waitlist count
  - Optionally return list of registered users and waitlist
  - Return 200 OK with registration data
  - _Requirements: 2.1, 2.2_

- [ ]* 10.4 Write unit tests for registration API endpoints
  - Test successful registration
  - Test full event scenarios
  - Test waitlist addition
  - Test unregistration and promotion
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2_

- [ ] 11. Update Event endpoints to support waitlist configuration
- [ ] 11.1 Extend POST /events and PUT /events/{event_id} endpoints
  - Add hasWaitlist field to EventCreate and EventUpdate models
  - Ensure backward compatibility (default hasWaitlist to false)
  - Validate capacity is positive integer
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 11.2 Write unit tests for event waitlist configuration
  - Test event creation with waitlist enabled
  - Test event creation with waitlist disabled
  - Test capacity validation
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Add error handling and validation
- [ ] 13.1 Implement comprehensive error responses
  - Add specific error messages for all error cases
  - Use appropriate HTTP status codes (400, 404, 409, 422)
  - Ensure error format matches existing API pattern
  - _Requirements: All_

- [ ] 13.2 Add input validation middleware
  - Validate all request bodies against Pydantic models
  - Validate path parameters (userId, eventId)
  - Return 400 Bad Request for invalid input
  - _Requirements: 1.3, 2.4_

- [ ]* 13.3 Write unit tests for error handling
  - Test all error scenarios
  - Verify correct status codes and error messages
  - Test validation error responses
  - _Requirements: All_

- [ ] 14. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
