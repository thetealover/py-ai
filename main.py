#!/usr/bin/env python3
"""Main entry point for running the application."""

import sys
from pathlib import Path

import uvicorn

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import settings


def run_api_server():
    """Run the API server."""
    uvicorn.run(
        "src.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )


def run_mcp_server():
    """Run the MCP server."""
    from src.mcp.server import run_mcp_server
    run_mcp_server()


def main():
    """Main entry point with command selection."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [api|mcp]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "api":
        run_api_server()
    elif command == "mcp":
        run_mcp_server()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python main.py [api|mcp]")
        sys.exit(1)


if __name__ == "__main__":
    main()
