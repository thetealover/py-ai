import logging
import operator
from typing import TypedDict, Annotated, Sequence, List, Optional

from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph, END

from src.ai.agents.base import BaseAgent
from src.ai.prompts import CHAT_AGENT_SYSTEM_PROMPT
from src.config.settings import settings

logger = logging.getLogger(__name__)


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
        """
        Implementation of the abstract 'build' method from BaseAgent.
        This builds the agent without a persistence layer.
        """
        logger.info("Building agent without a checkpointer (no persistence).")
        return await self.build_with_checkpointer(checkpointer=None)

    async def build_with_checkpointer(self, checkpointer: Optional[BaseCheckpointSaver] = None):
        """Build the LangGraph agent with an optional checkpointer for persistence."""
        self.model = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.google_api_key
        )

        if self.tools:
            self.model = self.model.bind_tools(self.tools)

        graph = StateGraph(AgentState)
        graph.add_node("agent", self._call_model)
        graph.add_node("action", self._call_tool)
        graph.set_entry_point("agent")
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {"continue": "action", "end": END},
        )
        graph.add_edge("action", "agent")

        if checkpointer:
            self._runnable = graph.compile(checkpointer=checkpointer)
            logger.info("Agent compiled successfully with persistence enabled.")
        else:
            self._runnable = graph.compile()
            logger.info("Agent compiled successfully without persistence.")

        return self._runnable

    @staticmethod
    def _should_continue(state: AgentState) -> str:
        """Determine if the agent should continue or end."""
        last_message = state["messages"][-1]
        if not last_message.tool_calls:
            return "end"
        return "continue"

    async def _call_model(self, state: AgentState):
        """Prepares messages and calls the LLM model."""
        messages = state["messages"]

        if not messages or not isinstance(messages[0], SystemMessage):
            messages_with_prompt = [SystemMessage(content=self.system_prompt)] + messages
        else:
            messages_with_prompt = messages

        response = await self.model.ainvoke(messages_with_prompt)
        return {"messages": [response]}

    async def _call_tool(self, state: AgentState):
        """Execute a tool call."""
        last_message = state["messages"][-1]
        action = last_message.tool_calls[0]
        tool_name = action["name"]
        tool_to_use = next((tool for tool in self.tools if tool.name == tool_name), None)

        if tool_to_use is None:
            response = f"Tool '{tool_name}' not found"
        else:
            response = await tool_to_use.ainvoke(action["args"])

        tool_message = ToolMessage(content=str(response), tool_call_id=action["id"])
        return {"messages": [tool_message]}
