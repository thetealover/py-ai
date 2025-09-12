import httpx

from src.config.settings import settings
from src.mcp.models.weather import Weather


class WeatherService:
    """Service for fetching weather data."""

    def __init__(self):
        self.base_url = settings.weather_api_base_url
        self.api_key = settings.weather_api_key

    async def get_current_weather(self, city: str) -> Weather:
        """Fetch current weather for a city."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/current.json",
                params={
                    "q": city,
                    "key": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            return Weather(**data)
