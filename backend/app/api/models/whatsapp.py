"""
WhatsApp Bot Pydantic Models

Request/Response models for WhatsApp API endpoints.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str = Field(..., description="Unique WhatsApp user identifier (phone number)")
    message: str = Field(default="", description="Text message from user")
    image: Optional[str] = Field(default=None, description="Base64 encoded image")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI generated response text")
    success: bool = Field(..., description="Whether the request was successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ClearSessionRequest(BaseModel):
    """Request model for clear session endpoint."""
    user_id: str = Field(..., description="Unique WhatsApp user identifier")


class ClearSessionResponse(BaseModel):
    """Response model for clear session endpoint."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(default="ok", description="Service status")
    active_sessions: int = Field(default=0, description="Number of active chat sessions")
