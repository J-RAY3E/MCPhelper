"""
Abstract base classes for the agent pipeline.
Following Interface Segregation Principle (ISP) - small, focused interfaces.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BasePlanner(ABC):
    """Generates an execution plan from user input."""
    
    @abstractmethod
    async def plan(self, user_input: str, tool_descriptions: str) -> List[Dict[str, Any]]:
        """
        Create an execution plan.
        
        Args:
            user_input: The user's query/task.
            tool_descriptions: Available tools in text format.
            
        Returns:
            List of step dictionaries with 'tool', 'args', 'description'.
        """
        pass


class BasePlanValidator(ABC):
    """Validates and normalizes a raw plan."""
    
    @abstractmethod
    async def validate(self, raw_plan: str) -> List[Dict[str, Any]]:
        """
        Validate and parse a raw plan string.
        
        Args:
            raw_plan: Raw output from planner (may contain markdown, errors).
            
        Returns:
            Parsed list of steps, or empty list if unrecoverable.
        """
        pass


class BaseExecutor(ABC):
    """Executes a validated plan using available tools."""
    
    @abstractmethod
    async def execute(self, plan: List[Dict[str, Any]], session) -> List[str]:
        """
        Execute each step in the plan.
        
        Args:
            plan: List of validated steps.
            session: MCP session for tool calls.
            
        Returns:
            List of results from each step.
        """
        pass


class BaseSummarizer(ABC):
    """Generates a final response from execution results."""
    
    @abstractmethod
    async def summarize(self, task: str, results: List[str]) -> str:
        """
        Create a user-facing summary.
        
        Args:
            task: Original user request.
            results: Outputs from executor.
            
        Returns:
            Final response string.
        """
        pass
