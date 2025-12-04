"""
Events API - Main application entry point.

This module initializes the FastAPI application and registers all API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .events.api import router as events_router
from .users.api import router as users_router
from .registrations.api import router as registrations_router

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

# Register API routers
app.include_router(events_router)
app.include_router(users_router)
app.include_router(registrations_router)

# Lambda handler
handler = Mangum(app)
