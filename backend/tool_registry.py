import os
import sys
import inspect
import functools
from mcp.server.fastmcp import FastMCP

from tools.system_tools import SystemTools
from tools.navigation_tools import NavigationTools
from tools.redaction_tools import RedactionTools
from tools.financial_tools import FinancialTools

def register_tools(mcp: FastMCP, base_path: str):
    """
    Discovers and registers tool methods with the FastMCP server.
    Methods marked with @tool() decorator are auto-discovered.
    """
    system_tools_instance = SystemTools(allowed_base_path=base_path)
    navigation_tools_instance = NavigationTools()
    redaction_tools_instance = RedactionTools()
    financial_tools_instance = FinancialTools()

    tool_instances = {
        "system": system_tools_instance,
        "navigation": navigation_tools_instance,
        "redaction": redaction_tools_instance,
        "financial": financial_tools_instance,
    }

    for category, instance in tool_instances.items():
        for name, method in inspect.getmembers(instance, inspect.ismethod):
            if not hasattr(method, '_is_tool') or not method._is_tool:
                continue
            
            # Create a proper wrapper that preserves async nature
            if inspect.iscoroutinefunction(method):
                @functools.wraps(method)
                async def async_wrapper(*args, _bound_method=method, **kwargs):
                    return await _bound_method(*args, **kwargs)
                mcp.tool()(async_wrapper)
            else:
                @functools.wraps(method)
                def sync_wrapper(*args, _bound_method=method, **kwargs):
                    return _bound_method(*args, **kwargs)
                mcp.tool()(sync_wrapper)
            
            sys.stderr.write(f"  Registered: {name}\n")
    
    return tool_instances
