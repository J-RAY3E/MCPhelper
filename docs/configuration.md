# Configuration Guide

MCPDESK can be configured through environment variables and configuration files.

## Environment Variables

### Required

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | None |

### Optional - LLM Providers

#### OpenAI (Default)
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

#### Azure OpenAI
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

#### Ollama (Local)
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### Anthropic Claude
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus
```

### Optional - Application

```env
# Storage
STORAGE_DIR=./storage

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

## File Configuration

### Storage Directory

Files are automatically organized into:
- `datasets/` - CSV and data files
- `finance/` - Financial data
- `documents/` - Text documents
- `reports/` - Generated reports
- `other/` - Uncategorized files

### Backend Configuration

In `backend/main.py`:
```python
# Server configuration
uvicorn.run(app, host="0.0.0.0", port=8000)

# Storage
STORAGE_DIR = os.path.join(workspace_path, "storage")
```

### Frontend Configuration

In `frontend/config/settings.py`:
```python
BACKEND_URL = "http://localhost:8000"
FRONTEND_PORT = 8501
```

## Tool Configuration

### Financial Tools

Configure API endpoints in `backend/tools/financial_tools.py`:
- Yahoo Finance (default, no key required)
- Alpha Vantage (optional, for premium data)

### Web Scraping

Configure user agents and rate limits in `backend/core/scraper.py`.

## Voice Assistant

### Whisper Model

Choose model size in `backend/audio/whisper_processor.py`:
- `tiny` - Fastest, lowest accuracy
- `base` - Balanced (default)
- `small` - Good accuracy
- `medium` - High accuracy
- `large` - Highest accuracy, slowest

### TTS Configuration

Configure voice and rate in `backend/audio/tts_processor.py`.
