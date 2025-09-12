from typing import List, Optional

from langchain_core.tools import BaseTool

from src.ai.agents.chat_agent import ChatAgent
from src.ai.tools.mcp_tools import MCPToolProvider
from src.ai.tools.search_tools import SearchToolProvider
from src.api.services.chat_service import ChatService

# Cache for tools and agent
_tools_cache: Optional[List[BaseTool]] = None
_agent_cache: Optional[ChatAgent] = None


async def get_tools() -> List[BaseTool]:
    """Get all available tools with caching."""
    global _tools_cache

    if _tools_cache is None:
        tools = []

        # Get MCP tools
        mcp_provider = MCPToolProvider()
        tools.extend(await mcp_provider.get_tools())

        # Get search tools
        search_provider = SearchToolProvider()
        tools.extend(await search_provider.get_tools())

        _tools_cache = tools

    return _tools_cache


async def get_agent() -> ChatAgent:
    """Get the chat agent instance with caching."""
    global _agent_cache

    if _agent_cache is None:
        tools = await get_tools()
        agent = ChatAgent(tools=tools)
        await agent.build()
        _agent_cache = agent

    return _agent_cache


async def get_chat_service() -> ChatService:
    """Get the chat service instance."""
    agent = await get_agent()
    return ChatService(agent)
