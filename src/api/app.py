import asyncio
import importlib.metadata
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from psycopg_pool import AsyncConnectionPool, ConnectionPool

from src.ai.agent_manager import AgentManager
from src.api.exceptions import register_exception_handlers
from src.api.migrations import run_migrations_sync
from src.api.routes import chat, mcp
from src.config.config_utils import get_project_version
from src.config.logging_config import setup_logging
from src.config.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifecycle. It runs database migrations synchronously
    before setting up the main asynchronous connection pool for the application.
    """
    setup_logging()
    logger.info("Application startup: Initializing resources...")

    # 1. Run migrations synchronously using a dedicated synchronous pool
    try:
        with ConnectionPool(conninfo=settings.db_dsn) as sync_pool:
            await asyncio.to_thread(run_migrations_sync, sync_pool)
    except Exception as e:
        logger.critical(f"Database migration failed during startup: {e}")
        raise

    # 2. Set up the main asynchronous pool for the application
    db_pool = AsyncConnectionPool(conninfo=settings.db_dsn, open=False)
    await db_pool.open(wait=True)
    logger.info("Asynchronous database connection pool for the application is open.")

    manager = AgentManager()
    await manager.start(db_pool)
    app.state.agent_manager = manager

    yield

    logger.info("Application shutdown: Cleaning up resources...")
    await app.state.agent_manager.stop()
    await db_pool.close()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    api = FastAPI(
        title="AI Chat API",
        description="AI-powered chat API with MCP integration",
        version=get_project_version(),
        lifespan=lifespan,
    )

    register_exception_handlers(api)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(chat.router)
    api.include_router(mcp.router)

    @api.get("/health")
    async def health_check(request: Request):
        agent_manager = request.app.state.agent_manager
        agent = agent_manager.get_agent() if agent_manager else None
        persistence_enabled = agent and agent.runnable.checkpointer is not None
        return {
            "status": "healthy",
            "agent_initialized": agent is not None,
            "persistence_enabled": persistence_enabled,
        }

    return api


app = create_app()
