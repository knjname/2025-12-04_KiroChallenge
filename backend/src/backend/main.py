from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import List, Optional
from .models import Event, EventCreate, EventUpdate
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
