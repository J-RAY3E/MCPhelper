# Adding New Tools

This guide explains how to add new tools to MCPDESK.

## Step 1: Create Tool Class

Create a new file in `backend/tools/`:

```python
# backend/tools/my_tools.py
from utils.tool_decorator import tool

class MyTools:
    def __init__(self, config=None):
        self.config = config or {}
    
    @tool()
    def my_function(self, param: str) -> str:
        """Description of what this tool does"""
        # Tool implementation
        return f"Result: {param}"
    
    @tool()
    async def async_function(self, query: str) -> str:
        """Description of async tool"""
        # Async implementation
        return f"Async result: {query}"
```

## Step 2: Register Tool

Add to `backend/tool_registry.py`:

```python
from tools.my_tools import MyTools

def register_tools(mcp: FastMCP, base_path: str):
    my_tools_instance = MyTools(config={...})
    
    tool_instances = {
        # ... existing tools
        "my_tools": my_tools_instance,
    }
    
    # Registration happens automatically
    return tool_instances
```

## Tool Decorator

The `@tool()` decorator marks methods as tools:

```python
@tool()
def function_name(self, param: str) -> str:
    """This description is shown to the LLM"""
    return result
```

## Best Practices

1. **Clear descriptions**: Write clear docstrings
2. **Type hints**: Use type hints for parameters
3. **Error handling**: Handle errors gracefully
4. **Async support**: Use async for I/O operations
5. **Validation**: Validate input parameters

## Testing

Test your tool:

```python
from tools.my_tools import MyTools

tools = MyTools()
result = tools.my_function("test")
print(result)
```
