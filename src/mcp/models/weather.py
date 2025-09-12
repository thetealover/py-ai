from typing import Optional
from pydantic import BaseModel, Field


class Location(BaseModel):
    """Location information model."""
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str = Field(alias="tz_id")
    localtime: str
    localtime_epoch: Optional[int] = None


class Condition(BaseModel):
    """Weather condition model."""
    text: str
    icon: str
    code: int


class CurrentWeather(BaseModel):
    """Current weather information model."""
    condition: Optional[Condition] = None
    last_updated_epoch: Optional[int] = None
    last_updated: Optional[str] = None
    temp_c: float
    temp_f: float
    is_day: int
    wind_kph: float
    feelslike_c: float
    uv: float
    humidity: int
    cloud: int


class Weather(BaseModel):
    """Complete weather response model."""
    location: Optional[Location] = None
    current: Optional[CurrentWeather] = None
