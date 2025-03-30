import os
import json
import logging
import google.generativeai as genai
from pydantic import BaseModel
import re
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class SQLResponse(BaseModel):
    sql_query: str
    explanation: str


def clean_string(response):
    """Extract the JSON part from a response string and convert it to a Python dictionary."""

    # Step 1: Extract JSON content using regex (handles cases with extra text)
    match = re.search(r"```json\s*([\s\S]*?)\s*```", response)

    if not match:
        raise ValueError("No valid JSON found in the response")

    cleaned_string = match.group(1).strip()  # Extracted JSON text

    # Step 2: Convert to JSON object safely
    try:
        data = json.loads(cleaned_string)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

    # Step 3: Normalize None values (both actual null and string "null")
    data = {
        key: None if value in (None, "null") else value
        for key, value in data.items()
    }

    return data


def validate_api_key(api_key):
    """Validate Gemini API key"""
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Please set the GEMINI_API_KEY environment variable."
        )
    if len(api_key) < 20:  # Gemini keys are typically longer
        raise ValueError(
            "API key appears to be incomplete. Please ensure you've copied the entire key."
        )


# Configure Gemini
try:
    validate_api_key(GEMINI_API_KEY)
    logger.info("API key validation passed")
    genai.configure(api_key=GEMINI_API_KEY)
except ValueError as e:
    raise ValueError(f"API Key Validation Error: {str(e)}")


def generate_sql_query(user_question):
    """
    Convert natural language question to SQL query using Gemini API.

    Args:
        user_question (str): Natural language question about sales data

    Returns:
        dict: Contains generated SQL query and explanation
    """
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

    try:
        logger.info(f"Generating SQL query for question: {user_question}")

        # Create the complete prompt
        prompt = f"{system_prompt}\n\nQuestion: {user_question}"

        # Log API request details
        logger.info(f"API request parameters: {prompt}")

        # Generate content using Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt,
                                          generation_config={
                                              "temperature": 0.3,
                                              "top_p": 0.8,
                                              "top_k": 40
                                          })

        logger.info("Received response from Gemini API")
        logger.info(f"Response content: {response.text}")

        # Parse the response as JSON
        cleaned_json = clean_string(response.text)
        print("CLEANED JSON:", cleaned_json)
        result = cleaned_json

        # Validate response format
        if not all(key in result for key in ["sql_query", "explanation"]):
            raise ValueError("Invalid response format from Gemini API")

        logger.info("Successfully generated SQL query")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
        raise Exception(f"Failed to parse Gemini response: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        error_msg = f"Failed to generate SQL query: {str(e)}"
        raise Exception(error_msg)
