# Events API Backend

A FastAPI-based REST API for managing events with DynamoDB storage, designed to run on AWS Lambda.

## Overview

This backend service provides a complete CRUD API for event management with the following features:

- RESTful API endpoints for events
- DynamoDB integration for data persistence
- AWS Lambda deployment support via Mangum
- Input validation with Pydantic models
- CORS support for frontend integration

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Boto3** - AWS SDK for Python
- **DynamoDB** - NoSQL database
- **Mangum** - AWS Lambda adapter for ASGI applications
- **Uvicorn** - ASGI server for local development

## Setup Instructions

### Prerequisites

- Python 3.13+
- AWS account with DynamoDB access
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository and navigate to the backend folder:**
   ```bash
   cd backend
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export EVENTS_TABLE_NAME=Events
   export AWS_REGION=us-east-1
   ```

   For local development with DynamoDB Local:
   ```bash
   export AWS_ENDPOINT_URL=http://localhost:8000
   ```

### Running Locally

Start the development server:

```bash
uv run uvicorn backend.main:app --reload
```

Or with standard Python:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### Interactive API Docs

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Code Documentation

Generated API documentation is available in the `docs/` folder. Open `docs/index.html` in your browser to view the complete code documentation.

## API Endpoints

### List Events
```http
GET /events
GET /events?status=active
```

Returns all events, optionally filtered by status (`active`, `cancelled`, or `completed`).

**Response:**
```json
[
  {
    "eventId": "event-001",
    "title": "Tech Conference 2025",
    "description": "Annual technology conference",
    "date": "2025-06-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "active"
  }
]
```

### Get Event
```http
GET /events/{event_id}
```

Retrieves a specific event by ID.

**Response:** Single event object (same structure as above)

### Create Event
```http
POST /events
Content-Type: application/json
```

**Request Body:**
```json
{
  "eventId": "event-001",
  "title": "Tech Conference 2025",
  "description": "Annual technology conference",
  "date": "2025-06-15",
  "location": "San Francisco, CA",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "active"
}
```

**Response:** Created event object with 201 status

### Update Event
```http
PUT /events/{event_id}
Content-Type: application/json
```

**Request Body:** (all fields optional)
```json
{
  "title": "Updated Title",
  "capacity": 600,
  "status": "completed"
}
```

**Response:** Updated event object

### Delete Event
```http
DELETE /events/{event_id}
```

**Response:**
```json
{
  "message": "Event event-001 deleted successfully"
}
```

## Data Models

### Event
- `eventId` (string, required): Unique identifier
- `title` (string, 1-200 chars): Event title
- `description` (string, 1-1000 chars): Event description
- `date` (string, YYYY-MM-DD format): Event date
- `location` (string, 1-200 chars): Event location
- `capacity` (integer, > 0): Maximum attendees
- `organizer` (string, 1-200 chars): Event organizer
- `status` (string): One of `active`, `cancelled`, or `completed`

## Project Structure

```
backend/
├── src/
│   └── backend/
│       ├── __init__.py
│       ├── main.py          # FastAPI application and endpoints
│       ├── models.py        # Pydantic data models
│       └── database.py      # DynamoDB client
├── docs/                    # Generated API documentation
├── pyproject.toml          # Project configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Deployment

This application is designed to run on AWS Lambda using the Mangum adapter. The `handler` function in `main.py` serves as the Lambda entry point.

### Environment Variables for Production

- `EVENTS_TABLE_NAME`: DynamoDB table name (default: "Events")
- `AWS_REGION`: AWS region for DynamoDB

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful GET, PUT, DELETE
- `201 Created`: Successful POST
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Resource already exists (duplicate eventId)
- `500 Internal Server Error`: Server-side error

Error responses include a detail message:
```json
{
  "detail": "Event with ID event-001 not found"
}
```

## Development

### Running Tests

```bash
# Add your test commands here
pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
