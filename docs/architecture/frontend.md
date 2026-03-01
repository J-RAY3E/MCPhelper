# Frontend Components

The frontend is built with NiceGUI and follows a modular architecture.

## Module Structure

```
frontend/
├── app.py              # Main entry point
├── config/             # Configuration
│   ├── commands.py     # Slash commands definitions
│   └── settings.py     # App settings
├── state/              # State management
│   └── store.py        # Cell and global state
├── services/           # Backend communication
│   ├── backend.py      # API calls
│   └── voice.py        # Voice processing
└── components/         # UI components
    ├── cell.py         # Cell rendering
    ├── output.py       # Output rendering
    ├── autocomplete.py  # Command autocomplete
    └── sidebar.py      # File panel, upload
```

## Components

### app.py

Main application entry point:
- Initializes UI layout
- Imports all modules
- Runs NiceGUI server

### Components

#### cell.py
- `render_cells()`: Renders all cells
- `_render_cell()`: Renders individual cell
- `add_cell()`: Adds new cell
- `delete_cell()`: Removes cell

#### output.py
- `_render_output()`: Renders command output
  - Text output
  - Error display
  - Vega-Lite charts

#### autocomplete.py
- `on_input_change()`: Handles input changes
- `_rebuild_suggestions()`: Shows command suggestions
- `_insert_command()`: Inserts selected command

#### sidebar.py
- `refresh_files()`: Refreshes file tree
- `handle_upload()`: Handles file uploads

### Services

#### backend.py
- `get_files()`: Fetches file list
- `run_cell()`: Executes cell command

#### voice.py
- `start_voice()`: Starts recording
- `stop_voice()`: Stops recording
- `check_and_send_voice()`: Processes voice input
- `toggle_voice()`: Toggles recording state

## State Management

The state module (`store.py`) contains:
- `Cell` class: Represents a notebook cell
- `cells`: List of all cells
- `cells_container`: Reference to UI container
- `files_panel`: Reference to file panel
- `voice_btn`, `voice_status`: Voice UI references
