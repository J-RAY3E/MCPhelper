"""LLM-based Planner implementation."""
from typing import List, Dict, Any

from core.interfaces import BasePlanner
from prompts.planner_prompt import PLANNER_PROMPT


class LLMPlanner(BasePlanner):
    """Uses an LLM to generate execution plans."""
    
    def __init__(self, llm_client):
        """
        Args:
            llm_client: LLMClient instance (supports .chat() method)
        """
        self.llm = llm_client
    
    async def plan(self, user_input: str, tool_descriptions: str) -> str:
        """
        Generate a raw plan string from the LLM.
        Returns the raw output (to be validated by PlanValidator).
        """
        messages = [
            {"role": "system", "content": PLANNER_PROMPT.format(tools=tool_descriptions)},
            {"role": "user", "content": user_input}
        ]
        
        return self.llm.chat(messages, temperature=0.09)
