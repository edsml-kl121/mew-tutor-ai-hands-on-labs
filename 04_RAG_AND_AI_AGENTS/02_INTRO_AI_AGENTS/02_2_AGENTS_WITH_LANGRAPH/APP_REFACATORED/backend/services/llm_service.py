# backend/services/llm_service.py
"""LLM service for handling AI interactions."""

import json
import re
from typing import List, Union
from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import settings


class LLMService:
    """Service for handling LLM interactions."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=None,
            timeout=None,
            max_retries=settings.LLM_MAX_RETRIES,
            google_api_key=settings.GOOGLE_API_KEY
        )
    
    def route_query(self, query: str) -> str:
        """Determine if query is order-related or greeting."""
        prompt = f"""Analyze this user query and determine if it's related to ordering products or just greeting/irrelevant topics.

Query: "{query}"

Respond with either "order" or "greeting" only."""
        
        try:
            response = self.llm.invoke(prompt)
            route = response.content.strip().lower()
            return "order" if "order" in route else "greeting"
        except Exception:
            return "greeting"
    
    def handle_greeting(self, query: str) -> str:
        """Generate a greeting response."""
        prompt = f"""The user said: "{query}"

Provide a friendly response. If it's a greeting, greet them back and mention you can help with ordering products.
Keep it brief and helpful."""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception:
            return "Hello! I can help you order products. What would you like?"
    
    def extract_products(self, query: str) -> List[str]:
        """Extract product names from user query."""
        prompt = f"""User Query: "{query}"

Instructions:
- Identify all distinct product mentions from the user message
- Generate exactly one simple search term per item, staying close to user phrasing
- Focus on food items, groceries, or products that can be ordered
- Normalize to singular form (e.g., "apples" -> "apple")
- Return output as a JSON array of strings

Examples:
- "Do you have apples, oranges and pineapples?" -> ["apple", "orange", "pineapple"]
- "I want to buy bananas" -> ["banana"]
- "Can I order some milk and bread?" -> ["milk", "bread"]

Return only the JSON array, nothing else:"""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()
            
            if response_text.startswith('[') and response_text.endswith(']'):
                products = json.loads(response_text)
            else:
                json_match = re.search(r'\[.*?\]', response_text)
                if json_match:
                    products = json.loads(json_match.group())
                else:
                    products = []
            
            return products if isinstance(products, list) else []
        except Exception:
            return []
    
    def detect_order_intent(self, user_response: str) -> bool:
        """Detect if user wants to place an order."""
        intent_prompt = f"""User said: "{user_response}"

Analyze if the user wants to order/buy products or not. Consider responses in any language.
Look for:
- Positive intent (yes, want, buy, order, take, เอา, ซื้อ, ต้องการ, etc.)
- Negative intent (no, don't want, cancel, ไม่, ไม่เอา, etc.)

Respond with only "YES" if they want to order, or "NO" if they don't want to order."""
        
        try:
            intent_response = self.llm.invoke(intent_prompt)
            return "YES" in intent_response.content.strip().upper()
        except Exception:
            return False
    
    def extract_quantity(self, user_response: str) -> int:
        """Extract quantity from user response."""
        quantity_prompt = f"""User said: "{user_response}"

Extract any quantity/number mentioned. Look for:
- Numbers (1, 2, 3, สาม, etc.)
- Quantity words (one, two, หนึ่ง, สอง, สาม, etc.)

If a quantity is mentioned, respond with just the number (e.g., "3").
If no quantity mentioned, respond with "0"."""
        
        try:
            quantity_response = self.llm.invoke(quantity_prompt)
            return int(quantity_response.content.strip())
        except Exception:
            return 0


# Global LLM service instance
llm_service = LLMService()