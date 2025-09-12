import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration using Pydantic BaseSettings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    google_api_key: str = Field(
        default=os.environ.get("GOOGLE_API_KEY"),
        description="Google API key for Gemini",
        alias="GOOGLE_API_KEY"
    )
    tavily_api_key: str = Field(
        default=os.environ.get("TAVILY_API_KEY"),
        description="Tavily API key for search",
        alias="TAVILY_API_KEY"
    )
    weather_api_key: str = Field(
        default=os.environ.get("WEATHER_API_KEY"),
        description="Weather API key",
        alias="WEATHER_API_KEY"
    )

    # API URLs
    weather_api_base_url: str = Field(
        default="https://api.weatherapi.com/v1",
        description="Weather API base URL",
        alias="WEATHER_API_BASE_URL"
    )
    mcp_ws_url: str = Field(
        default="http://localhost:8001/mcp",
        description="MCP WebSocket URL",
        alias="MCP_WS_URL"
    )

    # Server Configuration
    mcp_ws_server_name: str = Field(
        default="py_api_mcp",
        description="MCP server name",
        alias="MCP_WS_SERVER_NAME"
    )
    mcp_ws_port: int = Field(
        default=8001,
        description="MCP WebSocket port",
        alias="MCP_WS_PORT"
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
        alias="API_PORT"
    )
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
        alias="API_HOST"
    )

    # Model Configuration
    llm_model: str = Field(
        default="gemini-2.5-flash",
        description="LLM model to use",
        alias="LLM_MODEL"
    )
    llm_temperature: float = Field(
        default=0.0,
        description="LLM temperature",
        alias="LLM_TEMPERATURE"
    )

    # Feature Flags
    enable_mcp_tools: bool = Field(
        default=True,
        description="Enable MCP tools",
        alias="ENABLE_MCP_TOOLS"
    )
    enable_search_tools: bool = Field(
        default=True,
        description="Enable search tools",
        alias="ENABLE_SEARCH_TOOLS"
    )

    @field_validator("llm_temperature")
    def validate_temperature(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v


# Global settings instance
settings = Settings()
