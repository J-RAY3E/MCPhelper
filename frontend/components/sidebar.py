import asyncio
import requests
from nicegui import ui
from nicegui.events import UploadEventArguments
from ..config.settings import BACKEND_URL
from ..state.store import files_panel as _global_files_panel

def refresh_files(panel=None):
    panel = panel or _global_files_panel
    if panel is None:
        return
    try:
        r = requests.get(f"{BACKEND_URL}/files", timeout=5)
        tree_nodes = r.json().get("tree", []) if r.status_code == 200 else []
    except Exception:
        tree_nodes = []

    panel.clear()
    with panel:
        if tree_nodes:
            ui.tree(
                nodes=tree_nodes,
                node_key="id",
                label_key="label",
                children_key="children",
            ).classes("text-slate-400 text-xs font-mono w-full")
        else:
            ui.label("empty").classes("text-xs font-mono text-slate-600 italic")

async def handle_upload(e: UploadEventArguments):
    try:
        files = {"file": (e.name, e.content.read(), "application/octet-stream")}
        resp = await asyncio.to_thread(
            requests.post, f"{BACKEND_URL}/upload", files=files, timeout=60
        )
        if resp.status_code == 200:
            category = resp.json().get("category", "other")
            ui.notify(f"✅ {e.name} → 📂 {category}/", type="positive", position="top-right")
        else:
            ui.notify(f"❌ Upload failed: {resp.text}", type="negative", position="top-right")
        refresh_files()
    except Exception as ex:
        ui.notify(str(ex), type="negative", position="top-right")
