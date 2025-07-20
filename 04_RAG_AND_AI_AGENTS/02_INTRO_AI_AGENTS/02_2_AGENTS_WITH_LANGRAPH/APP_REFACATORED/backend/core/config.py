# backend/core/config.py
"""Application configuration."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # API Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # LLM Configuration
    GOOGLE_API_KEY: str = os.environ["GOOGLE_API_KEY"]
    LLM_MODEL: str = "gemini-2.0-flash"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_RETRIES: int = 5
    
    # Product Database
    PRODUCT_DB: Dict[str, Dict[str, Any]] = {
        "apple": {"name": "Apple", "price": 1.50, "in_stock": True},
        "orange": {"name": "Orange", "price": 2.00, "in_stock": True},
        "pineapple": {"name": "Pineapple", "price": 5.00, "in_stock": False},
        "banana": {"name": "Banana", "price": 1.00, "in_stock": True},
        "grape": {"name": "Grape", "price": 3.00, "in_stock": True},
        "milk": {"name": "Milk", "price": 2.50, "in_stock": True},
        "bread": {"name": "Bread", "price": 3.00, "in_stock": True}
    }


settings = Settings()