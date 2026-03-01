import asyncio
from nicegui import ui
from ..state.store import cells, Cell, cells_container as _global_cells_container
from ..services.backend import run_cell
from .autocomplete import on_input_change
from .output import _render_output

def render_cells(container=None):
    container = container or _global_cells_container
    if container is None:
        return
    container.clear()
    with container:
        for idx, cell in enumerate(cells):
            _render_cell(idx, cell)
        ab = ui.button(on_click=add_cell).props("flat dense").classes(
            "text-slate-700 hover:text-emerald-500 font-mono text-xs mt-2"
        )
        with ab:
            ui.icon("add", size="xs")
            ui.label("nueva celda").classes("ml-1")
        ab.tooltip("Añadir celda")

def _render_cell(idx: int, cell: Cell):
    with ui.element("div").classes("w-full mb-4"):
        with ui.row().classes("w-full items-start gap-2"):
            with ui.column().classes("items-center gap-1 pt-1 w-8 shrink-0"):
                ui.label(f"{idx:02d}").classes(
                    "text-xs font-mono text-slate-700 select-none leading-none"
                )
                btn = ui.button(
                    on_click=lambda c=cell: asyncio.create_task(run_cell(c))
                ).props("flat dense round").classes("text-emerald-600 hover:text-emerald-300")
                with btn:
                    ui.icon("play_arrow", size="xs")
                btn.tooltip("Ejecutar")
                cell._spinner_btn = btn
            with ui.column().classes("flex-1 gap-0"):
                ta = ui.textarea(
                    value=cell.content,
                    on_change=lambda e, c=cell: on_input_change(e, c),
                    placeholder="mensaje o /comando…",
                ).classes("w-full font-mono text-sm text-slate-200").style(
                    "background:transparent;"
                    "border:none;"
                    "border-bottom:1px solid #1e293b;"
                    "border-radius:0;"
                    "padding:4px 0;"
                    "resize:none;"
                ).props("borderless autogrow rows=1")
                cell._textarea = ta
                panel = ui.element("div").classes(
                    "w-full rounded-b overflow-hidden"
                ).style(
                    "background:#0d1117;"
                    "border:1px solid #1e293b;"
                    "border-top:none;"
                )
                cell._suggestion_panel = panel
                panel.set_visibility(False)
            if len(cells) > 1:
                db = ui.button(
                    on_click=lambda c=cell: delete_cell(c.id)
                ).props("flat dense round").classes(
                    "text-slate-800 hover:text-red-500 mt-1 shrink-0"
                )
                with db:
                    ui.icon("close", size="xs")
                db.tooltip("Eliminar celda")
        out = ui.element("div").classes(
            "ml-10 mt-1 px-3 py-2 rounded"
            " bg-slate-900 border-l-2 border-emerald-900 w-full"
        )
        cell._output_area = out
        if cell.result:
            with out:
                _render_output(cell.result)
        else:
            out.set_visibility(False)

def add_cell():
    cells.append(Cell())
    render_cells()

def delete_cell(cell_id: int):
    if len(cells) > 1:
        cells[:] = [c for c in cells if c.id != cell_id]
        render_cells()
