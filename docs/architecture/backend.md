# Backend Components

## Core Modules

### agent_orchestrator.py

The main orchestration engine that coordinates the agent pipeline.

**Key functions:**
- `execute_query()`: Main entry point for query processing
- Coordinates Planner → Validator → Executor → Summarizer

### planner.py

Task planning using LLM.

**Key functions:**
- `create_plan()`: Decomposes user query into steps
- Uses prompt engineering to generate executable plans

### validator.py

Plan validation and safety checks.

**Key functions:**
- `validate_plan()`: Ensures plan is safe and feasible
- Checks for dangerous operations

### executor.py

Tool execution engine.

**Key functions:**
- `execute_plan()`: Runs the validated plan
- Handles tool invocation and error recovery

### summarizer.py

Response generation.

**Key functions:**
- `summarize()`: Generates natural language response from tool results

### data_analyst.py

Data analysis with pandas and visualization.

**Key functions:**
- `handle_data_command()`: Routes data commands
- `plot_data()`: Creates Vega-Lite charts
- `describe_data()`: Generates statistics

## Tool Modules

### tool_registry.py

Discovers and registers all tools with FastMCP.

### system_tools.py

File and system operations:
- `read_file()`: Read file contents
- `write_file()`: Write to files
- `list_directory()`: List directory contents
- `execute_code()`: Run Python code

### financial_tools.py

Financial data and analysis:
- `get_stock_info()`: Company information
- `get_indicators()`: Technical indicators (SMA, EMA, RSI, MACD)
- `backtest_strategy()`: Trading backtesting
- `get_sentiment()`: News sentiment analysis

### navigation_tools.py

Web navigation:
- `scrape_url()`: Extract content from URLs
- `search_web()`: Web search functionality

### redactor_tools.py

Document processing:
- `redact_text()`: Text redaction
- `extract_text()`: Extract text from documents
