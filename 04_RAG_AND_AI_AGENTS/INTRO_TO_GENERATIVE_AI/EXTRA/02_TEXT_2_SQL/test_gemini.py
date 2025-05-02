import os
import logging
import google.generativeai as genai
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic model for SQL response
class SQLResponse(BaseModel):
    sql_query: str
    explanation: str


# Configure the API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Test prompt
system_prompt = """
You are a SQL expert. Convert the given natural language question into a SQL query.
The database has a 'sales' table with the following schema:
- id (INTEGER PRIMARY KEY)
- date (DATE)
- product_name (TEXT)
- quantity (INTEGER)
- unit_price (REAL)
- total_amount (REAL)

Respond with a JSON object containing:
{
    "sql_query": "your SQL query here",
    "explanation": "brief explanation of what the query does"
}
"""

test_question = "What is the total sales for each product?"

try:
    # Log available models
    logger.info("Listing available models:")
    for model in genai.list_models():
        logger.info(f"Model: {model.name}")

    # Generate content
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(
        f"{system_prompt}\n\nQuestion: {test_question}",
        generation_config={
            "temperature": 0.3,
            "top_p": 0.8,
            "top_k": 40
        })

    # Print raw response
    print("\nRaw response text:")
    print(response.text)

except Exception as e:
    logger.error(f"Error during test: {str(e)}")
    raise
