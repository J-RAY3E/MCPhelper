import asyncio
import requests
from typing import List
from ..config.settings import BACKEND_URL
from ..state.store import Cell

HELP_TEXT = """
## 🤖 Guía del Asistente MCPDESK

Este asistente es un **Agente Autónomo** impulsado por Inteligencia Artificial.

### 📝 Comandos de Datos
- `/plot [archivo]`: Crea gráficos interactivos.
- `/describe [archivo]`: Estadísticas descriptivas.

### 📈 Comandos Financieros
- `/info [ticker]`: Información de la empresa.
- `/indicators [ticker]`: Indicadores técnicos.
- `/backtest [ticker]`: Backtest de estrategias.
- `/forecast [ticker]`: Predicción de precios.
- `/portfolio [tickers]`: Métricas de portfolio.
- `/sentiment [ticker]`: Análisis de sentimiento.
- `/crypto [moneda]`: Datos de criptomonedas.
- `/calendar`: Calendario económico.
- `/compare [tickers]`: Comparar acciones.
"""

def get_files() -> List[str]:
    try:
        r = requests.get(f"{BACKEND_URL}/files", timeout=5)
        if r.status_code == 200:
            return r.json().get("files", [])
    except Exception:
        pass
    return []

async def run_cell(cell: Cell):
    from nicegui import ui
    from ..components.output import _render_output
    
    if not cell.content.strip():
        return
    cell.running = True
    if cell._spinner_btn:
        cell._spinner_btn.clear()
        with cell._spinner_btn:
            ui.spinner(size="xs").props("color=green")
    if cell._output_area:
        cell._output_area.set_visibility(False)
        cell._output_area.clear()
    if cell.content.strip().startswith("/help"):
        cell.result = {"type": "text", "content": HELP_TEXT}
    else:
        try:
            resp = await asyncio.to_thread(
                requests.post,
                f"{BACKEND_URL}/command",
                json={"command": cell.content},
                timeout=120,
            )
            cell.result = resp.json() if resp.status_code == 200 else {
                "type": "error", "content": resp.text
            }
        except requests.exceptions.Timeout:
            cell.result = {"type": "error", "content": "timeout — backend tardó demasiado"}
        except Exception as e:
            cell.result = {"type": "error", "content": str(e)}
    cell.running = False
    if cell._spinner_btn:
        cell._spinner_btn.clear()
        with cell._spinner_btn:
            ui.icon("play_arrow", size="xs")
    if cell._output_area and cell.result:
        cell._output_area.clear()
        with cell._output_area:
            _render_output(cell.result)
        cell._output_area.set_visibility(True)
