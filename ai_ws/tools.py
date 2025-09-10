import asyncio
import os
import threading
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection
from langchain_tavily import TavilySearch

load_dotenv()

mcp_ws_url = os.getenv("MCP_WS_URL")
mcp_ws_server_name = os.getenv("MCP_WS_SERVER_NAME")

# Cache for tools to avoid repeated fetching
_cached_tools: Optional[List[BaseTool]] = None
_tools_lock = threading.Lock()


def get_all_tools_sync() -> List[BaseTool]:
    """
    Synchronously get all tools (MCP + Tavily) by creating a new event loop.
    Uses caching to avoid repeated MCP server calls.
    """
    global _cached_tools

    if _cached_tools is None:
        with _tools_lock:
            # Double-check locking pattern
            if _cached_tools is None:
                # Create a new event loop in a separate thread to avoid conflicts
                def run_in_thread():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(_get_all_tools_async())
                    finally:
                        loop.close()

                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    _cached_tools = future.result()

    return _cached_tools


async def _get_all_tools_async() -> List[BaseTool]:
    """Internal async function to fetch all tools"""
    try:
        mcp_tools = await get_mcp_tools_for_langgraph()
    except Exception as e:
        print(f"Warning: Failed to load MCP tools: {e}")
        mcp_tools = []

    tavily_tool = get_tavily_search_tool()
    return mcp_tools + [tavily_tool]


async def get_all_tools() -> List[BaseTool]:
    return await _get_all_tools_async()


async def get_mcp_tools_for_langgraph() -> List[BaseTool]:
    mcp_tools = await get_py_api_mcp_tools()
    # Tools from mcp_client.get_tools() are already LangChain-compatible
    return mcp_tools


async def get_multi_server_mcp_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(connections={
        mcp_ws_server_name: StreamableHttpConnection(transport="streamable_http", url=mcp_ws_url)})


async def get_py_api_mcp_tools():
    # Use the same pattern as in main.py - use client.get_tools() instead of load_mcp_tools()
    mcp_client = await get_multi_server_mcp_client()
    tools = await mcp_client.get_tools(server_name=mcp_ws_server_name)
    return tools


def get_tavily_search_tool():
    return TavilySearch(max_results=2)
