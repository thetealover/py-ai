from abc import ABC, abstractmethod
from typing import List
from langchain_core.tools import BaseTool


class ToolProvider(ABC):
    """Abstract base class for tool providers."""

    @abstractmethod
    async def get_tools(self) -> List[BaseTool]:
        """Get list of tools provided by this provider."""
        pass
