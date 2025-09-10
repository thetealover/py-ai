# ai_ws/services.py

from fastapi import Depends
from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .dependencies import get_agent_runnable
import json

# In-memory store for chat histories.
chat_histories = {}

# A more nuanced, balanced system prompt
AGENT_SYSTEM_PROMPT = """
You are a highly capable AI agent designed to be a reliable information-retrieval and problem-solving engine. Your goal is to provide the most accurate and relevant answer to the user.

To achieve this, you must follow a clear decision-making process:

1.  **First, Analyze the User's Request:** Before acting, classify the request into one of two categories:
    a. **Static Knowledge Request:** Questions about established facts, history, literature, creative writing, general knowledge, or math. Your extensive internal training data is the primary and most reliable source for these.
    b. **Dynamic Knowledge Request:** Questions about recent events, news, stock prices, weather, or any information that changes over time. These REQUIRE the use of a tool.

2.  **Act Based on the Category:**
    *   For **Static Knowledge Requests**, answer directly from your internal knowledge. DO NOT use a tool unless the user explicitly asks for a search. Your training on classic texts like Shakespeare is more reliable than a web search.
    *   For **Dynamic Knowledge Requests**, you MUST use a tool. State which tool you are using. If the tool fails or does not provide a definitive answer, you may then state what the tool returned and attempt to provide a more general answer from your internal knowledge, clearly stating that the information may not be up-to-date.

3.  **Be Confident in Your Knowledge:** Do not apologize for your primary functions. Answering from your internal knowledge is a core capability, not a limitation.
"""


class ChatService:
    def __init__(self, agent_runnable: Runnable = Depends(get_agent_runnable)):
        """
        Initializes the ChatService with a dependency-injected agent.
        """
        self.agent_runnable = agent_runnable

    async def stream_chat(self, user_input: str, session_id: str):
        """
        Streams the chat response from the LangGraph agent using a more nuanced system prompt.
        """
        # Retrieve the history for this session, or start a new one
        messages = chat_histories.get(session_id, [])

        # If this is the first message of the session, add our System Prompt
        if not messages:
            messages.append(SystemMessage(content=AGENT_SYSTEM_PROMPT))

        messages.append(HumanMessage(content=user_input))

        inputs = {"messages": messages}

        # astream_events provides a detailed stream of events from the graph
        async for event in self.agent_runnable.astream_events(
                inputs, version="v1"
        ):
            kind = event["event"]

            # Stream out the intermediate steps of the agent
            if kind == "on_tool_start":
                tool_input = event['data']['input']
                # Make the tool input look like code for better rendering
                tool_input_str = json.dumps(tool_input)
                yield f"data: {json.dumps({'type': 'tool_start', 'data': f'Using tool with input: `{tool_input_str}`...'})}\n\n"

            # Stream the tokens from the LLM as they are generated
            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    # Yield each content chunk as a JSON object
                    yield f"data: {json.dumps({'type': 'chunk', 'data': chunk.content})}\n\n"

            # When the full response is available, save it to the history
            elif kind == "on_chain_end":
                if (
                        event["name"] == "agent" and
                        isinstance(event["data"]["output"], dict) and
                        "messages" in event["data"]["output"]
                ):
                    # The final message is an AIMessage, add it to our history
                    ai_message = event["data"]["output"]["messages"][-1]
                    if isinstance(ai_message, AIMessage):
                        messages.append(ai_message)

        # Store the updated history for the next interaction
        chat_histories[session_id] = messages

        # Signal the end of the stream
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
