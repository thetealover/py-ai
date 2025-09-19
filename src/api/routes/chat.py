import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig

from src.api.dependencies import get_chat_service, get_agent
from src.api.services.chat_service import ChatService
from src.ai.agents.chat_agent import ChatAgent
from src.api.db import get_conversations_for_user

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatInput(BaseModel):
    """Chat input model."""

    message: str
    session_id: str


@router.post("/stream")
async def stream_chat(
    chat_input: ChatInput,
    background_tasks: BackgroundTasks,
    chat_service: ChatService = Depends(get_chat_service),
):
    """Stream chat responses and trigger title generation in the background."""
    return StreamingResponse(
        chat_service.stream_chat(
            chat_input.message, chat_input.session_id, background_tasks
        ),
        media_type="text/event-stream",
    )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, agent: ChatAgent = Depends(get_agent)):
    """Retrieve the full chat history for a given session ID."""
    try:
        config = RunnableConfig(configurable={"thread_id": session_id})
        state = await agent.runnable.aget_state(config)

        if state is None:
            return JSONResponse(content=[])

        messages = [msg.dict() for msg in state.values.get("messages", [])]
        return JSONResponse(content=messages)

    except Exception as e:
        logger.error(f"Error retrieving history for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve chat history.")


@router.get("/user/{username}")
async def get_user_conversations(username: str):
    """Retrieve all conversation threads for a specific user."""
    try:
        conversations = await get_conversations_for_user(username)
        return JSONResponse(content=conversations)
    except Exception as e:
        logger.error(f"API error fetching conversations for user '{username}': {e}")
        raise HTTPException(
            status_code=500, detail="Could not retrieve user conversations."
        )
