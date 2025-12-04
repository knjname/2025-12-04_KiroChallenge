from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import List, Optional
from .models import (
    Event, EventCreate, EventUpdate,
    User, UserCreate,
    Registration, RegistrationRequest, RegistrationStatus
)
from .database import DynamoDBClient

app = FastAPI(
    title="Events API",
    description="REST API for managing events with DynamoDB",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DynamoDB client
db = DynamoDBClient()


@app.get("/events", response_model=List[Event], status_code=status.HTTP_200_OK)
async def list_events(status_filter: Optional[str] = Query(None, alias="status")):
    """
    List all events, optionally filtered by status
    """
    try:
        events = db.list_events(status=status_filter)
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve events: {str(e)}"
        )


@app.get("/events/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
async def get_event(event_id: str):
    """
    Get a specific event by ID
    """
    try:
        event = db.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve event: {str(e)}"
        )


@app.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    """
    Create a new event
    """
    try:
        event_data = event.model_dump()
        created_event = db.create_event(event_data)
        return created_event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@app.put("/events/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
async def update_event(event_id: str, event: EventUpdate):
    """
    Update an existing event
    """
    try:
        update_data = event.model_dump(exclude_unset=True)
        updated_event = db.update_event(event_id, update_data)
        
        if not updated_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        return updated_event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )


@app.delete("/events/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(event_id: str):
    """
    Delete an event
    """
    try:
        deleted = db.delete_event(event_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        return {"message": f"Event {event_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}"
        )


# Lambda handler
handler = Mangum(app)


# User endpoints
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user
    """
    try:
        user_data = user.model_dump()
        created_user = db.create_user(user_data)
        return created_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@app.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    """
    Get a specific user by ID
    """
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@app.get("/users/{user_id}/registrations", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_user_registrations(user_id: str):
    """
    Get all events a user is registered for
    """
    try:
        # Check if user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        events = db.get_user_registrations(user_id)
        return events
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user registrations: {str(e)}"
        )


# Registration endpoints
@app.post("/events/{event_id}/registrations", response_model=Registration, status_code=status.HTTP_200_OK)
async def register_for_event(event_id: str, request: RegistrationRequest):
    """
    Register a user for an event
    """
    try:
        registration = db.register_user(request.userId, event_id)
        return registration
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        elif "already registered" in error_msg or "already on the waitlist" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        elif "is full" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )


@app.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_200_OK)
async def unregister_from_event(event_id: str, user_id: str):
    """
    Unregister a user from an event
    """
    try:
        db.unregister_user(user_id, event_id)
        return {"message": f"User {user_id} unregistered from event {event_id} successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unregister user: {str(e)}"
        )


@app.get("/events/{event_id}/registrations", response_model=RegistrationStatus, status_code=status.HTTP_200_OK)
async def get_event_registrations(event_id: str):
    """
    Get registration status for an event
    """
    try:
        # Check if event exists
        event = db.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        registrations = db.get_event_registrations(event_id)
        
        registered_users = [r['userId'] for r in registrations if r['status'] == 'registered']
        waitlisted = [r for r in registrations if r['status'] == 'waitlisted']
        waitlisted.sort(key=lambda x: (x.get('waitlistPosition', 999), x.get('registeredAt', '')))
        waitlist_users = [r['userId'] for r in waitlisted]
        
        return RegistrationStatus(
            eventId=event_id,
            registeredCount=len(registered_users),
            waitlistCount=len(waitlist_users),
            registeredUsers=registered_users,
            waitlistUsers=waitlist_users
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve event registrations: {str(e)}"
        )
