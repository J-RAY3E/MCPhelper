# Adding Frontend Components

This guide explains how to add new UI components to the MCPDESK frontend.

## Module Structure

The frontend is organized as:

```
frontend/
├── app.py              # Entry point
├── config/             # Configuration
├── state/              # State management  
├── services/           # Backend communication
└── components/        # UI components
```

## Creating a New Component

### Step 1: Create Component File

Create `frontend/components/my_component.py`:

```python
from nicegui import ui

def my_component(param: str):
    """Description of the component"""
    with ui.card():
        ui.label(f"Hello {param}")
```

### Step 2: Export from __init__.py

Add to `frontend/components/__init__.py`:

```python
from .my_component import my_component
```

### Step 3: Use in app.py

Import and use in `frontend/app.py`:

```python
from components import my_component

# Use in layout
my_component("World")
```

## Component Patterns

### With State

```python
from nicegui import ui

def interactive_component(value=[None]):
    """Component with internal state"""
    with ui.row():
        ui.label("Counter:")
        ui.label(str(value[0] or 0))
        
        def increment():
            value[0] = (value[0] or 0) + 1
        
        ui.button("Add", on_click=increment)
```

### With Callbacks

```python
def component_with_callback(on_change=None):
    """Component that calls back"""
    def handle_change(e):
        if on_change:
            on_change(e.value)
    
    ui.input(on_change=handle_change)
```

## Adding Services

### Backend Communication

Create `frontend/services/my_service.py`:

```python
import requests
from config.settings import BACKEND_URL

def call_backend(param: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/endpoint",
        json={"param": param}
    )
    return response.json()
```

## State Management

For components that need persistent state:

```python
# In state/store.py
my_state = {"value": None}

# In component
from state.store import my_state

def my_component():
    ui.label(str(my_state["value"]))
```

## Best Practices

1. **Modular**: Keep components focused
2. **Reusable**: Make components configurable
3. **Styled**: Use existing CSS classes
4. **Responsive**: Consider different screen sizes
5. **Accessible**: Add proper labels and hints
