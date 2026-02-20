# 📔 Project Documentation: MCPDESK

## 1. Overview
MCPDESK is a market intelligence platform designed as a minimalist, interactive workspace. It combines the power of the Model Context Protocol (MCP) with an Obsidian-like notebook interface (Streamlit) and a robust processing backend (FastAPI).

Its goal is to enable analysts to perform complex tasks (scraping, plotting, modeling, and data cleaning) using simple commands (`/plot`, `/scrape`, `/upload`) that abstract away technical complexity.

## 2. Quick Start

Get MCPDESK running in less than 2 minutes:

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Backend:**
    ```bash
    python backend/main.py
    ```
    *(Note: This starts the API on port 8000 and an interactive terminal console)*

3.  **Start the Frontend:**
    In a new terminal, run:
    ```bash
    streamlit run frontend/app.py
    ```

4.  **Try it out:**
    - Go to the Streamlit URL (usually `http://localhost:8501`).
    - Upload a CSV file using the sidebar.
    - Type `/describe` in a cell and click **RUN COMMAND**.

## 3. System Architecture

MCPDESK follows a decoupled **Frontend** and **Backend** architecture:

### Frontend (Streamlit)
- **Directory:** `frontend/`
- **Interface:** Minimalist dark theme inspired by Obsidian.
- **Functionality:** 
    - Notebook cells for command execution.
    - Real-time command suggestions for slash commands (`/`).
    - Professional, clean action buttons and headers.
    - Rendering of Markdown, LaTeX, interactive tables, and charts.

### Backend (FastAPI + LLM Agent)
- **Directory:** `backend/`
- **Responsibility:** Process commands, interact with LLMs, and execute tools.
- **Key Components:**
    - `FastAPI Server`: Entry point for the frontend.
    - `LLM Client`: Abstraction layer with fallback (Local -> Gemini Cloud).
    - `MCP Server`: FastMCP implementation for dynamic tool registration.
    - `Command Handler`: Direct logic for data analysis (Pandas) and visualization.

## 4. Installation and Configuration

### Prerequisites
- Python 3.10+
- (Optional) LM Studio or Ollama for local LLM (OpenAI-compatible API).
- (Optional) Gemini API Key for cloud fallback.

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key.
- `LOCAL_LLM_URL`: URL of your local server (default: `http://localhost:8080/v1`).

## 5. Roadmap
- **Phase 3:** Integration of advanced `/plot` commands using Plotly.
- **Phase 4:** PDF Export and Report Generation.
- **Phase 5:** Multi-agent collaboration for complex market reports.
