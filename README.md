# MCPDESK

An autonomous AI-powered desktop assistant that combines a modern notebook interface with intelligent agent orchestration. MCPDESK leverages Large Language Models to understand natural language commands, execute complex tasks, and provide data analysis capabilities.

## Features

### Core Capabilities
- **Natural Language Interface**: Execute commands using natural language or slash commands
- **Autonomous Agent Orchestration**: Multi-stage agent pipeline (Plan → Validate → Execute → Summarize)
- **Data Analysis**: Built-in pandas integration for CSV analysis, visualization with Vega-Lite charts
- **File Management**: AI-powered file classification and hierarchical file browser

### Tools & Integrations
- **System Tools**: File operations, code execution, system commands
- **Financial Tools**: Stock data, technical indicators, backtesting, sentiment analysis
- **Navigation Tools**: Web scraping, content extraction
- **Redaction Tools**: Document processing and text manipulation

### User Interface
- **Notebook-style Frontend**: Interactive cells with autocomplete for commands
- **Voice Assistant**: Voice input using WebAudio API and Whisper transcription
- **Real-time Updates**: Live execution status and output streaming
- **Dark Theme**: Professional dark mode interface

## Architecture

```
MCPDESK/
├── backend/              # FastAPI backend server
│   ├── core/            # Agent orchestration components
│   │   ├── planner.py          # LLM-powered task planning
│   │   ├── validator.py       # Plan validation
│   │   ├── executor.py         # Tool execution engine
│   │   ├── summarizer.py      # Response generation
│   │   └── data_analyst.py    # Data analysis module
│   ├── tools/           # Tool implementations
│   │   ├── system_tools.py
│   │   ├── financial_tools.py
│   │   ├── navigation_tools.py
│   │   └── redaction_tools.py
│   ├── audio/           # Audio processing
│   │   ├── whisper_processor.py
│   │   ├── tts_processor.py
│   │   └── audio_recorder.py
│   ├── prompts/         # LLM prompt templates
│   ├── utils/           # Utilities
│   └── main.py          # Entry point
├── frontend/            # NiceGUI frontend
│   ├── app.py           # Main application
│   ├── config/          # Configuration
│   ├── components/      # UI components
│   ├── services/        # Backend communication
│   ├── state/           # State management
│   └── audio/           # Audio components
└── storage/             # User data storage
```

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key (or compatible LLM endpoint)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd MCPDESK
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
Create a `.env` file in the project root:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here

# Optional: Use Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_KEY=your_key

# Optional: Use Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Running the Application

1. **Start the Backend Server** (Terminal 1)
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`

2. **Start the Frontend** (Terminal 2)
```bash
cd frontend
python app.py
```
The UI will open at `http://localhost:8501`

### Usage

#### Basic Commands
- **Plain text queries**: Ask questions in natural language
- `/help`: Show available commands
- `/plot [file]`: Create interactive charts from CSV
- `/describe [file]`: Show dataset statistics

#### Financial Commands
- `/info [ticker]`: Company information (e.g., `/info AAPL`)
- `/indicators [ticker]`: Technical indicators (SMA, EMA, RSI, MACD)
- `/backtest [ticker]`: Trading strategy backtesting
- `/forecast [ticker]`: Price prediction
- `/sentiment [ticker]`: News sentiment analysis
- `/crypto [symbol]`: Cryptocurrency data
- `/compare [tickers]`: Compare multiple stocks

#### Voice Commands
Click the microphone button to use voice input. Speech is transcribed via Whisper and executed as a command.

## Configuration

### Backend Port
Modify in `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Frontend Port
Modify in `frontend/app.py`:
```python
ui.run(port=8501, ...)
```

### Storage Directory
Default: `./storage`. Files are automatically organized into:
- `datasets/`: CSV and data files
- `finance/`: Financial data
- `documents/`: Text documents
- `reports/`: Generated reports
- `other/`: Uncategorized files

## Development

### Adding New Tools

1. Create a new tool class in `backend/tools/`
2. Use the `@tool()` decorator:
```python
from utils.tool_decorator import tool

class MyTools:
    @tool()
    def my_function(self, param: str) -> str:
        """Description of what this tool does"""
        return f"Result: {param}"
```

3. Register in `backend/tool_registry.py`

### Adding New Frontend Components

1. Create component in `frontend/components/`
2. Export from `frontend/components/__init__.py`
3. Import in `frontend/app.py`

## License

MIT License

## Acknowledgments

- [NiceGUI](https://nicegui.io/) - UI Framework
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP Server
- [OpenAI](https://openai.com/) - LLM Provider
- [Whisper](https://github.com/openai/whisper) - Speech Recognition
