"""
MCPDESK Frontend - NiceGUI (Refactorizado v0.5)
"""
import sys
import os
from nicegui import ui

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.config import BACKEND_URL
from frontend.state import voice_btn, voice_status
from frontend.services import start_voice, stop_voice, toggle_voice
from frontend.components import render_cells, refresh_files, handle_upload

ui.dark_mode(True)

ui.add_head_html("""
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
<script>window.voiceAssistant = { isRecording: false };</script>
<style>
  body, .nicegui-content { background: #080b0f !important; }
  textarea { background: transparent !important; color: #cbd5e1 !important; caret-color: #10b981; }
  textarea::placeholder { color: #1e293b !important; }
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: #080b0f; }
  ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 2px; }
  .markdown-body h1, .markdown-body h2, .markdown-body h3 { color: #cbd5e1 !important; margin-top: 0.5em; margin-bottom: 0.5em; border: none; padding-bottom: 0; }
  .markdown-body p { margin-bottom: 0.5em; }
  .markdown-body code { background-color: #1e293b !important; color: #38bdf8 !important; }
  .markdown-body pre { background-color: #0f172a !important; border: 1px solid #1e293b; }
</style>
""")

with ui.row().classes("w-full min-h-screen").style("background:#080b0f"):
    with ui.column().classes("shrink-0 h-screen sticky top-0 flex flex-col").style(
        "width:200px;background:#0d1117;border-right:1px solid #1e293b;padding:16px 12px;"
    ):
        ui.label("MCPDESK").classes("text-emerald-400 font-mono font-bold text-base tracking-widest mb-6")
        
        ui.label("VOICE").classes("text-slate-700 font-mono text-[10px] tracking-widest uppercase mb-2")
        voice_btn = ui.button('🎤 Escuchar', on_click=toggle_voice, icon='mic').props("round color=primary").classes("w-full mb-2")
        voice_btn.tooltip("Click para hablar")
        voice_status = ui.label("🎤 Escuchar").classes("text-xs text-slate-600 font-mono mb-4")
        
        ui.separator().classes("my-3")
        ui.label("FILES").classes("text-slate-700 font-mono text-[10px] tracking-widest uppercase mb-2")
        files_panel = ui.column().classes("w-full mb-4 gap-0")
        refresh_files(files_panel)
        
        ui.label("UPLOAD").classes("text-slate-700 font-mono text-[10px] tracking-widest uppercase mb-2")
        upl = ui.upload(on_upload=handle_upload, multiple=False).props("flat dense accept='.csv,.json,.txt,.xlsx'").classes("text-xs text-slate-600 w-full")
        upl.tooltip("CSV · JSON · TXT · XLSX")
        
        ui.space()
        ui.label("v0.5 · modular").classes("text-slate-800 font-mono text-[10px]")

    with ui.column().classes("flex-1 overflow-y-auto").style("padding:24px 32px"):
        with ui.row().classes("items-baseline gap-3 mb-6"):
            ui.label("notebook").classes("text-slate-200 font-mono font-bold text-2xl")
            ui.label("/ session").classes("text-slate-700 font-mono text-sm")
        cells_container = ui.column().classes("w-full max-w-3xl gap-0")
        render_cells(cells_container)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="MCPDESK", port=8501, reload=False, show=True, dark=True, favicon="◈")
