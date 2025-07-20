# frontend/services/api_client.py
"""API client for backend communication."""

import requests
from typing import Optional, Dict, Any

# Backend URL
BACKEND_URL = "http://localhost:8000"


class APIResponse:
    """Response wrapper for API calls."""
    
    def __init__(self, success: bool, data: Dict[str, Any] = None, error: str = None):
        self.success = success
        self.data = data or {}
        self.error = error


class APIClient:
    """Client for communicating with the backend API."""
    
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url
    
    def start_conversation(self, user_query: str) -> APIResponse:
        """Start a new conversation."""
        try:
            response = requests.post(
                f"{self.base_url}/start-conversation",
                json={"user_query": user_query},
                timeout=30
            )
            
            if response.status_code == 200:
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(
                    success=False, 
                    error="Sorry, there was an error processing your request."
                )
        
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=f"Connection error: {str(e)}")
    
    def continue_conversation(
        self, 
        user_response: str, 
        thread_id: str, 
        current_state: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Continue an existing conversation."""
        try:
            payload = {
                "user_response": user_response,
                "thread_id": thread_id
            }
            
            if current_state:
                payload["current_state"] = current_state
            
            response = requests.post(
                f"{self.base_url}/continue-conversation",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(
                    success=False,
                    error="Sorry, there was an error processing your response."
                )
        
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=f"Connection error: {str(e)}")
    
    def check_health(self) -> bool:
        """Check if backend is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False


# Global API client instance
api_client = APIClient()


def check_backend_connection() -> bool:
    """Check backend connection status."""
    return api_client.check_health()