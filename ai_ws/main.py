# ai_ws/main.py
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection
from starlette.responses import JSONResponse

# from ai_ws.mcp_tools import get_current_weather_mcp

# IMPORTANT: Load environment variables from .env file BEFORE other imports
# This ensures that API keys are available when other modules are imported.
load_dotenv()

# --- Now, we can safely import the rest of our application modules ---
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from .services import ChatService
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class UserInput(BaseModel):
    message: str
    session_id: str  # Added to track conversation history


@app.get(path="/mcp")
async def call_mcp(city: Optional[str]) -> Any:
    mcp_client = MultiServerMCPClient(connections={
        "py_api_mcp": StreamableHttpConnection(transport="streamable_http", url="http://localhost:8001/mcp")})

    tools = await mcp_client.get_tools(server_name="py_api_mcp")
    get_current_weather_tool = tools.pop(0)

    print(f"getting the weather for {city}")

    result = JSONResponse(await get_current_weather_tool.ainvoke({"city": city}))
    print(result)
    return result


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat/stream")
async def stream_chat(
        user_input: UserInput,
        chat_service: ChatService = Depends(),
):
    """
    Endpoint to handle chat requests and stream responses via SSE.
    Now uses a session_id to maintain chat history.
    """
    return StreamingResponse(
        chat_service.stream_chat(user_input.message, user_input.session_id),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
