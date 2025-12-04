# Requirements Document

## Introduction

The user-registration feature enables users to register for events with capacity management and waitlist functionality. The system manages user profiles, event registrations, and automatically handles capacity constraints including waitlist management when events reach full capacity.

## Glossary

- **Registration System**: The software system that manages user profiles and event registrations
- **User**: An individual with a unique identifier who can register for events
- **Event**: A scheduled occurrence with a defined capacity constraint
- **Capacity**: The maximum number of users that can be registered for an event
- **Waitlist**: An ordered list of users waiting for availability when an event is at full capacity
- **Registration**: The association between a user and an event indicating the user's participation
- **Full Event**: An event where the number of registered users equals the capacity

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to create users with basic information, so that individuals can be identified and tracked within the system.

#### Acceptance Criteria

1. WHEN a user creation request is received with a userId and name THEN the Registration System SHALL create a new user record with the provided information
2. WHEN a user creation request contains a userId that already exists THEN the Registration System SHALL reject the request and return an error
3. WHEN a user creation request is missing required fields THEN the Registration System SHALL reject the request and return a validation error
4. THE Registration System SHALL store the userId as a unique identifier for each user
5. THE Registration System SHALL store the name as a string field for each user

### Requirement 2

**User Story:** As an event organizer, I want to configure events with capacity constraints and optional waitlists, so that I can control attendance and manage overflow demand.

#### Acceptance Criteria

1. WHEN an event is created with a capacity value THEN the Registration System SHALL enforce that capacity as the maximum number of registered users
2. WHEN an event is created with a waitlist enabled THEN the Registration System SHALL maintain an ordered waitlist for that event
3. WHEN an event is created without a waitlist enabled THEN the Registration System SHALL not maintain a waitlist for that event
4. THE Registration System SHALL store the capacity as a positive integer for each event
5. THE Registration System SHALL store the waitlist configuration as a boolean flag for each event

### Requirement 3

**User Story:** As a user, I want to register for events, so that I can participate in activities that interest me.

#### Acceptance Criteria

1. WHEN a user attempts to register for an event that is not full THEN the Registration System SHALL add the user to the registered participants list
2. WHEN a user attempts to register for an event that is full and has no waitlist THEN the Registration System SHALL deny the registration and return an error indicating the event is full
3. WHEN a user attempts to register for an event that is full and has a waitlist THEN the Registration System SHALL add the user to the waitlist in order of registration attempt
4. WHEN a user attempts to register for an event they are already registered for THEN the Registration System SHALL reject the duplicate registration
5. WHEN a user attempts to register for an event they are already on the waitlist for THEN the Registration System SHALL reject the duplicate waitlist entry

### Requirement 4

**User Story:** As a user, I want to unregister from events, so that I can free up my spot if my plans change.

#### Acceptance Criteria

1. WHEN a registered user unregisters from an event THEN the Registration System SHALL remove the user from the registered participants list
2. WHEN a registered user unregisters from an event with a waitlist THEN the Registration System SHALL move the first user from the waitlist to the registered participants list
3. WHEN a user on the waitlist unregisters THEN the Registration System SHALL remove the user from the waitlist and maintain the order of remaining waitlist entries
4. WHEN a user attempts to unregister from an event they are not registered for or on the waitlist for THEN the Registration System SHALL return an error
5. WHEN the last waitlisted user is promoted to registered status THEN the Registration System SHALL remove that user from the waitlist

### Requirement 5

**User Story:** As a user, I want to list all events I am registered for, so that I can keep track of my commitments.

#### Acceptance Criteria

1. WHEN a user requests their registered events THEN the Registration System SHALL return all events where the user is in the registered participants list
2. WHEN a user requests their registered events THEN the Registration System SHALL not include events where the user is only on the waitlist
3. WHEN a user has no registered events THEN the Registration System SHALL return an empty list
4. THE Registration System SHALL return event details including eventId for each registered event
5. THE Registration System SHALL maintain accurate registration status in real-time as registrations and unregistrations occur
