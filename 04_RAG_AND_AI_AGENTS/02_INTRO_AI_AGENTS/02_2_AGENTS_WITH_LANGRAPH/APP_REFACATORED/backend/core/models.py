# backend/core/models.py
"""Pydantic models for API requests and responses."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class InitialQueryRequest(BaseModel):
    """Request model for starting a conversation."""
    user_query: str


class ContinueConversationRequest(BaseModel):
    """Request model for continuing a conversation."""
    user_response: str
    thread_id: str
    current_state: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Response model for conversation endpoints."""
    message: str
    thread_id: str
    is_complete: bool
    waiting_for_input: bool = False
    current_state: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str