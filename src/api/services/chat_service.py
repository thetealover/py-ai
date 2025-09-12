import json
from typing import Dict, AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.ai.agents.chat_agent import ChatAgent
from src.ai.prompts import CHAT_AGENT_SYSTEM_PROMPT


class ChatService:
    """Service for handling chat interactions."""

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        self.chat_histories: Dict[str, list] = {}

    async def stream_chat(
            self,
            user_input: str,
            session_id: str
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses using Server-Sent Events format."""
        # Get or create chat history for this session
        messages = self.chat_histories.get(session_id, [])

        # Add system prompt for new sessions
        if not messages:
            messages.append(SystemMessage(content=CHAT_AGENT_SYSTEM_PROMPT))

        # Add user message
        messages.append(HumanMessage(content=user_input))

        inputs = {"messages": messages}

        # Stream events from the agent
        async for event in self.agent.runnable.astream_events(
                inputs, version="v1"
        ):
            kind = event["event"]

            # Stream tool usage information
            if kind == "on_tool_start":
                tool_input = event['data']['input']
                tool_input_str = json.dumps(tool_input)
                yield self._format_sse(
                    "tool_start",
                    f"Using tool with input: `{tool_input_str}`..."
                )

            # Stream LLM tokens as they are generated
            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield self._format_sse("chunk", chunk.content)

            # Save the complete response to history
            elif kind == "on_chain_end":
                if (
                        event["name"] == "agent" and
                        isinstance(event["data"]["output"], dict) and
                        "messages" in event["data"]["output"]
                ):
                    ai_message = event["data"]["output"]["messages"][-1]
                    if isinstance(ai_message, AIMessage):
                        messages.append(ai_message)

        # Update chat history
        self.chat_histories[session_id] = messages

        # Signal end of stream
        yield self._format_sse("end", "")

    def _format_sse(self, event_type: str, data: str) -> str:
        """Format data for Server-Sent Events."""
        return f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"
