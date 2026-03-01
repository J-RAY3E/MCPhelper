# Architecture Overview

MCPDESK follows a client-server architecture with modular components.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (NiceGUI Frontend)                        │
│   ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐    │
│   │  Cells  │  │  Voice  │  │  Files   │  │ Output   │    │
│   └────┬────┘  └────┬────┘  └────┬─────┘  └────┬─────┘    │
└────────┼────────────┼────────────┼─────────────┼───────────┘
         │            │            │             │
         └────────────┴────────────┴─────────────┘
                           │
                    HTTP/REST API
                           │
         ┌─────────────────┴─────────────────┐
         │                                    │
    ┌────┴────┐                         ┌────┴────┐
    │ Backend │                         │  Agent  │
    │  FastAPI│                         │Pipeline │
    └────┬────┘                         └────┬────┘
         │                                    │
    ┌────┴──────────────────────┐       ┌────┴────┐
    │     Tool Registry         │       │  Tools  │
    │  ┌──────┐ ┌───────────┐  │       │ ┌────┐  │
    │  │System│ │ Financial │  │       │ │... │  │
    │  └──────┘ └───────────┘  │       │ └────┘  │
    │  ┌──────────┐ ┌───────┐ │       └─────────┘
    │  │ Navigation│ │Audio  │ │
    │  └──────────┘ └───────┘ │
    └─────────────────────────┘
```

## Component Description

### Frontend (NiceGUI)

The frontend provides a notebook-style interface with:
- Interactive cells for command input
- Voice input via WebAudio API
- Real-time output rendering
- File browser with tree view

### Backend (FastAPI)

The backend handles:
- HTTP request routing
- File upload/classification
- Agent orchestration
- Tool registration and execution

### Agent Pipeline

The core AI system consists of:

1. **Planner**: Decomposes user queries into executable steps
2. **Validator**: Validates the plan is safe and feasible
3. **Executor**: Executes tools and gathers results
4. **Summarizer**: Generates natural language responses

### Tool System

Tools are registered via FastMCP and include:
- **System**: File operations, code execution
- **Financial**: Stock data, indicators, backtesting
- **Navigation**: Web scraping, content extraction
- **Redaction**: Document processing

## Data Flow

1. User enters command in frontend
2. Frontend sends POST to `/command`
3. Backend determines routing:
   - Data commands → DataAnalyst
   - Agent commands → Orchestrator
4. Orchestrator runs: Plan → Validate → Execute → Summarize
5. Response returned to frontend
6. Frontend renders output (text/charts)
