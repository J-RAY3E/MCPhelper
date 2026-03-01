import json
from nicegui import ui

def _render_output(result: dict):
    rtype   = result.get("type", "text")
    content = result.get("content", "")
    
    if rtype == "error":
        ui.html(f'<pre class="text-red-400 text-xs whitespace-pre-wrap font-mono">{content}</pre>')
    elif rtype == "mixed":
        for item in result.get("items", []):
            if item.get("type") == "text":
                ui.markdown(item.get("content","")).classes("text-slate-300 text-sm markdown-body")
            elif item.get("type") == "vega_lite":
                chart_container = ui.element('div').classes("w-full mt-4 h-[400px]")
                spec = item.get("spec", {})
                spec["data"] = {"values": item.get("data", [])}
                spec["width"] = "container"
                spec["height"] = 300
                spec["autosize"] = {"type": "fit", "contains": "padding"}
                spec["background"] = "transparent"
                spec["config"] = {
                    "axis": {"domainColor": "#334155", "gridColor": "#1e293b", "tickColor": "#334155", "labelColor": "#94a3b8", "titleColor": "#cbd5e1"},
                    "legend": {"labelColor": "#94a3b8", "titleColor": "#cbd5e1"},
                    "title": {"color": "#cbd5e1"},
                    "view": {"stroke": "transparent"}
                }
                spec_json = json.dumps(spec)
                ui.run_javascript(f'''
                    setTimeout(() => {{
                        vegaEmbed("div[id='c{chart_container.id}']", {spec_json}, {{"actions": false, "theme": "dark"}});
                    }}, 100);
                ''')
    else:
        ui.markdown(content).classes("text-slate-300 text-sm markdown-body")
