"""
Agent Orchestrator

Coordinador principal del flujo autónomo: Planner -> Executor -> Summarizer.
Esta clase abstrae la ejecución de los agentes del enrutador FastAPI.
"""
import sys
import json
from typing import Dict, Any

class AgentOrchestrator:
    def __init__(self, llm, planner, executor, summarizer, get_tools_desc_func):
        self.llm = llm
        self.planner = planner
        self.executor = executor
        self.summarizer = summarizer
        self.get_tools_desc_func = get_tools_desc_func

    async def execute_query(self, cmd: str) -> Dict[str, Any]:
        """
        Ejecuta el ciclo de inteligencia para responder a una consulta en lenguaje natural 
        o comandos financieros usando herramientas dinámicamente.
        """
        try:
            # Step 0: Pre-process query to resolve tickers
            sys.stderr.write(f"[PRE-PROCESS] Resolving company names to tickers...\n")
            ticker_prompt = f"Rewrite this query by replacing any company name with its exact stock ticker (e.g. Apple -> AAPL, Microsoft -> MSFT). If there are no company names, output the original query exactly as is. ONLY OUTPUT THE REWRITTEN QUERY:\n{cmd}"
            resolved_cmd = self.llm.chat([{"role": "user", "content": ticker_prompt}]).strip()
            sys.stderr.write(f"[PRE-PROCESS] Resolved query: {resolved_cmd}\n")

            # Step 1: Get plan from Planner
            sys.stderr.write(f"[PLANNER] Analyzing request: {resolved_cmd}\n")
            plan_str = await self.planner.plan(resolved_cmd, self.get_tools_desc_func())
            
            # Clean possible markdown formatting from the plan
            plan_str = plan_str.replace("```json", "").replace("```", "").strip()
            
            try:
                plan = json.loads(plan_str)
            except json.JSONDecodeError:
                # If planner fails to make JSON, maybe it just answered directly
                return {"type": "text", "content": plan_str, "mode": getattr(self.llm, "mode", "unknown")}
            
            # Step 2: Execute tools
            if not isinstance(plan, list) or len(plan) == 0:
                pass # empty plan, skipping to fallback
            elif plan[0].get("tool") is None:
                # The planner decided no tools are needed, and returned a direct response
                return {"type": "text", "content": plan[0].get("response", "No response generated.")}
            else:
                sys.stderr.write(f"[EXECUTOR] Running {len(plan)} steps...\n")
                results = await self.executor.execute(plan) 
                
                # Step 3: Summarize
                sys.stderr.write(f"[SUMMARIZER] Generating report...\n")
                final_report = await self.summarizer.summarize(cmd, results)
                return {
                    "type": "text", 
                    "content": final_report, 
                    "mode": getattr(self.llm, "mode", "unknown")
                }

            # If we fall through, just send directly to LLM
            result = self.llm.chat([{"role": "user", "content": cmd}])
            return {
                "type": "text", 
                "content": result, 
                "mode": getattr(self.llm, "mode", "unknown")
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"type": "text", "content": f"**Agent Execution Error:** {str(e)}"}
