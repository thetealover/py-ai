from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, mcp
from src.config.settings import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Chat API",
        description="AI-powered chat API with MCP integration",
        version="0.2.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chat.router)
    app.include_router(mcp.router)

    # Setup templates
    templates = Jinja2Templates(directory="src/templates")

    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        """Serve the main HTML page."""
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "llm_model": settings.llm_model,
            "mcp_enabled": settings.enable_mcp_tools,
            "search_enabled": settings.enable_search_tools
        }

    return app


# Create app instance
app = create_app()
