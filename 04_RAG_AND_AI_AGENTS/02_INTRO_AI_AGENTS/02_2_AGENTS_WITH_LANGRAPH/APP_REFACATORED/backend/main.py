# backend/main.py
"""FastAPI application entry point."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from core.config import settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Order System API",
        description="A conversational order system using LangGraph",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(router)
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.PORT,
        reload=settings.DEBUG
    )