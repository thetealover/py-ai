from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.api.dependencies import get_chat_service
from src.api.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatInput(BaseModel):
    """Chat input model."""
    message: str
    session_id: str


@router.post("/stream")
async def stream_chat(
        chat_input: ChatInput,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Stream chat responses via Server-Sent Events."""
    return StreamingResponse(
        chat_service.stream_chat(
            chat_input.message,
            chat_input.session_id
        ),
        media_type="text/event-stream"
    )
