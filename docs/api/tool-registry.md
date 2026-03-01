# Tool Registry

The tool registry automatically discovers and registers tools with the FastMCP server.

## How It Works

1. Tools are defined as classes with decorated methods
2. The registry scans for the `@tool()` decorator
3. Each tool is registered with FastMCP
4. Tools become available to the agent pipeline

## Tool Decorator

Use the `@tool()` decorator from `backend/utils/tool_decorator.py`:

```python
from utils.tool_decorator import tool

class MyTools:
    @tool()
    def my_function(self, param: str) -> str:
        """Description of what this tool does"""
        return f"Result: {param}"
```

## Available Tools

### System Tools

- `read_file(path)`: Read file contents
- `write_file(path, content)`: Write to file
- `list_directory(path)`: List directory contents
- `execute_code(code)`: Run Python code

### Financial Tools

- `get_stock_info(ticker)`: Get company info
- `get_indicators(ticker)`: Get technical indicators
- `backtest_strategy(ticker)`: Backtest trading strategy
- `get_sentiment(ticker)`: Get news sentiment

### Navigation Tools

- `scrape_url(url)`: Extract content from URL
- `search_web(query)`: Search the web

### Redaction Tools

- `redact_text(text)`: Redact sensitive information
- `extract_text(file)`: Extract text from documents

## Registration

Tools are registered in `backend/tool_registry.py`:

```python
from tools.system_tools import SystemTools
from tools.financial_tools import FinancialTools

def register_tools(mcp: FastMCP, base_path: str):
    system_tools = SystemTools(allowed_base_path=base_path)
    financial_tools = FinancialTools()
    
    # Tools are automatically discovered
    return tool_instances
```
