import operator
from typing import TypedDict, Annotated, Sequence, Optional, List

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from ai_ws.tools import get_all_tools


# 1. Define the state for our agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# 2. Lazy tool loading
_tools_cache: Optional[List[BaseTool]] = None
_model_cache: Optional[ChatGoogleGenerativeAI] = None


async def get_tools_and_model():
    """Get tools and model with lazy initialization"""
    global _tools_cache, _model_cache

    if _tools_cache is None:
        _tools_cache = await get_all_tools()

    if _model_cache is None:
        _model_cache = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        ).bind_tools(_tools_cache)

    return _tools_cache, _model_cache


# 4. Define the graph
graph = StateGraph(AgentState)


def should_continue(state: AgentState) -> str:
    last_message = state['messages'][-1]
    if not last_message.tool_calls:
        return "end"
    return "continue"


async def call_model(state: AgentState):
    _, model = await get_tools_and_model()
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}


async def call_tool(state: AgentState):
    tools, _ = await get_tools_and_model()
    last_message = state['messages'][-1]
    action = last_message.tool_calls[0]

    # Find the appropriate tool by name
    tool_name = action['name']
    tool_to_use = None
    for tool in tools:
        if tool.name == tool_name:
            tool_to_use = tool
            break

    if tool_to_use is None:
        response = f"Tool '{tool_name}' not found"
    else:
        response = await tool_to_use.ainvoke(action['args'])

    tool_message = ToolMessage(content=str(response), tool_call_id=action['id'])
    return {"messages": [tool_message]}


# Define the nodes in the graph
graph.add_node("agent", call_model)
graph.add_node("action", call_tool)

# Set the entry point for the graph
graph.set_entry_point("agent")

# Add conditional edges
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

# Add a regular edge from the action node back to the agent node
graph.add_edge('action', 'agent')

# Compile the graph into a runnable object
runnable = graph.compile()
