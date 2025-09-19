import logging
from typing import List, Optional

from langchain_core.tools import BaseTool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from src.ai.agents.chat_agent import ChatAgent
from src.ai.tools.mcp_tools import MCPToolProvider
from src.ai.tools.search_tools import SearchToolProvider

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages the lifecycle of the AI agent, using a pre-configured database pool.
    """

    def __init__(self):
        self.db_pool: Optional[AsyncConnectionPool] = None
        self.checkpointer: Optional[AsyncPostgresSaver] = None
        self.agent: Optional[ChatAgent] = None
        self._tools_cache: Optional[List[BaseTool]] = None

    async def start(self, db_pool: AsyncConnectionPool):
        """
        Initializes resources using the provided database connection pool.
        """
        logger.info("Agent Manager: Starting...")
        try:
            self.db_pool = db_pool
            logger.info("Agent Manager: Received shared connection pool.")

            self.checkpointer = AsyncPostgresSaver(self.db_pool)
            await self.checkpointer.setup()
            logger.info("Agent Manager: AsyncPostgresSaver setup complete.")

            tools = await self._get_tools()

            self.agent = ChatAgent(tools=tools)
            await self.agent.build_with_checkpointer(self.checkpointer)
            logger.info(
                "Agent Manager: Persistent agent created and compiled successfully."
            )

        except Exception as e:
            logger.critical(f"Agent Manager failed to start: {e}")
            raise

    async def stop(self):
        """
        Gracefully shuts down resources. The pool is closed by the lifespan manager.
        """
        if self.db_pool:
            logger.info("Agent Manager: Releasing resources...")
            self.db_pool = None
            logger.info("Agent Manager: Resources released.")

    async def _get_tools(self) -> List[BaseTool]:
        """Loads and caches all available tools."""
        if self._tools_cache is None:
            tools = []
            logger.info("Agent Manager: Loading tools...")
            try:
                mcp_provider = MCPToolProvider()
                tools.extend(await mcp_provider.get_tools())
                search_provider = SearchToolProvider()
                tools.extend(await search_provider.get_tools())
                self._tools_cache = tools
                logger.info(f"Agent Manager: Successfully loaded {len(tools)} tools.")
            except Exception as e:
                logger.error(f"Agent Manager: Error loading tools: {e}")
                self._tools_cache = []
        return self._tools_cache

    def get_agent(self) -> ChatAgent:
        """Returns the managed agent instance."""
        if not self.agent:
            raise RuntimeError(
                "Agent not initialized. The AgentManager must be started first."
            )
        return self.agent
