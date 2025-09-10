from typing import Optional

from openapi_pydantic.compat import ConfigDict
from pydantic import BaseModel


class LocationDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime: str
    localtime_epoch: Optional[int]


class ConditionDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str
    icon: str
    code: int


class CurrentWeatherDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    condition: Optional[ConditionDto]
    last_updated_epoch: Optional[int]
    last_updated: Optional[str]
    temp_c: float
    temp_f: float
    is_day: int
    wind_kph: float
    feelslike_c: float
    uv: float
    humidity: int
    cloud: int


class WeatherDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location: Optional[LocationDto]
    current: Optional[CurrentWeatherDto]
