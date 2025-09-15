from typing import Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.ai.tools.mcp_tools import MCPToolProvider

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("")
async def call_mcp(city: Optional[str] = None):
    """Call MCP tool directly (for testing)."""
    if not city:
        return JSONResponse(
            content={"error": "City parameter is required"},
            status_code=400
        )

    provider = MCPToolProvider()
    tools = await provider.get_tools()

    if not tools:
        return JSONResponse(
            content={"error": "No MCP tools available"},
            status_code=503
        )

    weather_tool = next(
        (tool for tool in tools if tool.name == "get_current_weather"),
        None
    )

    if not weather_tool:
        return JSONResponse(
            content={"error": "Weather tool not found"},
            status_code=404
        )

    result = await weather_tool.ainvoke({"city": city})
    return JSONResponse(content=result)
