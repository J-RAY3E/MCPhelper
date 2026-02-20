import os
import sys
import asyncio
import threading
import uvicorn
import pandas as pd
import io
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

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
from tool_registry import register_tools
from mcp.server.fastmcp import FastMCP

app = FastAPI(title="MCP Helper Backend")

# Initialize core components
llm = get_client()
planner = LLMPlanner(llm)
mcp = FastMCP("MCP-Helper")
workspace_path = project_root
register_tools(mcp, workspace_path)

# Ensure storage exists
STORAGE_DIR = os.path.join(workspace_path, "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def root():
    return {"status": "online", "message": "MCP Helper Backend is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the storage directory."""
    file_path = os.path.join(STORAGE_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/command")
async def handle_command(request: CommandRequest):
    """Handle commands from the frontend."""
    cmd = request.command.strip()
    
    try:
        if cmd.startswith("/describe"):
            # Format: /describe [filename.csv]
            parts = cmd.split()
            filename = parts[1] if len(parts) > 1 else None
            
            if not filename:
                # Try to find the latest CSV in storage
                csv_files = [f for f in os.listdir(STORAGE_DIR) if f.endswith(".csv")]
                if not csv_files:
                    return {"type": "text", "content": "Error: No hay archivos CSV en storage."}
                filename = csv_files[0]
            
            file_path = os.path.join(STORAGE_DIR, filename)
            if not os.path.exists(file_path):
                return {"type": "text", "content": f"Error: El archivo {filename} no existe."}
            
            df = pd.read_csv(file_path)
            description = df.describe().reset_index().to_json(orient="records")
            
            return {
                "type": "mixed",
                "items": [
                    {"type": "text", "content": f"### Estadísticas de `{filename}`\nAquí tienes el resumen descriptivo del dataset:"},
                    {"type": "table", "content": description}
                ]
            }

        elif cmd.startswith("/plot"):
            # Format: /plot line from [filename.csv]
            # Simple implementation for MVP
            csv_files = [f for f in os.listdir(STORAGE_DIR) if f.endswith(".csv")]
            if not csv_files:
                return {"type": "text", "content": "Error: No hay archivos CSV para graficar."}
            
            filename = csv_files[0] # Take first for simplicity
            file_path = os.path.join(STORAGE_DIR, filename)
            df = pd.read_csv(file_path)
            
            # Use numeric columns for charting
            numeric_df = df.select_dtypes(include=['number'])
            if numeric_df.empty:
                return {"type": "text", "content": "Error: No hay columnas numéricas para graficar."}
            
            chart_data = numeric_df.to_json(orient="records")
            
            return {
                "type": "mixed",
                "items": [
                    {"type": "text", "content": f"### Gráfico de `{filename}`\nVisualizando columnas numéricas:"},
                    {"type": "chart", "content": chart_data}
                ]
            }

        else:
            # Enhanced LLM prompt for Markdown/LaTeX
            system_msg = (
                "You are an expert market analyst. "
                "Always respond using Markdown. "
                "When expressing formulas, statistics, or complex symbols, use LaTeX (e.g., $E=mc^2$ or $\mu = \\frac{\sum X}{N}$). "
                "Be concise and professional."
            )
            result = llm.chat([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": cmd}
            ])
            return {"type": "text", "content": result}
            
    except Exception as e:
        return {"type": "text", "content": f"**Error:** {str(e)}"}

def run_console():
    """Interactive console for local testing."""
    print("--- MCP Helper Console Mode ---")
    print("Type 'exit' to quit.")
    while True:
        try:
            user_input = input("MCP> ")
            if user_input.lower() in ["salir", "exit", "quit"]:
                break
            
            # Simplified for console
            response = llm.chat([{"role": "user", "content": user_input}])
            print(f"[{llm.mode.upper()}] Response: {response}")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

def start_api():
    """Run the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Start API in a background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Run console in main thread
    run_console()
