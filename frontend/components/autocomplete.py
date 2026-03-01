from nicegui import ui
from ..config.commands import SLASH_COMMANDS
from ..state.store import Cell

def on_input_change(e, cell: Cell):
    cell.content = e.value
    panel = cell._suggestion_panel
    if panel is None:
        return
    words     = cell.content.split()
    last_word = words[-1] if words else ""
    if last_word.startswith("/") and len(last_word) >= 1:
        matches = {k: v for k, v in SLASH_COMMANDS.items() if k.startswith(last_word)}
        if matches:
            _rebuild_suggestions(panel, matches, cell)
            panel.set_visibility(True)
            return
    panel.set_visibility(False)

def _rebuild_suggestions(panel, matches: dict, cell: Cell):
    panel.clear()
    with panel:
        for cmd, desc in list(matches.items())[:8]:
            with ui.row().classes(
                "items-center gap-3 px-3 py-2 cursor-pointer w-full rounded"
                " hover:bg-slate-800 transition-colors duration-100"
            ) as row:
                ui.label(cmd).classes("text-emerald-400 font-mono text-sm w-28 shrink-0")
                ui.label(desc).classes("text-slate-500 text-xs truncate")
            row.on("click", lambda _e, c=cmd, ce=cell: _insert_command(c, ce))

def _insert_command(cmd: str, cell: Cell):
    words = cell.content.split()
    if words:
        words[-1] = cmd
        cell.content = " ".join(words) + " "
    else:
        cell.content = cmd + " "
    if cell._textarea:
        cell._textarea.set_value(cell.content)
    if cell._suggestion_panel:
        cell._suggestion_panel.set_visibility(False)
