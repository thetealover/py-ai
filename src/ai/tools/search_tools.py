from typing import List
from langchain_core.tools import BaseTool
from langchain_tavily import TavilySearch

from src.config.settings import settings
from src.ai.tools.base import ToolProvider


class SearchToolProvider(ToolProvider):
    """Provider for search tools."""

    async def get_tools(self) -> List[BaseTool]:
        """Get search tools."""
        if not settings.enable_search_tools:
            return []

        tavily_tool = TavilySearch(
            max_results=2, tavily_api_key=settings.tavily_api_key
        )
        return [tavily_tool]
