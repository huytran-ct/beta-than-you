from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import datetime

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

@mcp.tool()
async def get_current_time():
    """
    Get the current time.
    """
    return datetime.datetime.now().isoformat()

@mcp.tool()
async def convert_date_to_date_of_week(date: str):
    """
    Convert a date string to the day of the week.
    """
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        return date_obj.strftime("%A")
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
