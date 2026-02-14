"""Tool Executor implementation."""
from typing import List, Dict, Any

from core.interfaces import BaseExecutor


class ToolExecutor(BaseExecutor):
    """Executes tool calls via MCP session."""
    
    async def execute(self, plan: List[Dict[str, Any]], session) -> List[str]:
        """
        Execute each step in the plan.
        Handles PREVIOUS_RESULT injection.
        """
        results = []
        last_result = ""
        
        for step in plan:
            step_num = step.get("step", "?")
            tool_name = step.get("tool")
            tool_args = step.get("args", {})
            description = step.get("description", "")
            
            # Direct response (no tool)
            if tool_name is None or tool_name == "null":
                response_text = step.get("response", description)
                print(f"  [{step_num}] 💬 {response_text}")
                results.append(response_text)
                last_result = response_text
                continue
            
            # PREVIOUS_RESULT Injection
            for key, value in tool_args.items():
                if value == "PREVIOUS_RESULT":
                    tool_args[key] = f"Content from previous step:\n{last_result}"
            
            # Tool execution
            print(f"  [{step_num}] ⚡ {tool_name}({str(tool_args)[:100]}...)")
            
            try:
                result = await session.call_tool(tool_name, tool_args)
                output = "".join(c.text for c in result.content if hasattr(c, "text"))
                print(f"       ✅ Result: {output[:150]}...")
                results.append(output)
                last_result = output
            except Exception as e:
                print(f"       ❌ Error: {e}")
                results.append(f"Error: {e}")
                last_result = f"Error: {e}"
        
        return results
