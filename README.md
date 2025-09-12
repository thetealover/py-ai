# py-ai

An AI-powered chat API with Model Context Protocol (MCP) integration, built with FastAPI, LangChain, and LangGraph.

## Features

- **Backend:** FastAPI with Python 3.12
- **Conversational AI:** LangChain with LangGraph for stateful, multi-step agents
- **LLM:** Google Gemini (configurable model)
- **Real-time Communication:** Server-Sent Events (SSE) for streaming LLM responses
- **MCP Integration:** Support for Model Context Protocol tools
- **Search Capabilities:** Integrated Tavily search
- **Configuration:** Pydantic-based settings management
- **Dependency Management:** Poetry

## Architecture

The project follows a clean architecture pattern with clear separation of concerns:

- `src/config/`: Configuration management using Pydantic
- `src/ai/`: AI agents and tools
- `src/mcp/`: MCP server implementation
- `src/api/`: FastAPI application and routes
- `src/templates/`: HTML templates

## Prerequisites

- Python 3.12 or higher
- Poetry for dependency management

## Setup

1. **Install Poetry:** If you don't have Poetry installed, follow the instructions on
   the [official website](https://python-poetry.org/docs/).

2. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd py-ai
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Configure environment:** Edit `.env` and add your API keys. If none are provided, the variables will be
   interpolated from the system environment variables.

   Keys to be set up:
    - Get a Google API key from [Google AI for Developers](https://ai.google.dev/)
    - Get a Tavily API key from [Tavily](https://tavily.com/)
    - Get a Weather API key from [WeatherAPI](https://www.weatherapi.com/)

## Running the Application

You need to run both the MCP server and the API server for full functionality.

### Option 1: Using the main entry point

In separate terminal windows:

**Terminal 1 - Run the MCP server:**

```bash
poetry run python main.py mcp
```

**Terminal 2 - Run the API server:**

```bash
poetry run python main.py api
```

### Option 2: Run directly with modules

**Terminal 1 - Run the MCP server:**

```bash
poetry run python -m src.mcp.server
```

**Terminal 2 - Run the API server:**

```bash
poetry run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using shell scripts (create these for convenience)

Create `run-mcp.sh`:

```bash
#!/bin/bash
poetry run python main.py mcp
```

Create `run-api.sh`:

```bash
#!/bin/bash
poetry run python main.py api
```

Make them executable:

```bash
chmod +x run-mcp.sh run-api.sh
```

Then run in separate terminals:

```bash
./run-mcp.sh
./run-api.sh
```

## Accessing the Application

Once both servers are running:

1. Open your browser and navigate to `http://localhost:8000`
2. You'll see the chat interface where you can interact with the AI assistant
3. The assistant has access to:
    - Weather information (through MCP tools)
    - Web search capabilities (through Tavily)
    - General knowledge from the LLM

## API Endpoints

- `GET /` - Main chat interface (web UI)
- `POST /chat/stream` - Stream chat responses (SSE)
- `GET /mcp?city={city}` - Test MCP weather tool directly
- `GET /health` - Health check endpoint

## Development

### Code Quality Tools

Format code with Black:

```bash
poetry run black src tests
```

Sort imports with isort:

```bash
poetry run isort src tests
```

Lint with flake8:

```bash
poetry run flake8 src tests
```

Type check with mypy:

```bash
poetry run mypy src
```

Run all checks:

```bash
poetry run black src tests && poetry run isort src tests && poetry run flake8 src tests && poetry run mypy src
```

### Running Tests

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=src
```

Run specific test file:

```bash
poetry run pytest tests/test_api.py
```

## Configuration

All configuration is managed through environment variables and the `src/config/settings.py` file. Key settings include:

### Required Environment Variables

- `GOOGLE_API_KEY`: Google API key for Gemini LLM
- `TAVILY_API_KEY`: Tavily API key for search functionality
- `WEATHER_API_KEY`: Weather API key for weather data

### Optional Environment Variables

- `API_PORT`: API server port (default: 8000)
- `API_HOST`: API server host (default: 0.0.0.0)
- `MCP_WS_PORT`: MCP server port (default: 8001)
- `LLM_MODEL`: LLM model to use (default: gemini-2.5-flash)
- `LLM_TEMPERATURE`: LLM temperature setting (default: 0.0)
- `ENABLE_MCP_TOOLS`: Enable/disable MCP tools (default: true)
- `ENABLE_SEARCH_TOOLS`: Enable/disable search tools (default: true)

## Troubleshooting

### Common Issues

1. **Dependency conflicts during installation:**
   ```bash
   poetry lock --no-update
   poetry install
   ```

2. **MCP server connection errors:**
    - Ensure the MCP server is running before starting the API server
    - Check that the MCP_WS_URL in your .env matches the MCP server address

3. **API key errors:**
    - Verify all required API keys are set in your .env file
    - Ensure there are no extra spaces or quotes around the API keys

4. **Port already in use:**
    - Change the port in your .env file or use different ports:
   ```bash
   poetry run uvicorn src.api.app:app --port 8001
   ```

Build and run:

```bash
docker build -t py-ai .
docker run -p 8000:8000 -p 8001:8001 --env-file .env py-ai
```

## Project Structure

```
py-ai/
├── src/
│   ├── config/          # Configuration management
│   │   └── settings.py  # Pydantic settings
│   ├── ai/              # AI agents and tools
│   │   ├── agents/      # Agent implementations
│   │   ├── tools/       # Tool providers
│   │   └── prompts.py   # System prompts
│   ├── mcp/             # MCP server implementation
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic
│   │   └── server.py    # MCP server
│   ├── api/             # FastAPI application
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # API services
│   │   └── app.py       # FastAPI app
│   └── templates/       # HTML templates
├── tests/               # Test suite
├── main.py              # Main entry point
├── .env                 # Environment variables
├── pyproject.toml       # Poetry configuration
└── README.md            # This file
```
