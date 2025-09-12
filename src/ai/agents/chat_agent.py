import operator
from typing import TypedDict, Annotated, Sequence, List, Optional
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from src.config.settings import settings
from src.ai.agents.base import BaseAgent
from src.ai.prompts import CHAT_AGENT_SYSTEM_PROMPT


class AgentState(TypedDict):
    """State definition for the chat agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ChatAgent(BaseAgent):
    """Main conversational AI agent using LangGraph."""

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        super().__init__(tools)
        self.model = None
        self.system_prompt = CHAT_AGENT_SYSTEM_PROMPT

    async def build(self):
        """Build the LangGraph agent."""
        # Initialize model with tools
        self.model = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.google_api_key
        )

        if self.tools:
            self.model = self.model.bind_tools(self.tools)

        # Build the graph
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("agent", self._call_model)
        graph.add_node("action", self._call_tool)

        # Set entry point
        graph.set_entry_point("agent")

        # Add conditional edges
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "action",
                "end": END,
            },
        )

        # Add edge from action back to agent
        graph.add_edge("action", "agent")

        # Compile the graph
        self._runnable = graph.compile()
        return self._runnable

    def _should_continue(self, state: AgentState) -> str:
        """Determine if the agent should continue or end."""
        last_message = state["messages"][-1]
        if not last_message.tool_calls:
            return "end"
        return "continue"

    async def _call_model(self, state: AgentState):
        """Call the LLM model."""
        messages = state["messages"]
        response = await self.model.ainvoke(messages)
        return {"messages": [response]}

    async def _call_tool(self, state: AgentState):
        """Execute a tool call."""
        last_message = state["messages"][-1]
        action = last_message.tool_calls[0]

        # Find the appropriate tool by name
        tool_name = action["name"]
        tool_to_use = None

        for tool in self.tools:
            if tool.name == tool_name:
                tool_to_use = tool
                break

        if tool_to_use is None:
            response = f"Tool '{tool_name}' not found"
        else:
            response = await tool_to_use.ainvoke(action["args"])

        tool_message = ToolMessage(
            content=str(response),
            tool_call_id=action["id"]
        )
        return {"messages": [tool_message]}
