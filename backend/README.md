# 📓 MCP Helper - Backend

This is the central server for MCP Helper's market analysis.

## Features
- **FastAPI Server:** Exposes endpoints for the interactive frontend.
- **LLM Integration:** Abstraction layer with automatic fallback between local models (LM Studio/Ollama) and Gemini Cloud.
- **MCP Server:** Integrates Model Context Protocol tools for Claude and other compatible clients.
- **Console Mode:** Allows interaction with the system directly from the terminal at launch.

## How to run

1.  Make sure you set your environment variables if you plan to use Gemini:
    ```bash
    export GEMINI_API_KEY="your_key"
    ```

2.  Launch the backend:
    ```bash
    python backend/main.py
    ```
    *Note: This will start the server at `http://localhost:8000` and open an interactive console in the terminal.*

## Structure
- `/core`: Planning and processing logic.
- `/tools`: Implementation of system, navigation, and redaction tools.
- `/utils`: LLM clients and decorators.
- `/prompts`: Agent behavior definitions.
