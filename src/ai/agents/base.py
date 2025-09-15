from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        self.tools = tools or []
        self._runnable: Optional[Runnable] = None

    @abstractmethod
    async def build(self) -> Runnable:
        """Build and return the agent runnable."""
        pass

    @property
    def runnable(self) -> Runnable:
        """Get the compiled agent runnable."""
        if self._runnable is None:
            raise RuntimeError(
                "Agent is not compiled. Call build() or build_with_checkpointer() first."
            )
        return self._runnable
