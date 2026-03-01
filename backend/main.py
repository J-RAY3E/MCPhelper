import os
import sys
import threading
import uvicorn
import inspect
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

# Add current directory to sys.path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
# Also add project root
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.llm_client import get_client
from core.planner import LLMPlanner
from core.validator import LLMPlanValidator
from core.executor import ToolExecutor
from core.summarizer import LLMSummarizer
from core.data_analyst import DataAnalyst
from core.agent_orchestrator import AgentOrchestrator
from tool_registry import register_tools
from mcp.server.fastmcp import FastMCP

# Import audio routes
from audio_routes import router as audio_router

app = FastAPI(title="MCPDESK Backend")

# Include audio routes
app.include_router(audio_router)

# Initialize core components
llm = get_client()
planner = LLMPlanner(llm)
validator = LLMPlanValidator(llm)
summarizer = LLMSummarizer(llm)

mcp = FastMCP("MCPDESK")
workspace_path = project_root
tool_instances = register_tools(mcp, workspace_path)
executor = ToolExecutor(tool_instances)

# Ensure storage exists
STORAGE_DIR = os.path.join(workspace_path, "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Initialize modular handlers
data_analyst = DataAnalyst(llm, STORAGE_DIR)

def get_tool_descriptions():
    """Build a text description of all registered tools."""
    descriptions = []
    for category, instance in tool_instances.items():
        for name, method in inspect.getmembers(instance, inspect.ismethod):
            if hasattr(method, '_is_tool') and method._is_tool:
                doc = inspect.getdoc(method) or "No description"
                sig = inspect.signature(method)
                params = str(sig)
                descriptions.append(f"- {name}{params}: {doc}")
    return "\n".join(descriptions)

orchestrator = AgentOrchestrator(llm, planner, executor, summarizer, get_tool_descriptions)

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def root():
    return {"status": "online", "name": "MCPDESK Backend"}

# ── File Upload with AI Classifier ─────────────────────────────────────────────

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to storage.
    The LLM classifies the file by name/extension and saves it into the
    appropriate subfolder (datasets/, finance/, documents/, reports/, other/).
    """
    contents = await file.read()
    filename = file.filename

    # AI-based file classification
    classification_prompt = (
        f"You are a file librarian. Classify this file into ONE of these categories: "
        f"'datasets', 'finance', 'documents', 'reports', 'other'. "
        f"Respond ONLY with that single category word — nothing else. File name: '{filename}'"
    )
    try:
        category = llm.chat([{"role": "user", "content": classification_prompt}])
        allowed = {"datasets", "finance", "documents", "reports", "other"}
        category = category.strip().lower().split()[0]
        if category not in allowed:
            category = "other"
    except Exception:
        category = "other"

    dest_dir = os.path.join(STORAGE_DIR, category)
    os.makedirs(dest_dir, exist_ok=True)
    file_path = os.path.join(dest_dir, filename)
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
        return {
            "status": "success",
            "filename": filename,
            "category": category,
            "path": os.path.relpath(file_path, STORAGE_DIR),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Hierarchical File Tree ──────────────────────────────────────────────────────

def _build_tree(directory: str, rel_base: str = "") -> list:
    """
    Recursively scan `directory` and return a list of nodes compatible with
    NiceGUI's ui.tree format: [{"id": ..., "label": ..., "children": [...]}, ...]
    Hidden directories (starting with '.') such as .cache are excluded.
    """
    nodes = []
    try:
        entries = sorted(
            os.scandir(directory),
            key=lambda e: (not e.is_dir(), e.name.lower())
        )
        for entry in entries:
            if entry.name.startswith("."):
                continue  # Skip .cache and other hidden dirs
            rel_path = os.path.join(rel_base, entry.name) if rel_base else entry.name
            if entry.is_dir():
                children = _build_tree(entry.path, rel_path)
                nodes.append({"id": rel_path, "label": entry.name, "children": children})
            else:
                nodes.append({"id": rel_path, "label": entry.name})
    except PermissionError:
        pass
    return nodes


@app.get("/files")
async def list_files():
    """Return a hierarchical file tree of storage/ (NiceGUI ui.tree compatible)."""
    tree = _build_tree(STORAGE_DIR)
    return {"tree": tree}


# ── Main Command Handler ────────────────────────────────────────────────────────

@app.post("/command")
async def handle_command(request: CommandRequest):
    """
    Handle commands from the frontend dynamically.
    Delegates strictly to modular components.
    """
    cmd = request.command.strip()

    try:
        # 1. IMMEDIATE ANALYTICAL CHECK (plain text, no slash)
        if not cmd.startswith("/") and len(cmd.split()) > 2:
            system_msg = "You are a Global Senior Intelligence Analyst. INTERPRET data, look for 'the why', and respond in professional Markdown."
            result = llm.chat([{"role": "system", "content": system_msg}, {"role": "user", "content": cmd}])
            return {"type": "text", "content": result, "mode": getattr(llm, "mode", "unknown")}

        # 2. DATA ANALYST (Pandas, Vega-Lite JSON logic)
        if cmd.startswith("/plot") or cmd.startswith("/describe"):
            return data_analyst.handle_data_command(cmd)

        # 3. AUTONOMOUS AGENT ORCHESTRATION (Planner -> Executor -> Summarizer)
        return await orchestrator.execute_query(cmd)

    except Exception as e:
        return {"type": "text", "content": f"**System Route Error:** {str(e)}"}


# ── Console & Server Bootstrap ──────────────────────────────────────────────────

def run_console():
    """Interactive console."""
    print("--- MCPDESK Console ---")
    while True:
        try:
            user_input = input("MCPDESK> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            import asyncio
            response = asyncio.run(orchestrator.execute_query(user_input))
            print(f"[{llm.mode.upper()}]\n{response.get('content')}")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    run_console()
