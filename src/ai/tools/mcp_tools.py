import logging
from typing import List
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection

from src.config.settings import settings
from src.ai.tools.base import ToolProvider

logger = logging.getLogger(__name__)


class MCPToolProvider(ToolProvider):
    """Provider for MCP (Model Context Protocol) tools."""

    def __init__(self):
        self.client = None

    async def get_tools(self) -> List[BaseTool]:
        """Get MCP tools from the MCP server."""
        if not settings.enable_mcp_tools:
            return []

        try:
            self.client = MultiServerMCPClient(
                connections={
                    settings.mcp_ws_server_name: StreamableHttpConnection(
                        transport="streamable_http",
                        url=settings.mcp_ws_url
                    )
                }
            )

            tools = await self.client.get_tools(
                server_name=settings.mcp_ws_server_name
            )
            return tools
        except Exception as e:
            logger.warning(f"Failed to load MCP tools: {e}")
            return []
