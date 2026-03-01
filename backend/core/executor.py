import asyncio
import inspect
import sys
import json
from typing import List, Dict, Any, Optional
from core.interfaces import BaseExecutor

class ToolExecutor(BaseExecutor):
    """Executes a validated plan using available tool instances."""
    
    def __init__(self, tool_instances: Dict[str, Any]):
        self.tool_instances = tool_instances
        self.results_cache = []

    def _find_tool(self, tool_name: str):
        """Finds a tool method by name across all registered instances."""
        if not tool_name or not isinstance(tool_name, str):
            return None
            
        for instance in self.tool_instances.values():
            for name, method in inspect.getmembers(instance, inspect.ismethod):
                if name == tool_name:
                    return method
        return None

    async def execute(self, plan: List[Dict[str, Any]]) -> List[str]:
        """
        Executes each step in the plan sequentially.
        """
        self.results_cache = []
        last_result = ""

        # Ensure plan is a list
        if not isinstance(plan, list):
            return ["Error: Invalid plan format. Expected a list of steps."]

        for step in plan:
            # Safety check: if step is not a dict, skip it
            if not isinstance(step, dict):
                continue

            tool_name = step.get("tool")
            args = step.get("args", {})
            
            if not tool_name or tool_name == "step": # Blindaje contra el error 'step'
                continue

            # Substitute PREVIOUS_RESULT
            processed_args = {}
            if isinstance(args, dict):
                for k, v in args.items():
                    if isinstance(v, str) and "PREVIOUS_RESULT" in v:
                        processed_args[k] = v.replace("PREVIOUS_RESULT", str(last_result))
                    else:
                        processed_args[k] = v
            else:
                processed_args = {}

            tool_method = self._find_tool(tool_name)
            if not tool_method:
                error_msg = f"Error: Tool '{tool_name}' not found."
                self.results_cache.append(error_msg)
                last_result = error_msg
                continue

            try:
                if asyncio.iscoroutinefunction(tool_method):
                    result = await tool_method(**processed_args)
                else:
                    result = tool_method(**processed_args)
                
                self.results_cache.append(str(result))
                last_result = result
            except Exception as e:
                error_msg = f"Error executing {tool_name}: {str(e)}"
                self.results_cache.append(error_msg)
                last_result = error_msg

        return self.results_cache
