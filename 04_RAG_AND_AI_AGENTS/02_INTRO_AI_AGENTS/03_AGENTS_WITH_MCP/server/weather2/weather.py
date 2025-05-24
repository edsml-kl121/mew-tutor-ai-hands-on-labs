from typing import Any
import httpx
import sys
import logging
from mcp.server.fastmcp import FastMCP

# Set up logging to stderr to help with debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("weather-mcp")

# Log startup information
logger.info("Starting Weather MCP Server")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {sys.path}")

# Initialize FastMCP server
try:
    mcp = FastMCP("weather")
    logger.info("FastMCP initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize FastMCP: {str(e)}")
    sys.exit(1)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    logger.debug(f"Making request to: {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            logger.debug("Request successful")
            return data
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {str(e)}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during API request: {str(e)}")
        return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    logger.info(f"Getting alerts for state: {state}")
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        logger.warning("No alert data found or invalid response")
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        logger.info(f"No active alerts for state: {state}")
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    result = "\n---\n".join(alerts)
    logger.info(f"Found {len(alerts)} alerts for state: {state}")
    return result

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    logger.info(f"Getting forecast for location: {latitude}, {longitude}")
    
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        logger.warning(f"Failed to get points data for {latitude}, {longitude}")
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    try:
        forecast_url = points_data["properties"]["forecast"]
        logger.debug(f"Forecast URL: {forecast_url}")
    except (KeyError, TypeError) as e:
        logger.error(f"Error extracting forecast URL from points data: {str(e)}")
        return "Unable to process location data. The API response format may have changed."

    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        logger.warning("Failed to get forecast data")
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    try:
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
            forecasts.append(forecast)

        result = "\n---\n".join(forecasts)
        logger.info(f"Successfully generated forecast with {len(forecasts)} periods")
        return result
    except (KeyError, TypeError) as e:
        logger.error(f"Error processing forecast data: {str(e)}")
        return "Error processing forecast data. The API response format may have changed."

if __name__ == "__main__":
    logger.info("Starting server with stdio transport")
    try:
        # Initialize and run the server
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Failed to start MCP server: {str(e)}")
        sys.exit(1)