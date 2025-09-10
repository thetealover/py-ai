# py-api

## Features

- **Backend:** FastAPI with Python 3.12
- **Conversational AI:** LangChain with LangGraph for stateful, multi-step agents.
- **LLM:** Google Gemini (`gemini-1.5-flash`)
- **Real-time Communication:** Server-Sent Events (SSE) for streaming LLM responses.
- **Dependency Management:** Poetry

## Setup

1. **Install Poetry:** If you don't have Poetry installed, follow the instructions on
   the [official website](https://python-poetry.org/docs/).

2. **Create `.env` file:** Create a `.env` file in the root of the project and add your API keys. You can get a Google
   API key from [Google AI for Developers](https://ai.google.dev/).

   ```
   GOOGLE_API_KEY="your_google_api_key_here"
   TAVILY_API_KEY="your_tavily_api_key_here"
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

## Running the Application

To run the FastAPI server, use the following command:

```shell script
poetry run uvicorn app.main:app --reload --port 8000
```

To run the MCP server, use the following command:

```shell script
poetry run python -m mcp_ws.server
``` 