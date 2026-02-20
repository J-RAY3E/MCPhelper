# utils/tool_decorator.py

def tool():
    """
    Decorator to mark a method as a tool.
    Adds a `_is_tool = True` attribute to the method.
    """
    def decorator(func):
        func._is_tool = True
        return func
    return decorator
