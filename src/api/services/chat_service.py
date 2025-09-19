import json
from typing import AsyncGenerator

from fastapi import BackgroundTasks
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.ai.agents.chat_agent import ChatAgent
from src.api.services.chat_title_service import generate_and_save_title


class ChatService:
    """Service for handling chat interactions, relying on the agent's checkpointer."""

    def __init__(self, agent: ChatAgent):
        self.agent = agent

    async def stream_chat(
        self, user_input: str, session_id: str, background_tasks: BackgroundTasks
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses and queue a background task to generate a title.
        """
        inputs = {"messages": [HumanMessage(content=user_input)]}
        config = RunnableConfig(configurable={"thread_id": session_id})

        async for event in self.agent.runnable.astream_events(
            inputs, config=config, version="v1"
        ):
            kind = event["event"]
            if kind == "on_tool_start":
                tool_input = event["data"]["input"]
                tool_input_str = json.dumps(tool_input)
                yield self._format_sse(
                    "tool_start", f"Using tool with input: `{tool_input_str}`..."
                )
            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield self._format_sse("chunk", chunk.content)

        # This code runs after the generator has been fully consumed by the client.
        yield self._format_sse("end", "")

        final_state = await self.agent.runnable.aget_state(config)
        if final_state:
            history = final_state.values.get("messages", [])
            # We generate a title after the first user message and AI response.
            if len(history) >= 2:
                background_tasks.add_task(generate_and_save_title, session_id, history)

    def _format_sse(self, event_type: str, data: str) -> str:
        """Format data for Server-Sent Events."""
        return f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"
