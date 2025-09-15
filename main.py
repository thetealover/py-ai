import subprocess
import sys
from pathlib import Path

import uvicorn

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


def run_streamlit_app():
    """Run the Streamlit UI application."""
    streamlit_path = Path(__file__).parent / "src" / "streamlit_app" / "app.py"
    command = [
        "streamlit",
        "run",
        str(streamlit_path),
        "--server.port",
        "8501",
        "--server.address",
        "localhost"
    ]
    subprocess.run(command)


def main():
    """Main entry point with command selection."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [api|mcp|streamlit]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "api":
        run_api_server()
    elif command == "mcp":
        run_mcp_server()
    elif command == "streamlit":
        run_streamlit_app()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python main.py [api|mcp|streamlit]")
        sys.exit(1)


if __name__ == "__main__":
    main()
