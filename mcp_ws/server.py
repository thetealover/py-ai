import os

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

from mcp_ws.dto import WeatherDto

load_dotenv()

mcp = FastMCP(name="py_api_mcp")
mcp_port = int(os.getenv("MCP_WS_PORT"))
weather_api_key = os.getenv("WEATHER_API_KEY")
weather_api_base_url = os.getenv("WEATHER_API_BASE_URL")


@mcp.tool(name="get_current_weather", description="Get the current weather in a given city")
async def get_weather(city: str) -> WeatherDto:
    try:
        response_json = requests.get(f"{weather_api_base_url}/current.json?q={city}&key={weather_api_key}").json()

        return WeatherDto(**response_json)

    except Exception as e:
        print(f"Error getting weather data: {str(e)}")
        raise


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=mcp_port)
