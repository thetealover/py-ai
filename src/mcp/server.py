import logging
from fastmcp import FastMCP

from src.config.settings import settings
from src.mcp.models.weather import Weather
from src.mcp.services.weather_service import WeatherService

logger = logging.getLogger(__name__)
mcp = FastMCP(name="py_api_mcp")
weather_service = WeatherService()


@mcp.tool(
    name="get_current_weather",
    description="Get the current weather in a given city"
)
async def get_weather(city: str) -> Weather:
    """Get current weather for a city."""
    try:
        return await weather_service.get_current_weather(city)
    except Exception as e:
        logger.error(f"Error getting weather data: {str(e)}")
        raise


def run_mcp_server():
    """Run the MCP server."""
    mcp.run(transport="streamable-http", port=settings.mcp_ws_port)


if __name__ == "__main__":
    run_mcp_server()
