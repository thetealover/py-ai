from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration using Pydantic BaseSettings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # --- Database Connection Components (Single Source of Truth) ---
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(..., alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")

    @property
    def db_dsn(self) -> str:
        """
        Data Source Name (DSN) connection string for native psycopg_pool.
        Format: "dbname=... user=... password=... host=... port=..."
        """
        return (
            f"dbname={self.db_name} user={self.db_user} "
            f"password={self.db_password} host={self.db_host} port={self.db_port}"
        )

    @property
    def sqlalchemy_url(self) -> str:
        """
        SQLAlchemy-style connection URI for Alembic.
        Format: "postgresql+psycopg://user:password@host:port/dbname"
        """
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # --- API Keys ---
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    tavily_api_key: str = Field(..., alias="TAVILY_API_KEY")
    weather_api_key: str = Field(..., alias="WEATHER_API_KEY")

    # --- API URLs ---
    weather_api_base_url: str = Field("https://api.weatherapi.com/v1", alias="WEATHER_API_BASE_URL")
    mcp_ws_url: str = Field("http://localhost:8001/mcp", alias="MCP_WS_URL")

    # --- Server Configuration ---
    mcp_ws_server_name: str = Field("py_api_mcp", alias="MCP_WS_SERVER_NAME")
    mcp_ws_port: int = Field(8001, alias="MCP_WS_PORT")
    api_port: int = Field(8000, alias="API_PORT")
    api_host: str = Field("http://localhost", alias="API_HOST")

    # --- Model Configuration ---
    llm_model: str = Field("gemini-2.5-flash", alias="LLM_MODEL")
    llm_temperature: float = Field(0.0, alias="LLM_TEMPERATURE")

    title_determinator_llm_model: str = Field("gemini-2.5-flash", alias="TITLE_DETERMINATOR_LLM_MODEL")
    title_determinator_llm_temperature: float = Field(0.0, alias="TITLE_DETERMINATOR_LLM_TEMPERATURE")

    # --- Feature Flags ---
    enable_mcp_tools: bool = Field(True, alias="ENABLE_MCP_TOOLS")
    enable_search_tools: bool = Field(True, alias="ENABLE_SEARCH_TOOLS")


settings = Settings()
